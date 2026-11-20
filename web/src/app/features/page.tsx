"use client";

import { PageShell } from "@/components/SiteChrome";

const ROWS = [
  ["register_mandate", "write", "Register semantic rules, allowed methods, quota_cap, tx_cap, and TTL"],
  ["issue_ticket", "write", "Audit intent with LLM validators + verbatim quote grounding; lock quota"],
  ["redeem_ticket", "write", "Executor redeems ACTIVE ticket before deadline against proof_hash anchor"],
  ["record_execution_receipt", "write", "Store downstream calldata SHA-256 and external transaction hash"],
  ["cancel_reservation", "write", "Principal/operator releases locked quota before expiry"],
  ["sweep_expired_ticket", "write", "Permissionless cleanup of expired or terminated ACTIVE tickets"],
  ["terminate_mandate", "write", "Principal permanently terminates mandate"],
  ["get_ticket_schedule", "view", "Check can_redeem vs can_sweep deadline split"],
  ["get_audit_round", "view", "Inspect per-rule AI assessments, quotes, and grounded flags"],
  ["list_mandates / list_tickets", "view", "Paginated on-chain views (max limit 100)"],
];

export default function FeaturesPage() {
  return (
    <PageShell
      active="/features/"
      title="Features & Contract Surface"
      lead="All write and view capabilities of IntentMandateGuard/v3.0."
    >
      <div className="table-wrap">
        <table className="api-table">
          <thead>
            <tr>
              <th>Method</th>
              <th>Kind</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {ROWS.map(([m, k, d]) => (
              <tr key={m}>
                <td><code>{m}</code></td>
                <td>{k}</td>
                <td>{d}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageShell>
  );
}
