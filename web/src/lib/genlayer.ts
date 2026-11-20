import { createClient } from "genlayer-js";
import type { CalldataEncodable } from "genlayer-js/types";
import { CONTRACT_ADDRESS, RPC_URL } from "./config";

export type Address = `0x${string}`;

export function formatError(err: unknown): string {
  if (typeof err === "string") return err;
  if (!err || typeof err !== "object") return String(err);
  const rec = err as Record<string, unknown>;
  if (typeof rec.message === "string" && rec.message) return rec.message;
  if (rec.data && typeof rec.data === "object") {
    const d = rec.data as Record<string, unknown>;
    if (typeof d.message === "string" && d.message) return d.message;
  }
  if (rec.cause && typeof rec.cause === "object") {
    const c = rec.cause as Record<string, unknown>;
    if (typeof c.message === "string" && c.message) return c.message;
  }
  try {
    const seen = new WeakSet<object>();
    const s = JSON.stringify(
      err,
      (_k, v) => {
        if (typeof v === "bigint") return v.toString();
        if (v && typeof v === "object") {
          const o = v as Record<string, unknown>;
          if (typeof o.request === "function" || "_readableState" in o || "pipes" in o) {
            return "[StreamOrProvider]";
          }
          if (seen.has(v)) return "[Circular]";
          seen.add(v);
        }
        return v;
      },
      2,
    );
    return s || "Unknown error";
  } catch {
    return "Unserializable error object";
  }
}

function getClient(account?: Address) {
  return createClient({
    endpoint: RPC_URL,
    ...(account ? { account } : {}),
  });
}

function toCalldataArgs(args: unknown[]): CalldataEncodable[] {
  return args as unknown as CalldataEncodable[];
}

async function rpcCall<T = unknown>(method: string, params: unknown[]): Promise<T> {
  const res = await fetch(RPC_URL, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: Date.now(), method, params }),
  });
  const text = await res.text();
  let json: { result?: T; error?: unknown };
  try {
    json = JSON.parse(text);
  } catch {
    throw new Error(text || `RPC HTTP ${res.status}`);
  }
  if (json.error) {
    throw new Error(formatError(json.error));
  }
  return json.result as T;
}

export async function getNativeBalance(address: string): Promise<string> {
  try {
    const hex = await rpcCall<string>("eth_getBalance", [address, "latest"]);
    const wei = BigInt(hex || "0x0");
    return (Number(wei) / 1e18).toFixed(4);
  } catch {
    return "0.0000";
  }
}

export async function fundWithTestGen(address: Address): Promise<string> {
  try {
    const res = await rpcCall<string>("sim_fundAccount", [address, 10000000000000000000]);
    return typeof res === "string" ? res : "";
  } catch (e) {
    throw new Error(formatError(e));
  }
}

export async function readContract<T = unknown>(method: string, args: unknown[] = []): Promise<T> {
  try {
    const client = getClient();
    const res = await client.readContract({
      address: CONTRACT_ADDRESS as Address,
      functionName: method,
      args: toCalldataArgs(args),
    });
    return res as T;
  } catch {
    return rpcCall<T>("gen_call", [
      {
        to: CONTRACT_ADDRESS,
        data: { method, args },
      },
    ]);
  }
}

export async function writeContract(
  from: Address,
  method: string,
  args: unknown[] = [],
): Promise<string> {
  try {
    const client = getClient(from);
    const txHash = await client.writeContract({
      address: CONTRACT_ADDRESS as Address,
      functionName: method,
      args: toCalldataArgs(args),
      value: BigInt(0),
    });
    return String(txHash || "");
  } catch (e) {
    throw new Error(formatError(e));
  }
}
