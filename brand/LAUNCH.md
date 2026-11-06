# Launch Playbook — IntentMandateGuard

## Announcement Thread Template (X / Telegram)

**Post 1:**
Introducing **IntentMandateGuard (v2.0)** on @GenLayer — a non-custodial Intelligent Contract for bounded semantic execution mandates and single-use intent tickets.

How do you let AI agents execute DeFi & treasury ops without risking rogue transactions?

**Post 2:**
1/ Three-Role Separation:
* **Principal:** Defines 1–6 semantic rules, method allowlists, and quota caps.
* **Operator:** Submits structured JSON intents (`method`, `target`, `payload`) for AI auditing.
* **Executor:** Redeems `ACTIVE` tickets verified against a SHA-256 `proof_hash`.

**Post 3:**
2/ Fail-Closed GenVM Consensus:
Leader and validator nodes independently evaluate every rule via `gl.nondet.exec_prompt` inside `gl.vm.run_nondet_unsafe`.
All fields are treated strictly as passive untrusted data to neutralize prompt injection. Approval requires `PASS` + `solid` certainty across every rule.
