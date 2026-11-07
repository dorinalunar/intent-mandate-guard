# System Architecture — IntentMandateGuard (`IntentMandateGuard/v2.0`)

## Overview

**IntentMandateGuard** implements a non-custodial neuro-symbolic authorization layer on GenLayer. It decouples high-level policy definition (`principal`), day-to-day intent formulation (`operator`), and downstream execution (`executor`), ensuring that autonomous AI agents can only trigger external effects after passing a deterministic GenVM consensus audit.

---

## End-to-End Execution Flow

    [Principal]
         |
         | 1. register_mandate(operator, executor, rules_json, methods_json, quota_cap, tx_cap, ttl_seconds)
         v
    +-------------------------------------------------------------------+
    | IntentMandateGuard State (mandates TreeMap)                       |
    | Stores 1..6 natural-language rules, method allowlist, & caps      |
    +-------------------------------------------------------------------+
         |
         | 2. issue_ticket(mandate_id, seq_nonce, intent_json, weight, ttl_seconds)
         v
    [Operator] ---> Pre-Checks (Role, Expiry, Nonce, Allowlist, Quota)
         |
         | 3. gl.vm.run_nondet_unsafe(leader_eval, validator_check)
         v
    +-------------------------------------------------------------------+
    | GenVM Consensus Audit (INTENT_MANDATE_GUARD_V2)                   |
    | - Leader runs evaluate_rules_nondet() via gl.nondet.exec_prompt   |
    | - Validator normalizes leader matrix & runs independent evaluation|
    | - Requires candidate == independent across all rule indices       |
    +-------------------------------------------------------------------+
         |
         | 4. Decision & Cryptographic Anchoring
         v
    +-------------------------------------------------------------------+
    | Ticket Minted (tickets TreeMap)                                   |
    | - Approved iff ALL rules == ("PASS", "solid") -> state = "ACTIVE" |
    | - Locks weight in locked_quota & increments locked_txs            |
    | - Commits canonical anchor into SHA-256 proof_hash                |
    +-------------------------------------------------------------------+
         |
         | 5. redeem_ticket(ticket_id, intent_json)
         v
    [Executor] ---> Verifies ACTIVE state, TTL, & exact intent match
                    Converts locked_quota -> used_quota, state -> "REDEEMED"
                    Returns { proof_hash, intent, weight } to downstream adapter

---

## State & Storage Model

* **`mandates: TreeMap[u256, str]`** — Stores canonical JSON records indexed by `mandate_id`, tracking `quota_cap`, `tx_cap`, `locked_quota`, `used_quota`, `locked_txs`, `used_txs`, `expires_at`, and `terminated`.
* **`tickets: TreeMap[u256, str]`** — Stores canonical JSON records indexed by `ticket_id`, binding the original `intent`, AI `assessments` matrix, canonical `anchor`, SHA-256 `proof_hash`, and lifecycle `state` (`ACTIVE`, `DENIED`, `REDEEMED`, `RELEASED`).
* **`used_nonces: TreeMap[str, bool]`** — Replay-protection registry keyed by `"{mandate_id}:{seq_nonce}"`.

---

## Cryptographic Anchor Structure

Every issued ticket computes a deterministic SHA-256 `proof_hash` over the canonical JSON serialization of:

* `protocol`: `"IntentMandateGuard/v2.0"`
* `chain_id`: GenVM execution chain identifier (`gl.message.chain_id`)
* `contract`: Deployed `IntentMandateGuard` contract address
* `mandate_id`: Parent mandate identifier
* `seq_nonce`: Unique operator sequence nonce
* `executor`: Designated downstream executor address
* `weight`: Quota units reserved by the ticket
* `intent`: Exact `{"method", "target", "payload"}` dictionary
