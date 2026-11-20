# IntentMandateGuard v3.0

**Bounded, non-transferable semantic execution mandates, single-use intent tickets, verbatim-grounded AI audits, deadline-split settlement, and on-chain execution receipts on GenLayer.**

| | |
|---|---|
| **Protocol Version** | `IntentMandateGuard/v3.0` |
| **Contract (Studio Dev, chain 61997)** | [`0xcB45206f7162BFc5427Df038F750B1F3705e0c5a`](https://explorer-studio-dev.genlayer.com/address/0xcB45206f7162BFc5427Df038F750B1F3705e0c5a) · [Deploy Record](STUDIO_DEV_DEPLOY.md) |
| **Deploy Tx** | [`0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c`](https://explorer-studio-dev.genlayer.com/tx/0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c) |
| **Milestone Hardening** | [`docs/MILESTONE_V3_HARDENING.md`](docs/MILESTONE_V3_HARDENING.md) |
| **Studio Dev Run** | https://studio-dev.genlayer.com/run-debug |
| **License** | [MIT](LICENSE.md) |

---

## Overview

`IntentMandateGuard` enforces semantic policy boundaries before an off-chain or downstream executor can act on an intent:

1. **Register Mandate (`register_mandate`)**: A principal defines natural-language semantic rules (1–6 rules), an allowlist of methods, `quota_cap`, `tx_cap`, `ttl_seconds`, and authorized `operator` and `executor` addresses.
2. **Issue Single-Use Ticket (`issue_ticket`)**: The operator submits a canonical JSON intent (`method`, `target`, `payload`) with a unique `seq_nonce` and `weight`. GenLayer validators evaluate every rule independently and verify that every `PASS` is backed by `solid` certainty and a **verbatim quote grounded in the intent or rules**.
3. **Redeem Ticket (`redeem_ticket`)**: Before `expires_at`, only the designated `executor` can redeem an `ACTIVE` ticket by presenting the exact committed intent payload matching the cryptographic anchor (`proof_hash`).
4. **Record Execution Receipt (`record_execution_receipt`)**: After redemption, the executor or operator anchors the downstream `calldata_sha256` and `external_tx_ref` on-chain.
5. **Deadline-Split Cleanup (`sweep_expired_ticket`)**: Once `expires_at` passes (or the principal calls `terminate_mandate`), anyone can permissionlessly sweep expired `ACTIVE` tickets to unlock reserved quota.

---

## Quickstart

### 1. Run the 60-Test Suite

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/update_code_snapshot.py verify
python3 scripts/validate_schemas.py
python3 -m pytest -v
```

### 2. Run the Web Console Locally

```bash
cd web
npm install
npm run dev
# Open http://localhost:3010/console/
```

The console connects directly to [`0xcB45206f7162BFc5427Df038F750B1F3705e0c5a`](https://explorer-studio-dev.genlayer.com/address/0xcB45206f7162BFc5427Df038F750B1F3705e0c5a) on GenLayer Studio Dev (`chain 61997`).
