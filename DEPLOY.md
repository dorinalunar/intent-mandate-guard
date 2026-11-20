# IntentMandateGuard v3.0 — Deployment Guide

## Live Studio Dev Instance

* **Network:** GenLayer Studio Dev (`chain 61997`)
* **RPC:** `https://studio-dev.genlayer.com/api`
* **Contract Address:** [`0xcB45206f7162BFc5427Df038F750B1F3705e0c5a`](https://explorer-studio-dev.genlayer.com/address/0xcB45206f7162BFc5427Df038F750B1F3705e0c5a)
* **Deploy Tx:** [`0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c`](https://explorer-studio-dev.genlayer.com/tx/0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c)
* **Creator:** `0x38409cca5f5ca70f3fe189638a87862318b478dd`

## Deploy Steps

1. Open [GenLayer Studio Dev](https://studio-dev.genlayer.com/run-debug) and connect your wallet on chain `61997`.
2. Load [`contracts/IntentMandateGuard.py`](contracts/IntentMandateGuard.py) (no constructor arguments required).
3. Click **Deploy** and wait for `FINALIZED` status.
4. Run the smoke flow from [`examples/demo_flow.md`](examples/demo_flow.md) or generate a call sheet via:
   ```bash
   python3 scripts/cli.py studio-calls
   ```
