import { CONTRACT_ADDRESS, RPC_URL } from "./config";

export type Address = `0x${string}`;

async function rpcCall<T = unknown>(method: string, params: unknown[]): Promise<T> {
  const res = await fetch(RPC_URL, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: Date.now(), method, params }),
  });
  const json = await res.json();
  if (json.error) {
    throw new Error(json.error.message || JSON.stringify(json.error));
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
  const res = await rpcCall<string>("sim_fundAccount", [address, 100]);
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
  const eth = (window as unknown as { ethereum?: { request: (a: { method: string; params?: unknown[] }) => Promise<unknown> } }).ethereum;
  if (!eth) throw new Error("MetaMask not found");
  const hash = await eth.request({
    method: "eth_sendTransaction",
    params: [
      {
        from,
        to: CONTRACT_ADDRESS,
        data: JSON.stringify({ method, args }),
      },
    ],
  });
  return String(hash || "");
}
