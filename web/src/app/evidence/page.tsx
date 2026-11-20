"use client";

import { PageShell } from "@/components/SiteChrome";
import { withBase } from "@/lib/basePath";

export default function EvidenceRedirectPage() {
  return (
    <PageShell
      active="/evidence-explorer/"
      title="Integrity & Attestations"
      lead="Inspect CODE_SNAPSHOT.json and ticket attestation schemas."
    >
      <a className="btn btn-primary" href={withBase("/evidence-explorer/")}>
        Open Integrity Explorer
      </a>
    </PageShell>
  );
}
