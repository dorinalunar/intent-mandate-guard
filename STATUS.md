# Project Status — IntentMandateGuard (`IntentMandateGuard/v2.0`)

## Milestone Checklist

* **Intelligent Contract (`IntentMandateGuard.py`):** Completed & Steward-Approved.
* **Deployed Contract (Studio):** `0x45d5b9fCEe51A8E58327E6C9eCa060bc7777559c`
* **Protocol Version:** `IntentMandateGuard/v2.0`
* **GenVM Dependency:** `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`
* **Unit & Dataset Tests (`test_intent_mandate_guard.py`):** 6/6 passing (`pytest`).
* **Frontend SDK Integration (`main.js`):** Completed using official `genlayer-js` (`createClient` + `studionet`) with encoded `readContract()` and wallet-signed `writeContract()`.
* **CI / Pages Workflows:** Configured in `.github/workflows/ci.yml` and `.github/workflows/pages.yml`.

---

## Verified Contract Invariants

1. **Zero Asset Custody:** The contract stores only mandate state, quota counters, and cryptographic intent commitments (`proof_hash`).
2. **Strict JSON Boundaries:** Intent payloads are capped at 10,000 chars (`method` <= 40, `target` <= 200, `payload` <= 6,000); mandate rules are capped at 1..6 rules (<= 800 chars each) and 1..8 unique allowlisted methods.
3. **Unanimous Solid Consensus:** A ticket transitions to `ACTIVE` if and only if every rule evaluates to `PASS` with `solid` certainty in both leader and validator runs.
4. **Replay & Quota Safety:** `used_nonces` prevents sequence nonce reuse per mandate (`mandate_id:seq_nonce`), and `locked_quota` / `used_quota` never exceed `quota_cap`.