"use client";

import { PageShell } from "@/components/SiteChrome";
import { withBase } from "@/lib/basePath";

export default function ChangelogPage() {
  return (
    <PageShell
      active="/docs/"
      title="Changelog"
      lead="Release history for IntentMandateGuard."
    >
      <a className="btn btn-ghost" href={withBase("/docs/CHANGELOG.md")}>
        Open CHANGELOG.md
      </a>
    </PageShell>
  );
}
