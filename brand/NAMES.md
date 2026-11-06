# Naming & Domain Taxonomy — IntentMandateGuard

## Core Terminology

* **Contract Name:** `IntentMandateGuard`
* **Protocol Identifier:** `IntentMandateGuard/v2.0`
* **Mandate (`mandate_id`):** A bounded delegation policy created by a `principal` specifying semantic rules, allowed methods, `quota_cap`, `tx_cap`, and `expires_at`.
* **Intent Ticket (`ticket_id`):** A single-use authorization artifact evaluated by GenVM consensus (`ACTIVE`, `DENIED`, `REDEEMED`, `RELEASED`).
* **Cryptographic Anchor (`proof_hash`):** Canonical SHA-256 digest binding chain ID, contract address, mandate ID, sequence nonce, executor, weight, and intent payload.
