"use client";

import { PageShell } from "@/components/SiteChrome";
import { withBase } from "@/lib/basePath";

export default function ApiReferencePage() {
  return (
    <PageShell
      active="/api-reference/"
      title="API Reference"
      lead="Method signatures and OpenAPI specification for IntentMandateGuard/v3.0."
    >
      <p>
        <a className="btn btn-ghost" href={withBase("/openapi.json")}>
          Download openapi.json
        </a>
      </p>
      <pre className="code">{`register_mandate(operator: Address, executor: Address, rules_json: str, methods_json: str, quota_cap: u256, tx_cap: u256, ttl_seconds: u256) -> u256
issue_ticket(mandate_id: u256, seq_nonce: u256, intent_json: str, weight: u256, ttl_seconds: u256) -> u256
redeem_ticket(ticket_id: u256, intent_json: str) -> dict
record_execution_receipt(ticket_id: u256, calldata_sha256: str, external_tx_ref: str) -> dict
cancel_reservation(ticket_id: u256) -> None
sweep_expired_ticket(ticket_id: u256) -> dict
terminate_mandate(mandate_id: u256) -> None`}</pre>
    </PageShell>
  );
}
