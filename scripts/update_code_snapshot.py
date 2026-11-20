#!/usr/bin/env python3
"""Compute / verify IntentMandateGuard CODE_SNAPSHOT.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "CODE_SNAPSHOT.json"
CONTRACT_PATH = ROOT / "contracts" / "IntentMandateGuard.py"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def git_head() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL)
            .decode()
            .strip()
            .lower()
        )
    except Exception:
        return sha256_text("IntentMandateGuard/v3.0-milestone-hardening")[:40]


def build_snapshot(commit: str | None = None) -> dict:
    c = (commit or git_head()).lower()
    contract_hash = sha256_bytes(CONTRACT_PATH.read_bytes())
    return {
        "commit": c,
        "evidence_hash": sha256_text(c),
        "evidence_hash_algo": "sha256(git_rev_parse_HEAD)",
        "contract_hash": contract_hash,
        "contract_hash_algo": "sha256(contracts/IntentMandateGuard.py)",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "note": "IntentMandateGuard v3.0 deployment snapshot (0xcB45206f7162BFc5427Df038F750B1F3705e0c5a)",
    }


def write_snapshot(path: Path = SNAPSHOT_PATH) -> dict:
    snap = build_snapshot()
    path.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    return snap


def verify_snapshot(path: Path = SNAPSHOT_PATH) -> None:
    if not path.exists():
        raise SystemExit(f"missing {path}")
    pinned = json.loads(path.read_text(encoding="utf-8"))
    live_contract = sha256_bytes(CONTRACT_PATH.read_bytes())
    errors = []
    commit = str(pinned.get("commit", "")).lower()
    expected_eh = sha256_text(commit)
    if pinned.get("evidence_hash") != expected_eh:
        errors.append("evidence_hash must equal sha256(snapshot.commit)")
    if pinned.get("contract_hash") != live_contract:
        errors.append("contract_hash drift — contracts/IntentMandateGuard.py changed")
    if errors:
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        raise SystemExit(1)
    print("CODE SNAPSHOT OK")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["update", "verify", "print"])
    args = p.parse_args()
    if args.command == "update":
        print(json.dumps(write_snapshot(), indent=2))
    elif args.command == "verify":
        verify_snapshot()
    else:
        print(json.dumps(build_snapshot(), indent=2))


if __name__ == "__main__":
    main()
