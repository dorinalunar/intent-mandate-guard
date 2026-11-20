"use client";

import { MandateGuardConsole } from "@/components/MandateGuardConsole";
import { WalletProvider } from "@/components/WalletProvider";
import { withBase } from "@/lib/basePath";
import { GITHUB } from "@/lib/config";

export default function ConsolePage() {
  return (
    <>
      <header className="wrap nav">
        <div className="brand">
          <img src={withBase("/logo.svg")} alt="IntentMandateGuard" />
          IntentMandateGuard v3.0
        </div>
        <nav className="nav-links">
          <a href={withBase("/")}>Home</a>
          <a href={withBase("/quickstart/")}>Quickstart</a>
          <a href={withBase("/console/")}>Console</a>
          <a href={GITHUB} target="_blank" rel="noreferrer">
            GitHub
          </a>
        </nav>
      </header>
      <main className="wrap" style={{ paddingBottom: "3rem" }}>
        <WalletProvider>
          <MandateGuardConsole />
        </WalletProvider>
      </main>
    </>
  );
}
