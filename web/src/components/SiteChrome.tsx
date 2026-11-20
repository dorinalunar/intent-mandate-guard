"use client";

import type { ReactNode } from "react";
import { withBase } from "@/lib/basePath";
import { STUDIO_URL } from "@/lib/config";

const LINKS = [
  { href: "/console/", label: "Console" },
  { href: "/how-it-works/", label: "How it works" },
  { href: "/quickstart/", label: "Quickstart" },
  { href: "/evidence-explorer/", label: "Integrity" },
  { href: "/features/", label: "Features" },
  { href: "/api-reference/", label: "API" },
  { href: "/docs/", label: "Docs" },
];

export function SiteNav({ active }: { active?: string }) {
  return (
    <header className="wrap nav">
      <a className="brand" href={withBase("/")}>
        <img src={withBase("/logo.svg")} alt="IntentMandateGuard" />
        IntentMandateGuard
      </a>
      <nav className="nav-links">
        {LINKS.map((l) => (
          <a
            key={l.href}
            href={withBase(l.href)}
            style={
              active === l.href
                ? { color: "var(--teal)", fontWeight: 600 }
                : undefined
            }
          >
            {l.label}
          </a>
        ))}
        <a
          className="btn btn-ghost"
          href={STUDIO_URL}
          target="_blank"
          rel="noreferrer"
        >
          Studio Dev
        </a>
      </nav>
    </header>
  );
}

export function PageShell({
  title,
  lead,
  active,
  children,
}: {
  title: string;
  lead: string;
  active?: string;
  children: ReactNode;
}) {
  return (
    <>
      <SiteNav active={active} />
      <main className="wrap" style={{ padding: "1.5rem 0 4rem" }}>
        <p>
          <a href={withBase("/")} style={{ color: "var(--muted)" }}>
            ← Home
          </a>
        </p>
        <h1 style={{ fontFamily: "Syne, sans-serif", letterSpacing: "-0.02em" }}>
          {title}
        </h1>
        <p className="lead">{lead}</p>
        {children}
      </main>
    </>
  );
}
