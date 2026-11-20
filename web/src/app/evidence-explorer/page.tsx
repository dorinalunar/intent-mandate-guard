"use client";

import { useEffect, useState } from "react";
import { PageShell } from "@/components/SiteChrome";
import { withBase } from "@/lib/basePath";

export default function EvidenceExplorerPage() {
  const [pack, setPack] = useState<unknown>(null);

  useEffect(() => {
    fetch(withBase("/integrity-pack.json"))
      .then((r) => r.json())
      .then(setPack)
      .catch(() => undefined);
  }, []);

  return (
    <PageShell
      active="/evidence-explorer/"
      title="Integrity & Snapshot Explorer"
      lead="Cryptographic checksums for contracts/IntentMandateGuard.py and Studio Dev deployment."
    >
      <pre className="code">{pack ? JSON.stringify(pack, null, 2) : "Loading integrity-pack.json…"}</pre>
    </PageShell>
  );
}
