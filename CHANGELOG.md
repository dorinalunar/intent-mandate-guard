# Changelog

## [3.1.0] — 2026-11-20 · Consensus binds the authorization bit (NOT DEPLOYED YET)

| Area | Change |
|------|--------|
| Contract | Validators now compare `(index, outcome, authorized)` per rule, where `authorized = PASS + solid + grounded`. Before, only `outcome` was compared, so a leader's "solid" vs a validator's "moderate" agreed while only the leader decided issuance |
| Contract | Quotes are grounded against the intent only. Rule text is no longer evidence that the intent satisfies the rule; the prompt asks for intent quotes only |
| Contract | Default anchor `chain_id` is Studio Dev `61997` (was `61999`) |
| Contract | Per-mandate ticket index uses `mandate_ticket_count` + `mandate_ticket_at` (O(1) per ticket) instead of rewriting one growing JSON list |
| Contract | `swept_by` stored as lowercase hex like every other address |
| Contract | Runner unchanged (`py-genlayer:1jb45aa8…`, the SDK this code is written for). Moving to the GenVM v0.4 runner needs the v0.4 import style; see the Ukrainian instructions |
| Web / env | Explorer links and `.env.example` point to Studio Dev (were Studio) |
| Adapter | Refuses padded `target`/`method`/`payload` and non-JSON payloads BEFORE redeeming, so a ticket is never burned without an action |
| Adapter | Requires a `wait_for_finality(ticket_id)` callback and dispatches the external effect only after the redemption is FINALIZED |
| Tests | 11 new tests in `test/test_v31_fixes.py`; tests 01, 26, 33 updated to the new rules (81 total) |

## [3.0.0] — 2026-11-19 · Hardening, Address Canonicalization & Verbatim Quote Grounding

| Area | Change |
|------|--------|
| Contract | Added `_addr_to_hex` canonicalization for `Address`, `int`, and hex strings across all role and mandate checks |
| Contract | Added `_build_searchable_sources` to ground LLM quotes against both canonical JSON and decoded nested `payload` objects |
| Contract | Hardened `normalize_assessments` and `validator_check` for multi-model consensus stability across heterogeneous validator LLMs |
| Contract | Added `record_execution_receipt`, `sweep_expired_ticket`, `get_ticket_schedule`, and paginated `list_mandates` / `list_tickets` / `list_mandate_tickets` |
| Deployment | Deployed `IntentMandateGuard/v3.0` on Studio Dev (`61997`) → `0xACA0da3b7b6CC25d8B65040f325F98603beAD072` (tx `0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c`) |
| Tests | Added 60-test verification suite (`tests/test_mandate_lifecycle.py` and `tests/test_v3_hardening.py`) |
| Web | Updated Next.js console, actions, forms, and documentation pages to `IntentMandateGuard/v3.0` (`0xACA0da3b7b6CC25d8B65040f325F98603beAD072`) |
