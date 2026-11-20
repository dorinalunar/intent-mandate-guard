# Changelog

## [3.0.0] — 2026-11-19 · Hardening, Address Canonicalization & Verbatim Quote Grounding

| Area | Change |
|------|--------|
| Contract | Added `_addr_to_hex` canonicalization for `Address`, `int`, and hex strings across all role and mandate checks |
| Contract | Added `_build_searchable_sources` to ground LLM quotes against both canonical JSON and decoded nested `payload` objects |
| Contract | Hardened `normalize_assessments` and `validator_check` for multi-model consensus stability across heterogeneous validator LLMs |
| Contract | Added `record_execution_receipt`, `sweep_expired_ticket`, `get_ticket_schedule`, and paginated `list_mandates` / `list_tickets` / `list_mandate_tickets` |
| Deployment | Deployed `IntentMandateGuard/v3.0` on Studio Dev (`61997`) → `0xcB45206f7162BFc5427Df038F750B1F3705e0c5a` (tx `0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c`) |
| Tests | Added 60-test verification suite (`tests/test_mandate_lifecycle.py` and `tests/test_v3_hardening.py`) |
| Web | Updated Next.js console, actions, forms, and documentation pages to `IntentMandateGuard/v3.0` (`0xcB45206f7162BFc5427Df038F750B1F3705e0c5a`) |
