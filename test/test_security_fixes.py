"""v3.1 fixes: consensus binds the authorization bit, rule text is not evidence, the default
chain id is Studio Dev, the per-mandate ticket index is O(1) per ticket, and the execution
adapter refuses bad input before burning a ticket and waits for finality before acting."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import load_contract, reset  # noqa: E402

mod = load_contract(ROOT)
gl = sys.modules["genlayer"]
UserError = gl.vm.UserError

sys.path.insert(0, str(ROOT / "contracts"))
sys.path.insert(0, str(ROOT))
from ExecutionAdapter import ExecutionAdapterError, IntentExecutionAdapter  # noqa: E402

PRINCIPAL = "0x38409cca5f5ca70f3fe189638a87862318b478dd"
OPERATOR = "0x1111111111111111111111111111111111111111"
EXECUTOR = "0x2222222222222222222222222222222222222222"
STRANGER = "0x9999999999999999999999999999999999999999"

RULES = json.dumps([
    "Maximum slippage tolerance must not exceed 50 bps.",
    "Only USDC to WETH swaps on approved routers are permitted.",
])
METHODS = json.dumps(["exactInputSingle", "multicall"])
TARGET = "uniswap-v3-router.eth"
METHOD = "exactInputSingle"
PAYLOAD = json.dumps({"tokenIn": "USDC", "tokenOut": "WETH", "amount": 2500, "maxSlippageBps": 25}, separators=(",", ":"))
VALID_INTENT = json.dumps({"method": METHOD, "target": TARGET, "payload": PAYLOAD}, separators=(",", ":"))

SOLID = {
    "assessments": [
        {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": '"maxSlippageBps":25'},
        {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": '"tokenIn":"USDC"'},
    ]
}


@pytest.fixture(autouse=True)
def _fresh():
    reset(gl)
    yield


def as_addr(addr: str):
    gl.message.sender_address = gl.Address(addr)


def make_mandate(c, tx_cap=20):
    as_addr(PRINCIPAL)
    return c.register_mandate(gl.Address(OPERATOR), gl.Address(EXECUTOR), RULES, METHODS, 50000, tx_cap, 3600)


def issue(c, mid, nonce=1):
    as_addr(OPERATOR)
    return c.issue_ticket(mid, nonce, VALID_INTENT, 1000, 300)


# -- consensus binds what decides authorization --

def test_v31_01_validator_with_moderate_certainty_disagrees_with_solid_leader():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    moderate = json.loads(json.dumps(SOLID))
    moderate["assessments"][0]["certainty"] = "moderate"
    gl.validator_queue = [SOLID, moderate]
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="Validator check failed"):
        c.issue_ticket(mid, 1, VALID_INTENT, 1000, 300)


def test_v31_02_validator_with_ungrounded_quote_disagrees_with_grounded_leader():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    ungrounded = json.loads(json.dumps(SOLID))
    ungrounded["assessments"][1]["quote"] = "a quote that appears nowhere in the intent"
    gl.validator_queue = [SOLID, ungrounded]
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="Validator check failed"):
        c.issue_ticket(mid, 1, VALID_INTENT, 1000, 300)


def test_v31_03_both_moderate_agree_and_ticket_is_denied():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    moderate = json.loads(json.dumps(SOLID))
    moderate["assessments"][0]["certainty"] = "moderate"
    gl.validator_queue = [moderate, json.loads(json.dumps(moderate))]
    tid = issue(c, mid)
    assert c.get_ticket(tid)["state"] == "DENIED"
    assert c.get_mandate(mid)["locked_quota"] == 0


def test_v31_04_rule_text_never_grounds_a_quote():
    assert mod.quote_grounded_in_source(
        "must not exceed 50 bps", '{"method":"x","payload":"{}","target":"y"}', ["must not exceed 50 bps"], {}
    ) is False


# -- anchor and bookkeeping --

def test_v31_05_anchor_defaults_to_studio_dev_chain_id():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    del gl.message.chain_id
    try:
        tid = issue(c, mid)
    finally:
        gl.message.chain_id = 61997
    assert c.get_ticket(tid)["anchor"]["chain_id"] == 61997


def test_v31_06_mandate_ticket_index_pages_in_order_without_a_json_list():
    c = mod.IntentMandateGuard()
    m1 = make_mandate(c, tx_cap=50)
    m2 = make_mandate(c, tx_cap=50)
    ids_m1 = []
    for n in range(1, 13):
        ids_m1.append(issue(c, m1, n))
        issue(c, m2, n)
    assert not hasattr(c, "mandate_ticket_ids")
    page1 = c.list_mandate_tickets(m1, 0, 5)
    page3 = c.list_mandate_tickets(m1, 10, 5)
    assert page1["total"] == 12 and [t["id"] for t in page1["items"]] == ids_m1[:5]
    assert [t["id"] for t in page3["items"]] == ids_m1[10:] and page3["has_more"] is False


def test_v31_07_swept_by_is_stored_as_hex():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    tid = issue(c, mid)
    gl.message.timestamp = gl.message.timestamp + 10_000
    as_addr(STRANGER)
    c.sweep_expired_ticket(tid)
    assert c.get_ticket(tid)["swept_by"] == STRANGER


# -- execution adapter --

class _Guard:
    """Calls the contract as the executor, like a wallet-bound client would."""

    def __init__(self, contract):
        self.c = contract

    def get_ticket(self, tid):
        return self.c.get_ticket(tid)

    def redeem_ticket(self, tid, intent_json):
        as_addr(EXECUTOR)
        return self.c.redeem_ticket(tid, intent_json)


def _ready():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    tid = issue(c, mid)
    return c, tid


def test_v31_08_padded_target_is_refused_before_the_ticket_is_burned():
    c, tid = _ready()
    adapter = IntentExecutionAdapter(_Guard(c), wait_for_finality=lambda _t: True)
    with pytest.raises(ExecutionAdapterError, match="whitespace"):
        adapter.consume_and_execute(tid, TARGET + " ", METHOD, PAYLOAD)
    assert c.get_ticket(tid)["state"] == "ACTIVE"


def test_v31_09_adapter_refuses_to_run_without_a_finality_waiter():
    c, tid = _ready()
    adapter = IntentExecutionAdapter(_Guard(c))
    with pytest.raises(ExecutionAdapterError, match="finality"):
        adapter.consume_and_execute(tid, TARGET, METHOD, PAYLOAD)
    assert c.get_ticket(tid)["state"] == "ACTIVE"


def test_v31_10_unfinalized_redemption_dispatches_nothing():
    c, tid = _ready()
    calls = []
    adapter = IntentExecutionAdapter(_Guard(c), wait_for_finality=lambda _t: False)
    with pytest.raises(ExecutionAdapterError, match="not finalized"):
        adapter.consume_and_execute(tid, TARGET, METHOD, PAYLOAD, action_handler=lambda *a: calls.append(a))
    assert calls == []


def test_v31_11_finalized_redemption_dispatches_exact_calldata_once():
    c, tid = _ready()
    calls = []
    adapter = IntentExecutionAdapter(_Guard(c), wait_for_finality=lambda _t: True)
    record = adapter.consume_and_execute(
        tid, TARGET, METHOD, PAYLOAD, action_handler=lambda t, m, cd: calls.append(cd) or {"ok": True}
    )
    assert record["proof_verified"] is True and record["state_after"] == "REDEEMED"
    assert len(calls) == 1 and json.loads(calls[0])["params"]["maxSlippageBps"] == 25
