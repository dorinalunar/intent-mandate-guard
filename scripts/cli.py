#!/usr/bin/env python3
"""IntentMandateGuard v3.0 CLI — snapshot, intent attestation, and Studio call helper."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_evidence  # noqa: E402
import update_code_snapshot as snap  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(prog="intentmandateguard", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("snapshot")
    s.add_argument("action", choices=["update", "verify", "print"])

    e = sub.add_parser("intent")
    e.add_argument("action", choices=["generate", "validate"])
    e.add_argument("-o", "--out", default=str(ROOT / "artifacts" / "ticket_attestation.json"))
    e.add_argument("path", nargs="?", default=str(ROOT / "artifacts" / "ticket_attestation.json"))

    c = sub.add_parser("studio-calls")

    args = p.parse_args()
    if args.cmd == "snapshot":
        if args.action == "update":
            print(json.dumps(snap.write_snapshot(), indent=2))
        elif args.action == "verify":
            snap.verify_snapshot()
        else:
            print(json.dumps(snap.build_snapshot(), indent=2))
    elif args.cmd == "intent":
        if args.action == "generate":
            payload = build_evidence.example_intent()
            parsed = build_evidence.validate_intent(payload)
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"ok": True, **parsed}, indent=2))
        else:
            raw = json.loads(Path(args.path).read_text(encoding="utf-8"))
            print(json.dumps(build_evidence.validate_intent(raw), indent=2))
    else:
        intent_str = json.dumps(build_evidence.example_intent(), separators=(",", ":"))
        print(f"""# IntentMandateGuard v3.0 Studio Call Sheet
Contract: 0xACA0da3b7b6CC25d8B65040f325F98603beAD072

1) register_mandate(
     operator="0x38409cca5f5ca70f3fe189638a87862318b478dd",
     executor="0x38409cca5f5ca70f3fe189638a87862318b478dd",
     rules_json='["Maximum slippage tolerance must not exceed 50 bps.", "Only USDC to WETH swaps on approved routers are permitted."]',
     methods_json='["exactInputSingle", "multicall"]',
     quota_cap=50000,
     tx_cap=10,
     ttl_seconds=3600
   )
2) issue_ticket(
     mandate_id=1,
     seq_nonce=1,
     intent_json={json.dumps(intent_str)},
     weight=2500,
     ttl_seconds=600
   )
3) redeem_ticket(ticket_id=1, intent_json={json.dumps(intent_str)})
4) record_execution_receipt(
     ticket_id=1,
     calldata_sha256="9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
     external_tx_ref="0x62048c591d8e3814b006bfbe813a9f0a69c2d6833943c56f881d8b814967886d"
   )
""")


if __name__ == "__main__":
    main()
