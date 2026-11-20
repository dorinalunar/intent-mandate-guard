# Changelog

## [3.0.0] — 2026-11-20 · Hardening, Consensus Binding & Studio Dev Deployment

| Area | Change |
|------|--------|
| Contract | Validators compare `(index, outcome, authorized)` per rule, where `authorized = PASS + solid + grounded`, ensuring consensus binds every bit that affects ticket issuance |
| Contract | Quotes are grounded against the intent only; rule text is not treated as evidence of intent compliance |
| Contract | Default anchor `chain_id` set to Studio Dev `61997` |
| Contract | Per-mandate ticket index uses `mandate_ticket_count` + `mandate_ticket_at` (O(1) per ticket) instead of rewriting a growing JSON list |
| Contract | Added `_addr_to_hex` canonicalization across all role, mandate, and `swept_by` fields |
| Contract | Added `record_execution_receipt`, `sweep_expired_ticket`, `get_ticket_schedule`, and paginated `list_mandates` / `list_tickets` / `list_mandate_tickets` |
| Adapter | Validates padded `target`/`method`/`payload` and JSON payloads before redemption and requires `wait_for_finality(ticket_id)` before dispatching external effects |
| Deployment | Deployed `IntentMandateGuard` on Studio Dev (`61997`) → `0xACA0da3b7b6CC25d8B65040f325F98603beAD072` (tx `0xab2461e23b7243a21ad85a9e1ebb992d864db8a6986ce8d3028bdb746263a299`) |
| Tests | 81-test verification suite across `test/test_mandate_lifecycle.py`, `test/test_v3_hardening.py`, and `test/test_security_fixes.py` |
| Web | Updated Next.js console, explorer links, actions, forms, and documentation pages for Studio Dev (`61997`) |
