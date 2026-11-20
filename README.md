<p align="center">
  <img src="brand/logo.svg" alt="IntentMandateGuard v3.0" width="460" />
</p>

<h1 align="center">IntentMandateGuard v3.0</h1>

<p align="center">
  <strong>Bounded, non-transferable semantic execution mandates, single-use intent tickets, verbatim-grounded AI audits, deadline-split settlement, and on-chain execution receipts on GenLayer.</strong>
</p>

<p align="center">
  <a href="https://dorinalunar.github.io/intent-mandate-guard/"><img src="https://img.shields.io/badge/Live_Console-GitHub_Pages-00bfa6?style=for-the-badge" alt="Live Console" /></a>
  <a href="https://studio-dev.genlayer.com/?import-contract=0xACA0da3b7b6CC25d8B65040f325F98603beAD072"><img src="https://img.shields.io/badge/GenLayer-Studio-6c5ce7?style=for-the-badge" alt="GenLayer Studio" /></a>
  <a href="https://explorer-studio-dev.genlayer.com/address/0xACA0da3b7b6CC25d8B65040f325F98603beAD072"><img src="https://img.shields.io/badge/Explorer-Contract-0984e3?style=for-the-badge" alt="Explorer" /></a>
  <a href="LICENSE.md"><img src="https://img.shields.io/badge/License-MIT-2d3436?style=for-the-badge" alt="MIT License" /></a>
</p>

---

## Live Deployment & Verification

