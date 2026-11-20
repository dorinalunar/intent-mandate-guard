"use client";

import { PageShell } from "@/components/SiteChrome";

export default function SecurityPage() {
  return (
    <PageShell
      active="/security/"
      title="Security Model"
      lead="How IntentMandateGuard v3.0 prevents prompt injection, replay attacks, address mismatches, and quota leaks."
    >
      <div className="grid-3">
        <article className="card">
          <h3>Address Canonicalization</h3>
          <p>_addr_to_hex normalizes Address objects, decimal integers, and hex strings into lowercase 0x-hex.</p>
        </article>
        <article className="card">
          <h3>Anti-Hallucination Grounding</h3>
          <p>PASS + solid assessments require a verbatim quote verified in canonical or decoded payload JSON.</p>
        </article>
        <article className="card">
          <h3>Replay & Quota Conservation</h3>
          <p>Per-mandate monotonic nonces plus hard _assert_mandate_invariants prevent double-spends.</p>
        </article>
      </div>
    </PageShell>
  );
}
