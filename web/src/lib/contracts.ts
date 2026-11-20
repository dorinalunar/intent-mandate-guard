import { readContract, writeContract, type Address } from "./genlayer";

export type ProtocolStats = Record<string, unknown>;
export type MandateRow = Record<string, any>;
export type TicketRow = Record<string, any>;
export type TicketSchedule = Record<string, any>;
export type ExecutionReceipt = Record<string, any>;

export async function getProtocolVersion(): Promise<string> {
  try {
    const res = await readContract<string>("get_protocol_version");
    return res || "IntentMandateGuard/v3.0";
  } catch {
    return "IntentMandateGuard/v3.0";
  }
}

export async function getStats(): Promise<ProtocolStats> {
  try {
    return await readContract<ProtocolStats>("get_stats");
  } catch {
    return { protocol: "IntentMandateGuard/v3.0", status: "connected" };
  }
}

export async function listMandates(offset = 0, limit = 20): Promise<{ items: MandateRow[] }> {
  try {
    const res = await readContract<{ items?: MandateRow[] } | MandateRow[]>("list_mandates", [offset, limit]);
    if (Array.isArray(res)) return { items: res };
    return { items: res?.items ?? [] };
  } catch {
    return { items: [] };
  }
}

export async function listTickets(offset = 0, limit = 20): Promise<{ items: TicketRow[] }> {
  try {
    const res = await readContract<{ items?: TicketRow[] } | TicketRow[]>("list_tickets", [offset, limit]);
    if (Array.isArray(res)) return { items: res };
    return { items: res?.items ?? [] };
  } catch {
    return { items: [] };
  }
}

export async function getTicketSchedule(ticketId: number): Promise<TicketSchedule> {
  return readContract<TicketSchedule>("get_ticket_schedule", [ticketId]);
}

export async function getExecutionReceipt(ticketId: number): Promise<ExecutionReceipt> {
  return readContract<ExecutionReceipt>("get_execution_receipt", [ticketId]);
}

function isProviderLike(val: unknown): boolean {
  if (!val || typeof val !== "object") return false;
  const obj = val as Record<string, unknown>;
  return typeof obj.request === "function" || "_readableState" in obj || "pipes" in obj;
}

function sanitizeValue(val: unknown, seen = new WeakSet<object>()): unknown {
  if (val === null || val === undefined) return val;
  if (typeof val === "bigint") return val.toString();
  if (typeof val !== "object") return val;
  if (isProviderLike(val)) return undefined;
  if (seen.has(val as object)) return undefined;
  seen.add(val as object);

  if (Array.isArray(val)) {
    return val.map((item) => sanitizeValue(item, seen)).filter((item) => item !== undefined);
  }

  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(val as Record<string, unknown>)) {
    if (k.startsWith("_") || k === "pipes" || typeof v === "function") continue;
    const clean = sanitizeValue(v, seen);
    if (clean !== undefined) out[k] = clean;
  }
  return out;
}

function extractCall(args: unknown[]): { from: Address; rest: unknown[] } {
  const filtered = args.filter((a) => !isProviderLike(a));
  const [from, ...rest] = filtered;
  const cleanRest = (sanitizeValue(rest) as unknown[]) ?? [];
  return {
    from: String(from || "") as Address,
    rest: cleanRest,
  };
}

export async function registerMandate(...args: unknown[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "register_mandate", rest);
}

export async function issueTicket(...args: unknown[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "issue_ticket", rest);
}

export async function redeemTicket(...args: unknown[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "redeem_ticket", rest);
}

export async function recordExecutionReceipt(...args: unknown[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "record_execution_receipt", rest);
}

export async function sweepExpiredTicket(...args: unknown[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "sweep_expired_ticket", rest);
}

export async function cancelReservation(...args: unknown[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "cancel_reservation", rest);
}

export async function terminateMandate(...args: unknown[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "terminate_mandate", rest);
}
