# Milestone: IntentMandateGuard v3.0 Hardening

**Summary:** v3.0 hardens `IntentMandateGuard` for production GenLayer Studio Dev (`61997`) execution, eliminating GenVM `Address` type serialization mismatches, stabilizing multi-model LLM consensus over verbatim-grounded quotes, enforcing deadline-split settlement via `sweep_expired_ticket`, and adding on-chain `record_execution_receipt` attestations.

| Field | Value |
|---|---|
| **Protocol Tag** | `IntentMandateGuard/v3.0` |
| **Deployment Address** | [`0xcB45206f7162BFc5427Df038F750B1F3705e0c5a`](https://explorer-studio-dev.genlayer.com/address/0xcB45206f7162BFc5427Df038F750B1F3705e0c5a) |
| **Deploy Transaction** | [`0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c`](https://explorer-studio-dev.genlayer.com/tx/0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c) |
| **Contract SHA-256** | `8e207b783f0a5b50c119c7ff28477b3bf9bc02ef95f71afea0b1a35688cf29a1` |
| **Verification Suite** | 60 unit & property tests (`tests/test_mandate_lifecycle.py` + `tests/test_v3_hardening.py`) |

## What Changed in v3.0

1. **Deterministic Address Canonicalization (`_addr_to_hex`)**
   * Studio Dev UI passes `Address` arguments either as `Address` instances (`.as_hex`), decimal integers (`int`), or hex strings.
   * `_addr_to_hex` converts all representations to lowercase `0x`-prefixed 40-char hex strings, eliminating `[HALT] Caller is not the authorized operator` mismatches.
2. **Inner-Payload Quote Grounding (`_build_searchable_sources`)**
   * Nested JSON payloads inside `intent_json` contain escaped quotes in canonical JSON (`\"maxSlippageBps\":25`), whereas LLM validators quote unescaped fields (`"maxSlippageBps":25`).
   * `quote_grounded_in_source` decodes nested JSON payloads and checks quotes against both canonical and unescaped representations while still rejecting fabricated quotes (`grounded=False` downgrades `PASS + solid` to `AMBIGUOUS`).
3. **Resilient Multi-Model Consensus (`normalize_assessments` & `validator_check`)**
   * Validator pools combine multiple LLM families (Claude, GPT, DeepSeek, Gemma) that may attach auxiliary keys or choose different supporting quotes.
   * `normalize_assessments` safely extracts required schema fields and `validator_check` verifies consensus on `(index, outcome)` after independent quote grounding.
4. **Permissionless Expiry Cleanup (`sweep_expired_ticket`) & Schedule View (`get_ticket_schedule`)**
   * After `expires_at` or `terminate_mandate`, anyone can call `sweep_expired_ticket` to release locked quota and transition `ACTIVE` tickets to `EXPIRED`.
   * `get_ticket_schedule` guarantees `can_redeem` and `can_sweep` are mutually exclusive at every timestamp.
5. **On-Chain Execution Receipts (`record_execution_receipt`) & Paginated Views**
   * Redeemed tickets can be linked to downstream execution calldata (`calldata_sha256`) and external transaction hashes (`external_tx_ref`).
   * `list_mandates`, `list_tickets`, and `list_mandate_tickets` provide bounded pagination (`limit <= 100`).

## Verification

* **On-Chain Studio Dev Run**: Confirmed `Deploy` (`0x6b88abc0bf8f...`), `register_mandate` (`0x94151a08f4a0...`), and `issue_ticket` (`0x62048c591d8e...`) finalized on [`0xcB45206f7162BFc5427Df038F750B1F3705e0c5a`](https://explorer-studio-dev.genlayer.com/address/0xcB45206f7162BFc5427Df038F750B1F3705e0c5a).
* **Offline Test Suite**: 60 automated tests covering lifecycle transitions, role enforcement, nonce replay protection, quote grounding, consensus disagreement, deadline boundaries, pagination, and randomized quota-conservation fuzzing.
