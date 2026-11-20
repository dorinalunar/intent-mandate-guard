#!/usr/bin/env python3
"""Build / validate IntentMandateGuard canonical intent & receipt payloads."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def validate_intent(data: dict) -> dict:
    if not isinstance(data, dict) or set(data.keys()) != {"method", "target", "payload"}:
        raise ValueError("intent must contain method, target, and payload keys only")
    for k in ("method", "target", "payload"):
        if not isinstance(data[k], str) or not data[k].strip():
            raise ValueError(f"{k} must be a non-empty string")
    norm = {k: data[k].strip() for k in ("method", "target", "payload")}
    canon = canonical_json(norm)
    return {
        "intent": norm,
        "canonical_json": canon,
        "intent_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
    }


def example_intent() -> dict:
    return {
        "method": "exactInputSingle",
        "target": "uniswap-v3-router.eth",
        "payload": json.dumps(
            {"tokenIn": "USDC", "tokenOut": "WETH", "amount": 2500, "maxSlippageBps": 25},
            separators=(",", ":"),
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate")
    g.add_argument("-o", "--out", type=Path, default=ROOT / "artifacts" / "ticket_attestation.json")

    v = sub.add_parser("validate")
    v.add_argument("path", type=Path)

    args = p.parse_args()
    if args.cmd == "generate":
        payload = example_intent()
        parsed = validate_intent(payload)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, "intent_sha256": parsed["intent_sha256"], "path": str(args.out)}, indent=2))
    else:
        raw = json.loads(args.path.read_text(encoding="utf-8"))
        parsed = validate_intent(raw)
        print(json.dumps({"ok": True, **parsed}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
  
