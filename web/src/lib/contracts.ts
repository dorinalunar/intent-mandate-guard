import type { CalldataEncodable } from "genlayer-js/types";
import { parseJson, readContract, writeAndWait, type Address } from "./genlayer";

export type ProtocolStats = Record<string, unknown>;
export type MandateRow = Record<string, any>;
export type TicketRow = Record<string, any>;
export type TicketSchedule = Record<string, any>;
export type ExecutionReceipt = Record<string, any>;

export async function getProtocolVersion(): Promise<string> {
  try {
    const res = await readContract<string>("protocol_version", []);
    if (typeof res === "string" && res) return res;
    return "IntentMandateGuard/v3.0";
  } catch {
    return "IntentMandateGuard/v3.0";
  }
}

export async function getStats(): Promise<ProtocolStats> {
  try {
    const raw = await readContract<string | ProtocolStats>("get_stats", []);
    if (typeof raw === "string") return parseJson<ProtocolStats>(raw, { protocol: "IntentMandateGuard/v3.0", status: "connected" });
    return raw ?? { protocol: "IntentMandateGuard/v3.0", status: "connected" };
  } catch {
    return { protocol: "IntentMandateGuard/v3.0", status: "connected" };
  }
}

export async function listMandates(offset = 0, limit = 20): Promise<{ items: MandateRow[] }> {
  try {
    const raw = await readContract<string | { items?: MandateRow[] } | MandateRow[]>(
      "list_mandates",
      [offset, limit],
    );
    const parsed = typeof raw === "string" ? parseJson<{ items?: MandateRow[] } | MandateRow[]>(raw, { items: [] }) : raw;
    if (Array.isArray(parsed)) return { items: parsed };
    return { items: parsed?.items ?? [] };
  } catch {
    return { items: [] };
  }
}

export async function listTickets(offset = 0, limit = 20): Promise<{ items: TicketRow[] }> {
  try {
    const raw = await readContract<string | { items?: TicketRow[] } | TicketRow[]>(
      "list_tickets",
      [offset, limit],
    );
    const parsed = typeof raw === "string" ? parseJson<{ items?: TicketRow[] } | TicketRow[]>(raw, { items: [] }) : raw;
    if (Array.isArray(parsed)) return { items: parsed };
    return { items: parsed?.items ?? [] };
  } catch {
    return { items: [] };
  }
}

export async function getTicketSchedule(ticketId: number): Promise<TicketSchedule> {
  const raw = await readContract<string | TicketSchedule>("get_ticket_schedule", [ticketId]);
  return typeof raw === "string" ? parseJson<TicketSchedule>(raw, {}) : (raw ?? {});
}

export async function getExecutionReceipt(ticketId: number): Promise<ExecutionReceipt> {
  const raw = await readContract<string | ExecutionReceipt>("get_execution_receipt", [ticketId]);
  return typeof raw === "string" ? parseJson<ExecutionReceipt>(raw, {}) : (raw ?? {});
}

export async function registerMandate(
  account: Address,
  provider: unknown,
  operatorAddr: string,
  executorAddr: string,
  rulesJson: string,
  methodsJson: string,
  quotaCap: number,
  txCap: number,
  mandateTtl: number,
): Promise<string> {
  return writeAndWait(account, provider, "register_mandate", [
    operatorAddr,
    executorAddr,
    rulesJson,
    methodsJson,
    quotaCap,
    txCap,
    mandateTtl,
  ] as CalldataEncodable[]);
}

export async function issueTicket(
  account: Address,
  provider: unknown,
  mandateId: number,
  seqNonce: number,
  intentJson: string,
  weight: number,
  ticketTtl: number,
): Promise<string> {
  return writeAndWait(account, provider, "issue_ticket", [
    mandateId,
    seqNonce,
    intentJson,
    weight,
    ticketTtl,
  ] as CalldataEncodable[]);
}

export async function redeemTicket(
  account: Address,
  provider: unknown,
  ticketId: number,
  intentJson: string,
): Promise<string> {
  return writeAndWait(account, provider, "redeem_ticket", [
    ticketId,
    intentJson,
  ] as CalldataEncodable[]);
}

export async function recordExecutionReceipt(
  account: Address,
  provider: unknown,
  ticketId: number,
  calldataSha256: string,
  externalTxRef: string,
): Promise<string> {
  return writeAndWait(account, provider, "record_execution_receipt", [
    ticketId,
    calldataSha256,
    externalTxRef,
  ] as CalldataEncodable[]);
}

export async function cancelReservation(
  account: Address,
  provider: unknown,
  ticketId: number,
): Promise<string> {
  return writeAndWait(account, provider, "cancel_reservation", [ticketId] as CalldataEncodable[]);
}

export async function sweepExpiredTicket(
  account: Address,
  provider: unknown,
  ticketId: number,
): Promise<string> {
  return writeAndWait(account, provider, "sweep_expired_ticket", [ticketId] as CalldataEncodable[]);
}

export async function terminateMandate(
  account: Address,
  provider: unknown,
  mandateId: number,
): Promise<string> {
  return writeAndWait(account, provider, "terminate_mandate", [mandateId] as CalldataEncodable[]);
}
