#!/usr/bin/env python3
"""Assemble artifacts/integrity-pack.json for GenLayer stewards."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "integrity-pack.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    snap = json.loads((ROOT / "CODE_SNAPSHOT.json").read_text(encoding="utf-8"))
    pack = {
        "name": "IntentMandateGuard v3.0 Integrity Pack",
        "protocol": "IntentMandateGuard/v3.0",
        "contract_address": "0xACA0da3b7b6CC25d8B65040f325F98603beAD072",
        "deploy_tx": "0xab2461e23b7243a21ad85a9e1ebb992d864db8a6986ce8d3028bdb746263a299",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "files": {
            "CODE_SNAPSHOT.json": {
                "sha256": sha256_file(ROOT / "CODE_SNAPSHOT.json"),
                "content": snap,
            },
            "schemas/code_snapshot.schema.json": {
                "sha256": sha256_file(ROOT / "schemas" / "code_snapshot.schema.json"),
            },
            "schemas/intent_ticket.schema.json": {
                "sha256": sha256_file(ROOT / "schemas" / "intent_ticket.schema.json"),
            },
            "templates/ticket_attestation.json": {
                "sha256": sha256_file(ROOT / "templates" / "ticket_attestation.json"),
            },
            "contracts/IntentMandateGuard.py": {
                "sha256": sha256_file(ROOT / "contracts" / "IntentMandateGuard.py"),
            },
        },
        "checks": [
            "python3 scripts/update_code_snapshot.py verify",
            "python3 scripts/validate_schemas.py",
            "python3 -m pytest -v",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "path": str(OUT), "contract_hash": snap["contract_hash"]}, indent=2))


if __name__ == "__main__":
    main()
