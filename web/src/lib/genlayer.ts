import { CHAIN_ID, CONTRACT_ADDRESS, RPC_URL } from "./config";

export type Address = `0x${string}`;

function safeJsonStringify(value: unknown): string {
  const seen = new WeakSet<object>();
  return JSON.stringify(value, (_key, val) => {
    if (typeof val === "bigint") return val.toString();
    if (val && typeof val === "object") {
      const rec = val as Record<string, unknown>;
      if (typeof rec.request === "function" || "_readableState" in rec || "pipes" in rec) {
        return undefined;
      }
      if (seen.has(val)) return undefined;
      seen.add(val);
    }
    return val;
  });
}

async function rpcCall<T = unknown>(method: string, params: unknown[]): Promise<T> {
  const res = await fetch(RPC_URL, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: safeJsonStringify({ jsonrpc: "2.0", id: Date.now(), method, params }),
  });
  const text = await res.text();
  let json: { result?: T; error?: { message?: string } };
  try {
    json = JSON.parse(text);
  } catch {
    throw new Error(text || `RPC HTTP ${res.status}`);
  }
  if (json.error) {
    throw new Error(json.error.message || safeJsonStringify(json.error));
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
  const res = await rpcCall<string>("sim_fundAccount", [address, 10000000000000000000]);
  return typeof res === "string" ? res : "";
}

export async function readContract<T = unknown>(method: string, args: unknown[] = []): Promise<T> {
  return rpcCall<T>("gen_call", [
    {
      to: CONTRACT_ADDRESS,
      data: { method, args },
    },
  ]);
}

export async function writeContract(
  from: Address,
  method: string,
  args: unknown[] = [],
): Promise<string> {
  const eth = (
    window as unknown as {
      ethereum?: { request: (a: { method: string; params?: unknown[] }) => Promise<unknown> };
    }
  ).ethereum;
  if (!eth) throw new Error("MetaMask not found");

  const payload = {
    from,
    to: CONTRACT_ADDRESS,
    chainId: `0x${CHAIN_ID.toString(16)}`,
    data: safeJsonStringify({ method, args }),
  };

  try {
    const txHash = await rpcCall<string>("gen_sendTransaction", [
      {
        from,
        to: CONTRACT_ADDRESS,
        method,
        args,
      },
    ]);
    if (typeof txHash === "string" && txHash) return txHash;
  } catch {
    // Fallback to wallet provider when direct studio RPC requires wallet signing
  }

  const hash = await eth.request({
    method: "eth_sendTransaction",
    params: [JSON.parse(safeJsonStringify(payload))],
  });
  return String(hash || "");
}
