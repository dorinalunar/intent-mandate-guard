# Contributing Guidelines — IntentMandateGuard

Thank you for contributing to **IntentMandateGuard**. Because this repository contains a steward-approved GenLayer Intelligent Contract, all contributions must adhere to strict determinism and safety standards.

---

## Development Rules

1. **Preserve Non-Custodial Design:** Do not introduce native token custody, balance transfers, or external mutable calls inside `IntentMandateGuard.py`.
2. **Maintain Fail-Closed Validation:** Any changes to `parse_intent_payload` or `normalize_assessments` must reject malformed schemas, out-of-range integers, and unexpected JSON keys with `gl.vm.UserError`.
3. **GenVM Compatibility:** Keep the contract header `# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }` intact and avoid non-deterministic Python standard library calls outside GenVM primitives.
4. **Frontend SDK Standards:** All browser interactions in `main.js` must use official `genlayer-js` client methods (`readContract`, `writeContract`, `waitForTransactionReceipt`) rather than raw unsigned RPC fetches.

---

## Pre-Submission Verification

Before opening a pull request, install the test dependencies and verify that all unit and dataset tests pass locally:

    pip install -r requirements.txt
    pytest test_intent_mandate_guard.py -v
    