| Component | Details |
| :--- | :--- |
| **Protocol Version** | `IntentMandateGuard/v3.0` |
| **Network** | GenLayer Studio Dev (`chain 61997`) |
| **Contract Address** | [`0xACA0da3b7b6CC25d8B65040f325F98603beAD072`](https://explorer-studio-dev.genlayer.com/address/0xACA0da3b7b6CC25d8B65040f325F98603beAD072) |
| **GenLayer Studio** | [Import Contract in Studio](https://studio-dev.genlayer.com/?import-contract=0xACA0da3b7b6CC25d8B65040f325F98603beAD072) |
| **Live Web Console** | [dorinalunar.github.io/intent-mandate-guard](https://dorinalunar.github.io/intent-mandate-guard/) |
| **Source File** | [`contracts/IntentMandateGuard.py`](contracts/IntentMandateGuard.py) |
| **Source SHA-256** | `8e207b783f0a5b50c119c7ff28477b3bf9bc02ef95f71afea0b1a35688cf29a1` |
| **Deploy Record** | [`STUDIO_DEV_DEPLOY.md`](STUDIO_DEV_DEPLOY.md) |
| **Milestone Hardening** | [`docs/MILESTONE_V3_HARDENING.md`](docs/MILESTONE_V3_HARDENING.md) |

---

## Overview

Autonomous agents and off-chain executors need bounded authority before interacting with high-value protocols. Traditional smart contract allowlists can check addresses and numeric caps, but they cannot verify natural-language policy constraints (such as slippage intent, approved counterparty context, or operational rules).

**IntentMandateGuard v3.0** solves this on GenLayer by combining deterministic quota/nonce enforcement with **verbatim-grounded LLM validator consensus**:

1. **Non-Custodial Authorization**: No native assets are custodied inside the guard contract; it issues cryptographic, single-use execution tickets verified by downstream adapters.
2. **Verbatim Quote Grounding**: Every `PASS` verdict with `solid` certainty must cite an exact substring present in the canonical intent JSON, decoded payload, or mandate rules. Hallucinated or ungrounded approvals are automatically rejected.
3. **Deadline-Split Settlement**: Tickets cleanly separate redemption (`can_redeem`) from permissionless expiration cleanup (`can_sweep`) at `expires_at`, ensuring reserved quota is never permanently locked.
4. **On-Chain Execution Receipts**: After redemption, executors or operators anchor the downstream `calldata_sha256` and `external_tx_ref` on-chain for full end-to-end auditability.

---

## Protocol Lifecycle

    [Principal]                  [Operator]                   [Executor]
         |                            |                            |
         |-- 1. register_mandate() -->|                            |
         |   (rules, methods, caps)   |                            |
         |                            |-- 2. issue_ticket() ------>|
         |                            |   (canonical intent + AI)  |
         |                            |                            |
         |                            |      3. redeem_ticket() <--|
         |                            |         (proof_hash match) |
         |                            |                            |
         |                            | 4. record_execution_receipt|
         |                            |    (calldata_sha256 + tx)  |
         |                            |                            |
         |-- terminate_mandate()      | [After expires_at]         |
         |                            | 5. sweep_expired_ticket()  |

---

## Key Hardening in v3.0

- **Canonical Address Normalization (`_addr_to_hex`)**: Consistently normalizes GenLayer `Address` objects, integer UI inputs, and mixed-case hex strings so role checks (`principal`, `operator`, `executor`) never drift across clients.
- **Unescaped JSON Payload Grounding (`_build_searchable_sources`)**: Searches both the canonical JSON string and the decoded inner `payload` object, allowing validator LLMs to cite unescaped fields (e.g. `"maxSlippageBps":25`) without false downgrades.
- **Heterogeneous Validator Consensus Stability**: `normalize_assessments` tolerates valid extra metadata fields returned by diverse LLM providers while strictly enforcing verbatim quote grounding before granting `PASS + solid`.
- **Replay & Quota Protection**: Enforces monotonic `seq_nonce` per mandate, strict `quota_cap` and `tx_cap` accounting, and permissionless sweeping of expired reservations.

---

## Verified On-Chain Transactions

| Step | Action | Sender | Status | Transaction |
| :---: | :--- | :--- | :---: | :--- |
| 1 | `Deploy` (`IntentMandateGuard/v3.0`) | `0x38409cca...18b478dd` | `FINALIZED` | [`0x6b88abc0...8a3853c`](https://explorer-studio-dev.genlayer.com/tx/0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c) |
| 2 | `register_mandate` | `0x38409cca...18b478dd` | `FINALIZED` | [`0x94151a08...52b5b28`](https://explorer-studio-dev.genlayer.com/tx/0x94151a08f4a0bed67e2fd44ac44e26f9008fbad12aa14d51686d9364b52b5b28) |
| 3 | `issue_ticket` | `0x38409cca...18b478dd` | `FINALIZED` | [`0x62048c59...967886d`](https://explorer-studio-dev.genlayer.com/tx/0x62048c591d8e3814b006bfbe813a9f0a69c2d6833943c56f881d8b814967886d) |

---

## Quickstart

### 1. Run the Test Suite & Integrity Checks

    python3 -m pip install -r requirements-dev.txt
    python3 scripts/update_code_snapshot.py verify
    python3 scripts/validate_schemas.py
    python3 -m pytest -v

### 2. Run the Web Console Locally

    cd web
    npm install
    npm run dev
    # Open http://localhost:3000/console/

### 3. Verify Deployed Bytecode / Source Hash

    curl -s -X POST https://studio-dev.genlayer.com/api -H 'content-type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"gen_getContractCode","params":["0xACA0da3b7b6CC25d8B65040f325F98603beAD072"]}' \
      | python3 -c "import sys,json,base64,hashlib; print(hashlib.sha256(base64.b64decode(json.load(sys.stdin)['result'])).hexdigest())"

    shasum -a 256 contracts/IntentMandateGuard.py
    # Expected: 8e207b783f0a5b50c119c7ff28477b3bf9bc02ef95f71afea0b1a35688cf29a1

---

## Repository Structure

    intent-mandate-guard/
    ├── contracts/
    │   └── IntentMandateGuard.py       # Core v3.0 GenLayer Intelligent Contract
    ├── web/                            # Next.js static web console & documentation site
    │   ├── public/                     # Static assets, logo, OpenAPI, integrity packs
    │   └── src/                        # App Router pages, WalletProvider, Console UI
    ├── test/                           # Unit & v3.0 hardening test suites (pytest)
    ├── scripts/                        # Snapshot, schema validation & integrity pack CLIs
    ├── schemas/                        # JSON Schemas for snapshots and intent tickets
    ├── docs/                           # Hardening notes & Studio Dev runbooks
    ├── brand/                          # SVG logos and icons
    ├── ExecutionAdapter.py             # Reference downstream execution adapter
    ├── STUDIO_DEV_DEPLOY.md            # On-chain deployment record & tx proofs
    └── ARCHITECTURE.md                 # System design and threat model

---

## Documentation & Resources

- **Architecture & Threat Model**: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **Security Policy**: [`SECURITY.md`](SECURITY.md)
- **Changelog**: [`CHANGELOG.md`](CHANGELOG.md)
- **Submission Kit**: [`SUBMIT.md`](SUBMIT.md)
- **Demo Flow**: [`examples/demo_flow.md`](examples/demo_flow.md)

---

## License

Released under the [MIT License](LICENSE.md).
