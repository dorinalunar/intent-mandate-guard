"""Pytest bootstrap: deterministic GenVM stub for IntentMandateGuard v3.0."""

from __future__ import annotations

import sys
import types
from pathlib import Path


def _install_fake_genlayer() -> None:
    existing = sys.modules.get("genlayer")
    if existing is not None and getattr(existing, "_fake_mandate_vm", False):
        return

    gl = types.ModuleType("genlayer")
    gl._fake_mandate_vm = True

    class _Write:
        def __call__(self, fn):
            fn._payable = False
            return fn

    class _Public:
        write = _Write()

        @staticmethod
        def view(fn):
            return fn

    class TreeMap(dict):
        def __class_getitem__(cls, item):
            return cls

    class Address:
        def __init__(self, value):
            if isinstance(value, Address):
                self.as_hex = value.as_hex
            elif isinstance(value, int):
                self.as_hex = "0x" + format(value, "040x")
            else:
                s = str(value).strip()
                if s.isdigit():
                    self.as_hex = "0x" + format(int(s), "040x")
                else:
                    self.as_hex = s.lower()

        def __str__(self):
            return f"Address({self.as_hex})"

        def __eq__(self, other):
            if isinstance(other, Address):
                return self.as_hex.lower() == other.as_hex.lower()
            return False

    class _Contract:
        def __new__(cls, *args, **kwargs):
            obj = super().__new__(cls)
            for name, kind in getattr(cls, "__annotations__", {}).items():
                label = kind if isinstance(kind, str) else getattr(kind, "__name__", "")
                if label.startswith("TreeMap"):
                    setattr(obj, name, TreeMap())
            return obj

    class UserError(Exception):
        def __init__(self, message=""):
            super().__init__(message)
            self.message = message

    class Return:
        def __init__(self, calldata):
            self.calldata = calldata

    _VM = types.SimpleNamespace(UserError=UserError, Return=Return)

    def _run_nondet_unsafe(leader_fn, validator_fn):
        leader_out = leader_fn()
        if getattr(gl, "validator_disagrees", False):
            raise UserError("[CONSENSUS] Validator check rejected leader assessments")
        if not validator_fn(Return(leader_out)):
            raise UserError("[CONSENSUS] Validator check failed")
        return leader_out
    _VM.run_nondet_unsafe = _run_nondet_unsafe

    def _exec_prompt(prompt, response_format=None):
        gl.prompts.append(prompt)
        if getattr(gl, "validator_queue", None):
            reply = gl.validator_queue.pop(0)
        else:
            reply = gl.llm_reply
        if isinstance(reply, Exception):
            raise reply
        return reply

    gl.Contract = _Contract
    gl.contract = types.SimpleNamespace(Contract=_Contract)
    gl.vm = _VM
    gl.public = _Public()
    gl.nondet = types.SimpleNamespace(exec_prompt=_exec_prompt)
    gl.message = types.SimpleNamespace(
        sender_address=Address("0x38409cca5f5ca70f3fe189638a87862318b478dd"),
        contract_address=Address("0xcb45206f7162bfc5427df038f750b1f3705e0c5a"),
        chain_id=61997,
        timestamp=1_795_122_437,
    )
    gl.Address = Address
    gl.TreeMap = TreeMap
    gl.u256 = int
    gl.gl = gl
    gl.__all__ = ["gl", "Address", "TreeMap", "u256"]

    gl.clock = 1_795_122_437
    gl.llm_reply = {
        "assessments": [
            {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": '"maxSlippageBps":25'},
            {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "USDC"},
        ]
    }
    gl.validator_queue = []
    gl.validator_disagrees = False
    gl.prompts = []
    sys.modules["genlayer"] = gl


def load_contract(repo_root: Path):
    _install_fake_genlayer()
    gl = sys.modules["genlayer"]
    path = repo_root / "contracts" / "IntentMandateGuard.py"
    mod_name = "contract_IntentMandateGuard"
    module = types.ModuleType(mod_name)
    module.__dict__["gl"] = gl
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)

    real_datetime = module.__dict__["datetime"]

    class _TxDatetime(real_datetime):  # type: ignore[misc, valid-type]
        @classmethod
        def now(cls, tz=None):
            return real_datetime.fromtimestamp(gl.clock, tz)

    module.__dict__["datetime"] = _TxDatetime
    sys.modules[mod_name] = module
    return module


def reset(gl) -> None:
    gl.clock = 1_795_122_437
    gl.message.timestamp = gl.clock
    gl.message.sender_address = gl.Address("0x38409cca5f5ca70f3fe189638a87862318b478dd")
    gl.message.contract_address = gl.Address("0xcb45206f7162bfc5427df038f750b1f3705e0c5a")
    gl.message.chain_id = 61997
    gl.llm_reply = {
        "assessments": [
            {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": '"maxSlippageBps":25'},
            {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "USDC"},
        ]
    }
    gl.validator_queue = []
    gl.validator_disagrees = False
    gl.prompts = []


def advance(gl, seconds: int) -> None:
    gl.clock += int(seconds)
    gl.message.timestamp = gl.clock
                  
