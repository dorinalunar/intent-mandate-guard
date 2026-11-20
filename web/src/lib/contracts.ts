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

function extractCall(args: any[]): { from: Address; rest: unknown[] } {
  if (args.length > 1 && typeof args[0] === "object" && args[0] !== null && typeof args[1] === "string") {
    const [, from, ...rest] = args;
    return { from: from as Address, rest };
  }
  const [from, ...rest] = args;
  return { from: from as Address, rest };
}

export async function registerMandate(...args: any[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "register_mandate", rest);
}

export async function issueTicket(...args: any[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "issue_ticket", rest);
}

export async function redeemTicket(...args: any[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "redeem_ticket", rest);
}

export async function recordExecutionReceipt(...args: any[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "record_execution_receipt", rest);
}

export async function sweepExpiredTicket(...args: any[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "sweep_expired_ticket", rest);
}

export async function cancelReservation(...args: any[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "cancel_reservation", rest);
}

export async function terminateMandate(...args: any[]): Promise<string> {
  const { from, rest } = extractCall(args);
  return writeContract(from, "terminate_mandate", rest);
}
