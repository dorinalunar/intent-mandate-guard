"use client";

import { PageShell } from "@/components/SiteChrome";

const STEPS = [
  { actor: "Principal", action: "register_mandate(operator, executor, rules, methods, caps, ttl)", note: "Commits bounded policy & normalized 0x roles" },
  { actor: "Operator", action: "issue_ticket(mandate_id, seq_nonce, intent_json, weight, ttl)", note: "Locks quota & triggers LLM consensus audit" },
  { actor: "Validators", action: "evaluate_rules_nondet + quote_grounded_in_source", note: "Verifies PASS + solid + verbatim quote" },
  { actor: "Executor", action: "redeem_ticket(ticket_id, intent_json)", note: "Matches cryptographic proof_hash anchor before expiry" },
  { actor: "Executor", action: "record_execution_receipt(ticket_id, calldata_sha256, tx_ref)", note: "Anchors downstream execution receipt on-chain" },
  { actor: "Anyone", action: "sweep_expired_ticket(ticket_id)", note: "Permissionless cleanup after expires_at or termination" },
];

export default function HowItWorksPage() {
  return (
    <PageShell
      active="/how-it-works/"
      title="How it works"
      lead="IntentMandateGuard v3.0 separates semantic policy authorization from downstream execution via single-use cryptographic intent tickets."
    >
      <div className="seq">
        {STEPS.map((s, i) => (
          <div className="seq-row" key={s.action}>
            <div className="seq-n">{String(i + 1).padStart(2, "0")}</div>
            <div className="seq-actor">{s.actor}</div>
            <div className="seq-body">
              <code>{s.action}</code>
              <span>{s.note}</span>
            </div>
          </div>
        ))}
      </div>
    </PageShell>
  );
}
