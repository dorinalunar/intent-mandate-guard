"use client";

import { useCallback, useEffect, useState } from "react";
import {
  CHAIN_ID,
  CONTRACT_ADDRESS,
  DEFAULT_EXECUTOR,
  DEFAULT_OPERATOR,
  EXPLORER,
  GITHUB,
  RPC_URL,
  STUDIO_URL,
  txUrl,
} from "@/lib/config";
import {
  cancelReservation,
  getExecutionReceipt,
  getProtocolVersion,
  getStats,
  getTicketSchedule,
  issueTicket,
  listMandates,
  listTickets,
  recordExecutionReceipt,
  redeemTicket,
  registerMandate,
  sweepExpiredTicket,
  terminateMandate,
  type ExecutionReceipt,
  type MandateRow,
  type ProtocolStats,
  type TicketRow,
  type TicketSchedule,
} from "@/lib/contracts";
import { fundWithTestGen, getNativeBalance } from "@/lib/genlayer";
import { useWallet } from "./WalletProvider";

function short(addr: string) {
  return addr ? `${addr.slice(0, 6)}…${addr.slice(-4)}` : "—";
}

export function MandateGuardConsole() {
  const { address, provider, connect, error: walletError } = useWallet();
  const [version, setVersion] = useState("IntentMandateGuard/v3.0");
  const [stats, setStats] = useState<ProtocolStats | null>(null);
  const [mandates, setMandates] = useState<MandateRow[]>([]);
  const [tickets, setTickets] = useState<TicketRow[]>([]);
  const [gen, setGen] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState("");
  const [msg, setMsg] = useState("");
  const [tx, setTx] = useState("");

  // Form 1: register_mandate
  const [operatorAddr, setOperatorAddr] = useState<string>(DEFAULT_OPERATOR);
  const [executorAddr, setExecutorAddr] = useState<string>(DEFAULT_EXECUTOR);
  const [rulesJson, setRulesJson] = useState(
    JSON.stringify([
      "Maximum slippage tolerance must not exceed 50 bps.",
      "Only USDC to WETH swaps on approved routers are permitted.",
    ]),
  );
  const [methodsJson, setMethodsJson] = useState(
    JSON.stringify(["exactInputSingle", "multicall"]),
  );
  const [quotaCap, setQuotaCap] = useState("50000");
  const [txCap, setTxCap] = useState("10");
  const [mandateTtl, setMandateTtl] = useState("3600");
  const [targetMandateId, setTargetMandateId] = useState("1");

  // Form 2: issue_ticket
  const [seqNonce, setSeqNonce] = useState("1");
  const [intentJson, setIntentJson] = useState(
    JSON.stringify({
      method: "exactInputSingle",
      target: "uniswap-v3-router.eth",
      payload: JSON.stringify({
        tokenIn: "USDC",
        tokenOut: "WETH",
        amount: 2500,
        maxSlippageBps: 25,
      }),
    }),
  );
  const [weight, setWeight] = useState("2500");
  const [ticketTtl, setTicketTtl] = useState("600");

  // Form 3 & 4: redeem_ticket, record_execution_receipt, sweep_expired_ticket
  const [targetTicketId, setTargetTicketId] = useState("1");
  const [calldataSha256, setCalldataSha256] = useState(
    "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
  );
  const [externalTxRef, setExternalTxRef] = useState(
    "0x62048c591d8e3814b006bfbe813a9f0a69c2d6833943c56f881d8b814967886d",
  );
  const [scheduleInfo, setScheduleInfo] = useState<TicketSchedule | null>(null);
  const [receiptInfo, setReceiptInfo] = useState<ExecutionReceipt | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [ver, st, mPage, tPage] = await Promise.all([
        getProtocolVersion(),
        getStats(),
        listMandates(0, 20),
        listTickets(0, 20),
      ]);
      setVersion(ver);
      setStats(st);
      setMandates([...mPage.items].reverse());
      setTickets([...tPage.items].reverse());
      if (address) {
        const bal = await getNativeBalance(address);
        setGen(bal);
      }
      const tid = Number(targetTicketId);
      if (tid > 0) {
        try {
          const [sc, rc] = await Promise.all([
            getTicketSchedule(tid),
            getExecutionReceipt(tid),
          ]);
          setScheduleInfo(sc);
          setReceiptInfo(rc);
        } catch {
          setScheduleInfo(null);
          setReceiptInfo(null);
        }
      }
      setMsg("");
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "On-chain read failed");
    } finally {
      setLoading(false);
    }
  }, [address, targetTicketId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const run = async (label: string, fn: () => Promise<string | void>) => {
    if (!address || !provider) {
      setMsg("Connect MetaMask on chain 61997 first");
      return;
    }
    setBusy(label);
    setMsg("");
    try {
      const hash = await fn();
      if (hash) setTx(hash);
      setMsg(`${label} OK`);
      await refresh();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy("");
    }
  };

  const acct = address as `0x${string}`;
  const disabled = !!busy || !address;
  const selectedTicket = tickets.find((t) => t.id === Number(targetTicketId));

  return (
    <div className="console">
      <header className="console-header">
        <h1>IntentMandateGuard Console ({version})</h1>
        <p className="muted">
          Live GenLayer Studio Dev (chain {CHAIN_ID}) reads and writes — semantic mandates,
          verbatim-grounded AI audit tickets, deadline-split sweeps, and execution receipts.
        </p>
        <p className="muted">
          Contract{" "}
          <a href={EXPLORER} target="_blank" rel="noreferrer">
            <code>{CONTRACT_ADDRESS}</code>
          </a>{" "}
          · RPC <code>{RPC_URL}</code>
        </p>
        <div className="row">
          {address ? (
            <span className="pill">{short(address)} · connected</span>
          ) : (
            <button type="button" className="btn btn-primary" onClick={() => void connect()}>
              Connect MetaMask
            </button>
          )}
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => void refresh()}
            disabled={loading}
          >
            {loading ? "Loading…" : "Refresh on-chain"}
          </button>
          <a className="btn btn-ghost" href={EXPLORER} target="_blank" rel="noreferrer">
            Explorer
          </a>
          <a className="btn btn-ghost" href={STUDIO_URL} target="_blank" rel="noreferrer">
            Studio Dev
          </a>
          <a className="btn btn-ghost" href={GITHUB} target="_blank" rel="noreferrer">
            GitHub
          </a>
        </div>
        {(msg || walletError) && (
          <p className={msg.endsWith("OK") ? "ok" : "err"}>{msg || walletError}</p>
        )}
        {tx && (
          <p className="muted">
            last tx{" "}
            <a href={txUrl(tx)} target="_blank" rel="noreferrer">
              <code>{tx}</code>
            </a>
          </p>
        )}
        {busy && <p className="muted">Waiting for consensus: {busy}…</p>}
      </header>

      <section className="card">
        <h2>On-chain protocol state</h2>
        {address && (
          <p className="muted">
            Wallet balance: <code>{gen || "—"}</code> GEN{" "}
            <button
              type="button"
              className="btn btn-ghost"
              disabled={disabled}
              onClick={() => void run("faucet", () => fundWithTestGen(acct))}
            >
              Get test GEN
            </button>
          </p>
        )}
        <pre>{stats ? JSON.stringify(stats, null, 2) : "—"}</pre>

        <h3>Registered Mandates ({mandates.length})</h3>
        <ul>
          {mandates.length === 0 && <li className="muted">No mandates registered yet</li>}
          {mandates.map((m) => (
            <li key={m.id} style={{ marginBottom: "0.5rem" }}>
              <button
                type="button"
                className="btn btn-ghost"
                style={{ padding: "0.3rem 0.7rem", fontSize: "0.8rem" }}
                onClick={() => setTargetMandateId(String(m.id))}
              >
                Mandate #{m.id}
              </button>{" "}
              <strong>{m.terminated ? "TERMINATED" : "ACTIVE"}</strong> · quota{" "}
              <code>
                {m.used_quota} used / {m.locked_quota} locked / {m.quota_cap} cap
              </code>{" "}
              · txs{" "}
              <code>
                {m.used_txs}/{m.tx_cap}
              </code>{" "}
              · operator {short(m.operator)} · executor {short(m.executor)}
            </li>
          ))}
        </ul>

        <h3>Issued Intent Tickets ({tickets.length})</h3>
        <ul>
          {tickets.length === 0 && <li className="muted">No tickets issued yet</li>}
          {tickets.map((t) => (
            <li key={t.id} style={{ marginBottom: "0.5rem" }}>
              <button
                type="button"
                className="btn btn-ghost"
                style={{ padding: "0.3rem 0.7rem", fontSize: "0.8rem" }}
                onClick={() => {
                  setTargetTicketId(String(t.id));
                  setIntentJson(t.canonical_intent_json);
                }}
              >
                Ticket #{t.id}
              </button>{" "}
              <strong>{t.state}</strong> · mandate #{t.mandate_id} · nonce {t.seq_nonce} ·
              weight <code>{t.weight}</code> · method <code>{t.intent.method}</code> · proof{" "}
              <code>{t.proof_hash.slice(0, 12)}…</code>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2>1 · Principal: register_mandate</h2>
        <label>
          operator (0x address)
          <input value={operatorAddr} onChange={(e) => setOperatorAddr(e.target.value)} />
        </label>
        <label>
          executor (0x address)
          <input value={executorAddr} onChange={(e) => setExecutorAddr(e.target.value)} />
        </label>
        <label>
          rules_json (1 to 6 semantic constraints)
          <input value={rulesJson} onChange={(e) => setRulesJson(e.target.value)} />
        </label>
        <label>
          methods_json (JSON array of allowed methods)
          <input value={methodsJson} onChange={(e) => setMethodsJson(e.target.value)} />
        </label>
        <div className="row">
          <label style={{ flex: 1 }}>
            quota_cap
            <input value={quotaCap} onChange={(e) => setQuotaCap(e.target.value)} />
          </label>
          <label style={{ flex: 1 }}>
            tx_cap
            <input value={txCap} onChange={(e) => setTxCap(e.target.value)} />
          </label>
          <label style={{ flex: 1 }}>
            ttl_seconds (60 – 2592000)
            <input value={mandateTtl} onChange={(e) => setMandateTtl(e.target.value)} />
          </label>
        </div>
        <div className="row">
          <button
            type="button"
            className="btn btn-primary"
            disabled={disabled}
            onClick={() =>
              void run("register_mandate", () =>
                registerMandate(
                  acct,
                  provider,
                  operatorAddr,
                  executorAddr,
                  rulesJson,
                  methodsJson,
                  Number(quotaCap),
                  Number(txCap),
                  Number(mandateTtl),
                ),
              )
            }
          >
            register_mandate
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            disabled={disabled}
            onClick={() =>
              void run("terminate_mandate", () =>
                terminateMandate(acct, provider, Number(targetMandateId)),
              )
            }
          >
            terminate_mandate #{targetMandateId}
          </button>
        </div>
      </section>

      <section className="card">
        <h2>2 · Operator: issue_ticket (AI Consensus + Verbatim Quote Grounding)</h2>
        <div className="row">
          <label style={{ flex: 1 }}>
            mandate_id
            <input value={targetMandateId} onChange={(e) => setTargetMandateId(e.target.value)} />
          </label>
          <label style={{ flex: 1 }}>
            seq_nonce
            <input value={seqNonce} onChange={(e) => setSeqNonce(e.target.value)} />
          </label>
          <label style={{ flex: 1 }}>
            weight
            <input value={weight} onChange={(e) => setWeight(e.target.value)} />
          </label>
          <label style={{ flex: 1 }}>
            ttl_seconds (30 – 86400)
            <input value={ticketTtl} onChange={(e) => setTicketTtl(e.target.value)} />
          </label>
        </div>
        <label>
          intent_json (method, target, payload)
          <input value={intentJson} onChange={(e) => setIntentJson(e.target.value)} />
        </label>
        <div className="row">
          <button
            type="button"
            className="btn btn-primary"
            disabled={disabled}
            onClick={() =>
              void run("issue_ticket", () =>
                issueTicket(
                  acct,
                  provider,
                  Number(targetMandateId),
                  Number(seqNonce),
                  intentJson,
                  Number(weight),
                  Number(ticketTtl),
                ),
              )
            }
          >
            issue_ticket (LLM audit + lock quota)
          </button>
        </div>
      </section>

      <section className="card">
        <h2>3 · Executor: redeem_ticket & record_execution_receipt</h2>
        <label>
          ticket_id
          <input value={targetTicketId} onChange={(e) => setTargetTicketId(e.target.value)} />
        </label>
        {scheduleInfo && (
          <p className="muted">
            Schedule: state <strong>{scheduleInfo.state}</strong> · can_redeem=
            <code>{String(scheduleInfo.can_redeem)}</code> · can_sweep=
            <code>{String(scheduleInfo.can_sweep)}</code> · expires_at=
            <code>{scheduleInfo.expires_at}</code>
          </p>
        )}
        <div className="row">
          <button
            type="button"
            className="btn btn-primary"
            disabled={disabled || (selectedTicket && selectedTicket.state !== "ACTIVE")}
            onClick={() =>
              void run("redeem_ticket", () =>
                redeemTicket(acct, provider, Number(targetTicketId), intentJson),
              )
            }
          >
            redeem_ticket #{targetTicketId}
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            disabled={disabled}
            onClick={() =>
              void run("cancel_reservation", () =>
                cancelReservation(acct, provider, Number(targetTicketId)),
              )
            }
          >
            cancel_reservation
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            disabled={disabled}
            onClick={() =>
              void run("sweep_expired_ticket", () =>
                sweepExpiredTicket(acct, provider, Number(targetTicketId)),
              )
            }
          >
            sweep_expired_ticket (post-deadline cleanup)
          </button>
        </div>

        <label>
          calldata_sha256 (64 hex chars)
          <input value={calldataSha256} onChange={(e) => setCalldataSha256(e.target.value)} />
        </label>
        <label>
          external_tx_ref (downstream execution hash)
          <input value={externalTxRef} onChange={(e) => setExternalTxRef(e.target.value)} />
        </label>
        <div className="row">
          <button
            type="button"
            className="btn btn-primary"
            disabled={disabled}
            onClick={() =>
              void run("record_execution_receipt", () =>
                recordExecutionReceipt(
                  acct,
                  provider,
                  Number(targetTicketId),
                  calldataSha256,
                  externalTxRef,
                ),
              )
            }
          >
            record_execution_receipt
          </button>
        </div>
        {receiptInfo && (
          <pre>{JSON.stringify(receiptInfo, null, 2)}</pre>
        )}
      </section>
    </div>
  );
}
