"use client";

import { useState } from "react";
import { PageShell } from "@/components/SiteChrome";
import { CALL_TX_1, CALL_TX_2, CONTRACT_ADDRESS, DEPLOY_TX, EXPLORER, GITHUB, txUrl } from "@/lib/config";

const FIELDS = [
  { label: "Project Name", value: "IntentMandateGuard v3.0" },
  { label: "Contract Address", value: CONTRACT_ADDRESS },
  { label: "Explorer Link", value: EXPLORER },
  { label: "Deploy Tx", value: txUrl(DEPLOY_TX) },
  { label: "Call Tx 1 (register_mandate)", value: txUrl(CALL_TX_1) },
  { label: "Call Tx 2 (issue_ticket)", value: txUrl(CALL_TX_2) },
  { label: "GitHub Repository", value: GITHUB },
];

export default function SubmitPage() {
  const [copied, setCopied] = useState("");
  async function copy(label: string, val: string) {
    await navigator.clipboard.writeText(val);
    setCopied(label);
  }
  return (
    <PageShell
      active="/submit/"
      title="Milestone Submission Kit"
      lead="Copy verified v3.0 deployment addresses and transaction hashes."
    >
      {copied && <p className="status-line ok">Copied: {copied}</p>}
      <div style={{ display: "grid", gap: "0.75rem" }}>
        {FIELDS.map((f) => (
          <div className="card" key={f.label}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <strong>{f.label}</strong>
              <button className="btn btn-ghost" type="button" onClick={() => void copy(f.label, f.value)}>
                Copy
              </button>
            </div>
            <pre className="code" style={{ marginTop: "0.5rem" }}>{f.value}</pre>
          </div>
        ))}
      </div>
    </PageShell>
  );
}
