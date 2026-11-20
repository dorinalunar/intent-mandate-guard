"use client";

import { useState } from "react";
import { withBase } from "@/lib/basePath";
import { CONTRACT_ADDRESS, EXPLORER, GITHUB, STUDIO_URL } from "@/lib/config";

export default function HomePage() {
  const [packStatus, setPackStatus] = useState("");

  async function downloadIntegrityPack() {
    setPackStatus("Building…");
    try {
      const res = await fetch(withBase("/integrity-pack.json"));
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "intentmandateguard-v3-integrity-pack.json";
      a.click();
      URL.revokeObjectURL(url);
      setPackStatus(`Pack ready · sha256 ${data.files?.["contracts/IntentMandateGuard.py"]?.sha256?.slice(0, 10)}…`);
    } catch (e) {
      setPackStatus(`Failed: ${e instanceof Error ? e.message : "error"}`);
    }
  }

  return (
    <>
      <header className="wrap nav">
        <div className="brand">
          <img src={withBase("/logo.svg")} alt="IntentMandateGuard" />
          IntentMandateGuard v3.0
        </div>
        <nav className="nav-links">
          <a href={withBase("/console/")}>Console</a>
          <a href={withBase("/how-it-works/")}>How it works</a>
          <a href={withBase("/quickstart/")}>Quickstart</a>
          <a href={withBase("/evidence-explorer/")}>Integrity</a>
          <a href={withBase("/features/")}>Features</a>
          <a href={withBase("/api-reference/")}>API</a>
          <a href={withBase("/docs/")}>Docs</a>
          <a className="btn btn-ghost" href={GITHUB} target="_blank" rel="noreferrer">
            GitHub
          </a>
        </nav>
      </header>

      <main>
        <section className="wrap hero">
          <div className="hero-copy">
            <h1>
              Bound the mandate.
              <br />
              <span>Verify the intent.</span>
            </h1>
            <p>
              Semantic execution guard on GenLayer Studio Dev (<code>{CONTRACT_ADDRESS}</code>).
              Principals define natural-language policy rules and quota caps; validator LLMs audit
              intents with verbatim quote grounding before single-use tickets can be redeemed.
            </p>
            <div className="cta-row">
              <a className="btn btn-primary" href={withBase("/console/")}>
                Open Live Console
              </a>
              <a className="btn btn-ghost" href={EXPLORER} target="_blank" rel="noreferrer">
                View on Explorer
              </a>
              <a className="btn btn-ghost" href={STUDIO_URL} target="_blank" rel="noreferrer">
                Studio Dev
              </a>
            </div>
          </div>
        </section>

        <section className="wrap section">
          <h2>Why IntentMandateGuard v3.0</h2>
          <div className="grid-3">
            <article className="card">
              <h3>Bounded Semantic Mandates</h3>
              <p>
                Enforce natural-language policy constraints alongside hard quota_cap, tx_cap,
                and method allowlists.
              </p>
            </article>
            <article className="card">
              <h3>Verbatim Quote Grounding</h3>
              <p>
                Every PASS + solid LLM verdict requires a verbatim quote verified on-chain against
                the canonical intent or rules.
              </p>
            </article>
            <article className="card">
              <h3>Deadline-Split & Receipts</h3>
              <p>
                Permissionless sweep_expired_ticket unlocks expired reservations; executors anchor
                calldata SHA-256 receipts on-chain.
              </p>
            </article>
          </div>
        </section>

        <section className="wrap section">
          <h2>Console & Artifacts</h2>
          <div className="grid-3">
            <a className="card" href={withBase("/console/")}>
              <h3>Live Console</h3>
              <p>register_mandate, issue_ticket, redeem_ticket, record_execution_receipt, sweep.</p>
            </a>
            <a className="card" href={withBase("/quickstart/")}>
              <h3>Quickstart</h3>
              <p>Copy-paste Studio Dev payloads and verified transaction hashes.</p>
            </a>
            <a className="card" href={withBase("/evidence-explorer/")}>
              <h3>Integrity Pack</h3>
              <p>Inspect CODE_SNAPSHOT.json and contract SHA-256 checksums.</p>
            </a>
            <a className="card" href={withBase("/features/")}>
              <h3>Method Matrix</h3>
              <p>Complete reference for all 17 write and view entrypoints.</p>
            </a>
            <a className="card" href={withBase("/security/")}>
              <h3>Security Hardening</h3>
              <p>Address canonicalization, replay nonces, and prompt-injection isolation.</p>
            </a>
            <a className="card" href={withBase("/submit/")}>
              <h3>Milestone Kit</h3>
              <p>One-click copy fields for v3.0 milestone submission.</p>
            </a>
          </div>
          <div className="cta-row" style={{ marginTop: "1rem" }}>
            <button className="btn btn-ghost" type="button" onClick={downloadIntegrityPack}>
              Download integrity pack
            </button>
            {packStatus && <span style={{ color: "var(--teal)" }}>{packStatus}</span>}
          </div>
        </section>
      </main>

      <footer className="wrap footer">
        <div>IntentMandateGuard/v3.0 · GenLayer Studio Dev (61997)</div>
        <div>
          <a href={withBase("/submit/")}>Submit kit</a> · MIT License · © 2026 Andrii Efimenko
        </div>
      </footer>
    </>
  );
}
