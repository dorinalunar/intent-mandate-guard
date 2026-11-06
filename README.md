# IntentMandateGuard — Bounded Semantic Execution Mandates on GenLayer

**IntentMandateGuard** (`IntentMandateGuard/v2.0`) is a non-custodial GenLayer Intelligent Contract and Web3 Command Center for bounded, non-transferable semantic execution mandates and single-use intent tickets.

No native assets are custodied inside the contract. Downstream execution adapters verify and redeem the exact cryptographically committed intent payload after transaction finality before triggering external effects.

---

## Key Capabilities

1. **Three-Role Separation (`principal`, `operator`, `executor`):**
   * **Principal:** Registers the mandate (`register_mandate`), defines 1–6 natural-language semantic constraints, sets the method allowlist (1–8 methods), configures `quota_cap`, `tx_cap`, and `ttl_seconds`, and can unilaterally halt the mandate (`terminate_mandate`).
   * **Operator:** Submits candidate structured intents (`method`, `target`, `payload`) to `issue_ticket` with a monotonic `seq_nonce` and quota `weight`.
   * **Executor:** Redeems `ACTIVE` tickets (`redeem_ticket`) by presenting the exact committed `intent_json`, converting locked quota into consumed quota.
2. **Fail-Closed GenVM AI Consensus (`INTENT_MANDATE_GUARD_V2`):**
   * Evaluates every mandate rule independently via `gl.nondet.exec_prompt` inside `gl.vm.run_nondet_unsafe`.
   * Treats `target` and `payload` strictly as passive untrusted data to neutralize embedded prompt injections.
   * Requires unanimous `outcome == "PASS"` and `certainty == "solid"` across **every** rule. Any `FAIL`, `AMBIGUOUS`, or lower certainty tier marks the ticket `DENIED` without locking quota.
3. **Two-Phase Quota Reservation & SHA-256 Proof Anchors:**
   * Approved tickets lock `weight` in `locked_quota` and increment `locked_txs`.
   * Each ticket commits `protocol`, `chain_id`, `contract`, `mandate_id`, `seq_nonce`, `executor`, `weight`, and `intent` into a canonical SHA-256 `proof_hash`.
   * Unredeemed reservations can be released via `cancel_reservation`.

---

## Repository Layout

* `IntentMandateGuard.py` — GenLayer Intelligent Contract (`IntentMandateGuard/v2.0`).
* `test_intent_mandate_guard.py` — Deterministic `pytest` suite with local GenVM mock.
* `sample_dataset.json` — Reference DeFi swap and bridge mandate scenarios.
* `index.html` & `main.js` — Browser Command Center using encoded `genlayer-js` SDK calls.
* `STATUS.md` — Verification status, invariant checklist, and deployment readiness report.
* `brand/` — Brand identity (`BRAND.md`), UI copy (`COPY.md`), launch playbook (`LAUNCH.md`), and naming taxonomy (`NAMES.md`).
* `.github/workflows/` — Automated `ci.yml` (`pytest`) and `pages.yml` (GitHub Pages deployment).

---

## Quickstart & Local Verification

Install dependencies and run the unit test suite:

```bash
pip install -r requirements.txt
pytest test_intent_mandate_guard.py -v
```

---

## License

Released under the MIT License.
