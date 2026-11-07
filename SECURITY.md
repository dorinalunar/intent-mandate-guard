# Security Policy & Threat Model — IntentMandateGuard

## Core Security Principles

`IntentMandateGuard.py` is engineered around a strict **fail-closed**, **non-custodial** security model for AI-assisted transaction authorization on GenVM.

---

## 1. Prompt Injection & Untrusted Input Isolation

Autonomous operators and external dApps may pass arbitrary strings inside `intent_json` (`target` and `payload`). To prevent adversarial prompt injection:

* **Passive Data Framing:** The `INTENT_MANDATE_GUARD_V2` system prompt explicitly instructs the LLM to treat all JSON fields strictly as passive untrusted data and never as system instructions.
* **Strict Schema Normalization:** Raw LLM output is validated by `normalize_assessments()`, which enforces exact key sets (`{"assessments"}` at root and `{"index", "outcome", "certainty"}` per entry), rejects duplicate or out-of-bounds rule indices, and halts on any unrecognized token.

---

## 2. Fail-Closed Consensus Semantics

A single-use ticket is granted `ACTIVE` status if and only if **every** semantic rule in the mandate achieves:

* `outcome == "PASS"`
* `certainty == "solid"`

If any rule evaluates to `FAIL` or `AMBIGUOUS`, or if the certainty tier is `moderate` or `weak`, the ticket automatically fails closed to `DENIED` and **zero quota is locked**. Furthermore, inside `gl.vm.run_nondet_unsafe`, validators independently run `evaluate_rules_nondet(rules, intent)` and require exact matrix equality (`candidate == independent`).

---

## 3. Two-Phase Quota Accounting & Replay Prevention

* **Sequence Nonce Isolation:** Each `issue_ticket` call consumes a unique `"{mandate_id}:{seq_nonce}"` key in `used_nonces`, preventing duplicate ticket issuance.
* **Bounded Payload Sizes:** `intent_json` is capped at 10,000 characters (`method` <= 40, `target` <= 200, `payload` <= 6,000), `rules_json` at 6,000 characters (1..6 rules, <= 800 chars each), and `methods_json` at 500 characters (1..8 unique methods).
* **Atomic Quota Reservation:** Approved tickets move quota into `locked_quota` and `locked_txs`. Quota is only permanently finalized into `used_quota` upon valid `redeem_ticket` execution, or returned to available capacity via `cancel_reservation`.
* **Emergency Kill-Switch:** The mandate `principal` can invoke `terminate_mandate` at any time to immediately block new ticket issuance and halt pending redemptions.

---

## Reporting a Vulnerability

If you discover a consensus bypass, quota accounting flaw, or schema parsing vulnerability, please open a detailed issue in this repository with a minimal reproducible test case.
