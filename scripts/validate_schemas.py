#!/usr/bin/env python3
"""Validate CODE_SNAPSHOT.json and intent_ticket fixtures against JSON Schemas."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(instance: dict, schema: dict, label: str) -> list[str]:
    errors: list[str] = []
    for key in schema.get("required", []):
        if key not in instance:
            errors.append(f"{label}: missing required field '{key}'")
    props = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        for key in instance:
            if key not in props:
                errors.append(f"{label}: unexpected field '{key}'")
    for key, rules in props.items():
        if key not in instance:
            continue
        val = instance[key]
        if rules.get("type") == "string" and not isinstance(val, str):
            errors.append(f"{label}.{key}: expected string")
            continue
        if "const" in rules and val != rules["const"]:
            errors.append(f"{label}.{key}: expected const {rules['const']!r}")
        if "pattern" in rules and isinstance(val, str) and not re.match(rules["pattern"], val):
            errors.append(f"{label}.{key}: does not match {rules['pattern']}")
        if "minLength" in rules and isinstance(val, str) and len(val) < rules["minLength"]:
            errors.append(f"{label}.{key}: shorter than minLength")
    return errors


def main() -> None:
    snap = _load(ROOT / "CODE_SNAPSHOT.json")
    snap_schema = _load(ROOT / "schemas" / "code_snapshot.schema.json")
    errors = _validate(snap, snap_schema, "CODE_SNAPSHOT")

    tmpl = _load(ROOT / "templates" / "ticket_attestation.json")
    intent_schema = _load(ROOT / "schemas" / "intent_ticket.schema.json")
    errors.extend(_validate(tmpl["example"], intent_schema, "ticket_attestation.example"))

    commit = str(snap.get("commit", ""))
    expected = hashlib.sha256(commit.encode("utf-8")).hexdigest()
    if snap.get("evidence_hash") != expected:
        errors.append("CODE_SNAPSHOT.evidence_hash != sha256(commit)")

    if errors:
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        raise SystemExit(1)
    print("SCHEMA CHECK OK (CODE_SNAPSHOT + intent_ticket)")


if __name__ == "__main__":
    main()
