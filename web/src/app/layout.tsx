import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IntentMandateGuard v3.0 — Bounded Semantic Execution Mandates",
  description:
    "Semantic execution guard on GenLayer: bounded mandates, single-use intent tickets, verbatim-grounded AI audits, deadline-split sweeps, and on-chain execution receipts.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
