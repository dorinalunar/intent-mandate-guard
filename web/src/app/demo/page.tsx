"use client";

import { PageShell } from "@/components/SiteChrome";
import { withBase } from "@/lib/basePath";

export default function DemoPage() {
  return (
    <PageShell
      active="/demo/"
      title="Demo Walkthrough"
      lead="End-to-end IntentMandateGuard v3.0 execution flow."
    >
      <div className="cta-row">
        <a className="btn btn-primary" href={withBase("/console/")}>
          Launch Live Console
        </a>
        <a className="btn btn-ghost" href={withBase("/quickstart/")}>
          View Quickstart Payloads
        </a>
      </div>
    </PageShell>
  );
}
