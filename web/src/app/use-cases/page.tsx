"use client";

import { PageShell } from "@/components/SiteChrome";

export default function UseCasesPage() {
  return (
    <PageShell
      active="/features/"
      title="Use Cases"
      lead="Bounded autonomous execution with semantic guardrails."
    >
      <div className="grid-3">
        <article className="card">
          <h3>DeFi Treasury Agents</h3>
          <p>Cap slippage, restrict token pairs, and enforce per-epoch spending budgets.</p>
        </article>
        <article className="card">
          <h3>Multi-Agent Delegation</h3>
          <p>Separate principal policy authority, operator intent proposal, and executor settlement.</p>
        </article>
        <article className="card">
          <h3>Auditable Off-Chain Actions</h3>
          <p>Bind off-chain API or cross-chain calls to on-chain execution receipts.</p>
        </article>
      </div>
    </PageShell>
  );
}
