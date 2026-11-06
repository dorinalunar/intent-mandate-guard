import json
from pathlib import Path
import sys
import types
import pytest


def _install_genlayer_mock():
    if "genlayer" in sys.modules:
        return

    mock_gl = types.ModuleType("genlayer")

    class _UserError(Exception):
        pass

    class _Return:
        def __init__(self, calldata):
            self.calldata = calldata

    class _VM:
        UserError = _UserError
        Return = _Return

        @staticmethod
        def run_nondet_unsafe(leader_fn, validator_fn):
            result = leader_fn()
            wrapped = _Return(result)
            if not validator_fn(wrapped):
                raise _UserError("Validator rejected leader assessment")
            return result

    class _Nondet:
        _mock_response = None

        @classmethod
        def exec_prompt(cls, prompt_text: str, response_format: str = "json"):
            if callable(cls._mock_response):
                return cls._mock_response(prompt_text)
            if cls._mock_response is not None:
                return cls._mock_response
            raise _UserError("No mock LLM response configured")

    class _PublicProxy:
        def write(self, fn):
            return fn

        def view(self, fn):
            return fn

    class Address(str):
        pass

    class _Message:
        sender_address = Address("0x1111111111111111111111111111111111111111")
        contract_address = Address("0x2222222222222222222222222222222222222222")
        chain_id = 61999

    class _Contract:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            orig_init = cls.__init__

            def _wrapped_init(self, *args, **kw):
                for attr in getattr(cls, "__annotations__", {}):
                    setattr(self, attr, {})
                orig_init(self, *args, **kw)

            cls.__init__ = _wrapped_init

    class _TreeMapMeta(type):
        def __getitem__(cls, item):
            return dict

    class TreeMap(dict, metaclass=_TreeMapMeta):
        pass

    mock_gl.vm = _VM
    mock_gl.nondet = _Nondet
    mock_gl.public = _PublicProxy()
    mock_gl.message = _Message
    mock_gl.Contract = _Contract
    mock_gl.Address = Address
    mock_gl.TreeMap = TreeMap
    mock_gl.u256 = int
    mock_gl.gl = mock_gl
    mock_gl.__all__ = ["gl", "Address", "TreeMap", "u256"]

    sys.modules["genlayer"] = mock_gl


_install_genlayer_mock()

import genlayer as gl_mod  # noqa: E402
from IntentMandateGuard import (  # noqa: E402
    PROTOCOL_TAG,
    IntentMandateGuard,
    normalize_assessments,
    parse_intent_payload,
)

PRINCIPAL_ADDR = gl_mod.Address("0x1111111111111111111111111111111111111111")
OPERATOR_ADDR = gl_mod.Address("0x38409cCa5f5ca70F3fe189638a87862318b478dd")
EXECUTOR_ADDR = gl_mod.Address("0x9999999999999999999999999999999999999999")
STRANGER_ADDR = gl_mod.Address("0x7777777777777777777777777777777777777777")


def sample_rules() -> list:
    return [
        "Swap slippage must not exceed 50 bps (0.5%).",
        "Target protocol must be an approved Uniswap v3 router.",
    ]


def sample_methods() -> list:
    return ["exactInputSingle", "multicall"]


def sample_intent() -> dict:
    return {
        "method": "exactInputSingle",
        "target": "uniswap-v3-router.eth",
        "payload": '{"tokenIn":"USDC","tokenOut":"WETH","amount":2500,"maxSlippageBps":30}',
    }


def test_protocol_version_and_intent_parser():
    contract = IntentMandateGuard()
    assert contract.protocol_version() == PROTOCOL_TAG

    parsed = parse_intent_payload(json.dumps(sample_intent()))
    assert parsed["method"] == "exactInputSingle"

    with pytest.raises(gl_mod.gl.vm.UserError, match="method, target, and payload keys only"):
        parse_intent_payload('{"method":"swap","target":"router"}')


def test_normalize_assessments_ordering_and_bounds():
    raw = {
        "assessments": [
            {"index": 1, "outcome": "PASS", "certainty": "solid"},
            {"index": 0, "outcome": "PASS", "certainty": "solid"},
        ]
    }
    ordered = normalize_assessments(raw, 2)
    assert ordered[0]["index"] == 0
    assert ordered[1]["index"] == 1

    with pytest.raises(gl_mod.gl.vm.UserError, match="Duplicate or out-of-bounds"):
        normalize_assessments(
            {
                "assessments": [
                    {"index": 0, "outcome": "PASS", "certainty": "solid"},
                    {"index": 0, "outcome": "PASS", "certainty": "solid"},
                ]
            },
            2,
        )


