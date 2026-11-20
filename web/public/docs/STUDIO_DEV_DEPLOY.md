# IntentMandateGuard v3.0 — Studio Dev Deploy Record

| Field | Value |
|---|---|
| **Network** | GenLayer Studio Dev (`chain 61997`) |
| **RPC** | `https://studio-dev.genlayer.com/api` |
| **Active Contract (v3.0)** | [`0xcB45206f7162BFc5427Df038F750B1F3705e0c5a`](https://explorer-studio-dev.genlayer.com/address/0xcB45206f7162BFc5427Df038F750B1F3705e0c5a) |
| **Deploy Tx** | [`0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c`](https://explorer-studio-dev.genlayer.com/tx/0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c) |
| **Creator / Principal** | `0x38409cca5f5ca70f3fe189638a87862318b478dd` |
| **Deployed Timestamp** | `2026-11-19T23:34:13Z` |
| **Source File** | [`contracts/IntentMandateGuard.py`](contracts/IntentMandateGuard.py) |
| **Source SHA-256** | `8e207b783f0a5b50c119c7ff28477b3bf9bc02ef95f71afea0b1a35688cf29a1` |
| **Previous Staging Deploy** | `0x486208a0eD969039F7aF2D238c92b31b03E931D1` (superseded by v3.0 hardening deployment) |

## Verified On-Chain Transactions

| Step | Method / Action | Sender | Status | Transaction Hash |
|---|---|---|---|---|
| 1 | `Deploy` (`IntentMandateGuard/v3.0`) | `0x38409cca5f5ca70f3fe189638a87862318b478dd` | `FINALIZED` | [`0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c`](https://explorer-studio-dev.genlayer.com/tx/0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c) |
| 2 | `register_mandate` (Call #1) | `0x38409cca5f5ca70f3fe189638a87862318b478dd` | `FINALIZED` | [`0x94151a08f4a0bed67e2fd44ac44e26f9008fbad12aa14d51686d9364b52b5b28`](https://explorer-studio-dev.genlayer.com/tx/0x94151a08f4a0bed67e2fd44ac44e26f9008fbad12aa14d51686d9364b52b5b28) |
| 3 | `issue_ticket` (Call #2) | `0x38409cca5f5ca70f3fe189638a87862318b478dd` | `FINALIZED` | [`0x62048c591d8e3814b006bfbe813a9f0a69c2d6833943c56f881d8b814967886d`](https://explorer-studio-dev.genlayer.com/tx/0x62048c591d8e3814b006bfbe813a9f0a69c2d6833943c56f881d8b814967886d) |

## Verify Contract Source Hash

```bash
curl -s -X POST https://studio-dev.genlayer.com/api -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"gen_getContractCode","params":["0xcB45206f7162BFc5427Df038F750B1F3705e0c5a"]}' \
  | python3 -c "import sys,json,base64,hashlib; print(hashlib.sha256(base64.b64decode(json.load(sys.stdin)['result'])).hexdigest())"
shasum -a 256 contracts/IntentMandateGuard.py
# Expected SHA-256: 8e207b783f0a5b50c119c7ff28477b3bf9bc02ef95f71afea0b1a35688cf29a1
```

## Key Hardening Validated in v3.0

1. **Address Normalization (`_addr_to_hex`)**: Handles `Address` objects (`as_hex`), integer representations passed by Studio Dev UI forms, and mixed-case hex strings consistently so `principal`, `operator`, and `executor` checks never fail due to representation drift.
2. **Unescaped JSON Payload Quote Grounding (`_build_searchable_sources`)**: Grounding checks inspect both the canonical JSON string and the decoded inner `payload` object, allowing LLM validators to cite unescaped inner fields (e.g. `"maxSlippageBps":25`) without false downgrades.
3. **Heterogeneous LLM Consensus Stability**: `normalize_assessments` accepts valid extra metadata fields from diverse validator models while enforcing verbatim quote grounding before any `PASS + solid` authorization is granted.
4. **Deadline-Split Settlement & Execution Receipts**: `get_ticket_schedule` cleanly separates `can_redeem` and `can_sweep` at `expires_at`, while `record_execution_receipt` anchors downstream execution hashes on-chain.
