#!/usr/bin/env python3
"""Verify deployed IntentMandateGuard v3.0 bytecode/source hash on Studio Dev."""

import base64
import hashlib
import json
import pathlib
import sys
import urllib.request

RPC = "https://studio-dev.genlayer.com/api"
ADDRESS = "0xcB45206f7162BFc5427Df038F750B1F3705e0c5a"
SOURCE = pathlib.Path(__file__).resolve().parents[1] / "contracts" / "IntentMandateGuard.py"


def on_chain_sha256() -> str:
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": "gen_getContractCode", "params": [ADDRESS]}
    ).encode()
    request = urllib.request.Request(
        RPC,
        data=payload,
        headers={"content-type": "application/json", "user-agent": "intentmandateguard-ci"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.load(response)
    if "result" not in body:
        raise SystemExit(f"RPC error: {body.get('error')}")
    return hashlib.sha256(base64.b64decode(body["result"])).hexdigest()


def main() -> int:
    local = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    remote = on_chain_sha256()
    print("local   ", local)
    print("on-chain", remote)
    return 0 if local == remote else 1


if __name__ == "__main__":
    sys.exit(main())