def test_full_lifecycle_register_issue_and_redeem():
    contract = IntentMandateGuard()
    gl_mod.gl.message.sender_address = PRINCIPAL_ADDR

    mandate_id = contract.register_mandate(
        OPERATOR_ADDR,
        EXECUTOR_ADDR,
        json.dumps(sample_rules()),
        json.dumps(sample_methods()),
        10000,
        5,
        3600,
    )
    assert mandate_id == 1

    gl_mod.gl.message.sender_address = OPERATOR_ADDR
    gl_mod.gl.nondet._mock_response = {
        "assessments": [
            {"index": 0, "outcome": "PASS", "certainty": "solid"},
            {"index": 1, "outcome": "PASS", "certainty": "solid"},
        ]
    }

    intent_str = json.dumps(sample_intent())
    ticket_id = contract.issue_ticket(mandate_id, 101, intent_str, 2500, 600)
    assert ticket_id == 1

    mandate_after_issue = contract.get_mandate(mandate_id)
    assert mandate_after_issue["locked_quota"] == 2500
    assert mandate_after_issue["locked_txs"] == 1

    ticket = contract.get_ticket(ticket_id)
    assert ticket["state"] == "ACTIVE"

    gl_mod.gl.message.sender_address = EXECUTOR_ADDR
    receipt = contract.redeem_ticket(ticket_id, intent_str)
    assert receipt["proof_hash"] == ticket["proof_hash"]
    assert receipt["weight"] == 2500

    mandate_after_redeem = contract.get_mandate(mandate_id)
    assert mandate_after_redeem["locked_quota"] == 0
    assert mandate_after_redeem["used_quota"] == 2500
    assert mandate_after_redeem["used_txs"] == 1
    assert contract.get_ticket(ticket_id)["state"] == "REDEEMED"


def test_denied_ticket_does_not_lock_quota():
    contract = IntentMandateGuard()
    gl_mod.gl.message.sender_address = PRINCIPAL_ADDR
    mandate_id = contract.register_mandate(
        OPERATOR_ADDR,
        EXECUTOR_ADDR,
        json.dumps(sample_rules()),
        json.dumps(sample_methods()),
        10000,
        5,
        3600,
    )

    gl_mod.gl.message.sender_address = OPERATOR_ADDR
    gl_mod.gl.nondet._mock_response = {
        "assessments": [
            {"index": 0, "outcome": "FAIL", "certainty": "solid"},
            {"index": 1, "outcome": "PASS", "certainty": "solid"},
        ]
    }

    ticket_id = contract.issue_ticket(mandate_id, 202, json.dumps(sample_intent()), 4000, 600)
    assert contract.get_ticket(ticket_id)["state"] == "DENIED"
    assert contract.get_mandate(mandate_id)["locked_quota"] == 0


def test_cancel_reservation_and_terminate_mandate():
    contract = IntentMandateGuard()
    gl_mod.gl.message.sender_address = PRINCIPAL_ADDR
    mandate_id = contract.register_mandate(
        OPERATOR_ADDR,
        EXECUTOR_ADDR,
        json.dumps(sample_rules()),
        json.dumps(sample_methods()),
        10000,
        5,
        3600,
    )

    gl_mod.gl.message.sender_address = OPERATOR_ADDR
    gl_mod.gl.nondet._mock_response = {
        "assessments": [
            {"index": 0, "outcome": "PASS", "certainty": "solid"},
            {"index": 1, "outcome": "PASS", "certainty": "solid"},
        ]
    }
    ticket_id = contract.issue_ticket(mandate_id, 303, json.dumps(sample_intent()), 3000, 600)

    gl_mod.gl.message.sender_address = STRANGER_ADDR
    with pytest.raises(gl_mod.gl.vm.UserError, match="Only principal or operator"):
        contract.cancel_reservation(ticket_id)

    gl_mod.gl.message.sender_address = PRINCIPAL_ADDR
    contract.cancel_reservation(ticket_id)
    assert contract.get_ticket(ticket_id)["state"] == "RELEASED"
    assert contract.get_mandate(mandate_id)["locked_quota"] == 0

    contract.terminate_mandate(mandate_id)
    assert contract.get_mandate(mandate_id)["terminated"] is True


def test_sample_dataset_json_scenarios():
    dataset_path = Path(__file__).parent / "sample_dataset.json"
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    assert dataset["protocol"] == PROTOCOL_TAG

    contract = IntentMandateGuard()
    for idx, scenario in enumerate(dataset["scenarios"], start=1):
        gl_mod.gl.message.sender_address = PRINCIPAL_ADDR
        mid = contract.register_mandate(
            OPERATOR_ADDR,
            EXECUTOR_ADDR,
            json.dumps(scenario["rules"]),
            json.dumps(scenario["methods"]),
            scenario["quota_cap"],
            scenario["tx_cap"],
            scenario["ttl_seconds"],
        )
        gl_mod.gl.message.sender_address = OPERATOR_ADDR
        gl_mod.gl.nondet._mock_response = {"assessments": scenario["mock_assessments"]}
        tid = contract.issue_ticket(
            mid,
            idx * 10,
            json.dumps(scenario["intent"]),
            scenario["weight"],
            600,
        )
        assert contract.get_ticket(tid)["state"] == scenario["expected_state"]
