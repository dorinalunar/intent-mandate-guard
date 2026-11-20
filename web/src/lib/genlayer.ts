import { createClient } from "genlayer-js";
import { studioDevnet } from "genlayer-js/chains";
import type { CalldataEncodable } from "genlayer-js/types";
import { TransactionStatus } from "genlayer-js/types";
import { CONTRACT_ADDRESS, EXPLORER_BASE, RPC_URL } from "./config";

export type Address = `0x${string}`;

export type EthereumProvider = NonNullable<Parameters<typeof createClient>[0]>["provider"];

export const studioNext = {
  ...studioDevnet,
  rpcUrls: { default: { http: [RPC_URL] } },
  blockExplorers: { default: { name: "Studio Dev Explorer", url: EXPLORER_BASE } },
} as typeof studioDevnet;

export function getReadClient() {
  return createClient({ chain: studioNext });
}

export function getWriteClient(account: Address, provider: EthereumProvider) {
  return createClient({ chain: studioNext, account, provider });
}

export function parseJson<T>(raw: string, fallback: T): T {
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

async function rpc<T>(method: string, params: unknown[]): Promise<T> {
  const res = await fetch(RPC_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
  });
  const body = (await res.json()) as { result?: T; error?: { message?: string } };
  if (body.error) throw new Error(body.error.message || `${method} failed`);
  return body.result as T;
}

export async function fundWithTestGen(address: Address, gen = 100): Promise<void> {
  await rpc("sim_fundAccount", [address, gen * 1e18]);
}

export async function getNativeBalance(address: Address): Promise<string> {
  try {
    const wei = BigInt(await rpc<string>("eth_getBalance", [address, "latest"]));
    return (wei / 1000000000000000000n).toString();
  } catch {
    return "0";
  }
}

export async function readContract<T = unknown>(
  method: string,
  args: CalldataEncodable[] = [],
): Promise<T> {
  const client = getReadClient();
  return client.readContract({
    address: CONTRACT_ADDRESS as Address,
    functionName: method,
    args,
  }) as Promise<T>;
}

export async function writeAndWait(
  account: Address,
  provider: unknown,
  functionName: string,
  args: CalldataEncodable[] = [],
  value: bigint = BigInt(0),
): Promise<string> {
  const client = getWriteClient(account, provider as EthereumProvider);
  const fees = await client.estimateTransactionFees({});
  const hash = await client.writeContract({
    address: CONTRACT_ADDRESS as Address,
    functionName,
    args,
    value,
    fees,
  });
  await client.waitForTransactionReceipt({
    hash,
    status: TransactionStatus.ACCEPTED,
    retries: 200,
    interval: 3000,
  });
  return hash;
}
