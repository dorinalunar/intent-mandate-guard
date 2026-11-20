"use client";

import { PageShell } from "@/components/SiteChrome";
import { withBase } from "@/lib/basePath";

export default function DocsPage() {
  return (
    <PageShell
      active="/docs/"
      title="Documentation"
      lead="Deployment records, milestone hardening notes, and demo walkthroughs."
    >
      <div className="grid-3">
        <a className="card" href={withBase("/docs/STUDIO_DEV_DEPLOY.md")}>
          <h3>STUDIO_DEV_DEPLOY.md</h3>
          <p>Live address, deploy tx, and verified call hashes on chain 61997.</p>
        </a>
        <a className="card" href={withBase("/docs/MILESTONE_V3_HARDENING.md")}>
          <h3>MILESTONE_V3_HARDENING.md</h3>
          <p>Technical breakdown of v3.0 hardening and 60-test verification.</p>
        </a>
        <a className="card" href={withBase("/docs/STUDIO.md")}>
          <h3>STUDIO.md</h3>
          <p>Step-by-step operator guide for GenLayer Studio Dev.</p>
        </a>
      </div>
    </PageShell>
  );
}
