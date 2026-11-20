"""v3.0 Hardening suite: verbatim quote grounding, consensus, deadlines, pagination & invariants (36 tests)."""

import json
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import advance, load_contract, reset  # noqa: E402

mod = load_contract(ROOT)
gl = sys.modules["genlayer"]
UserError = gl.vm.UserError

PRINCIPAL = "0x38409cca5f5ca70f3fe189638a87862318b478dd"
OPERATOR = "0x1111111111111111111111111111111111111111"
EXECUTOR = "0x2222222222222222222222222222222222222222"
STRANGER = "0x9999999999999999999999999999999999999999"

RULES = json.dumps([
    "Maximum slippage tolerance must not exceed 50 bps.",
    "Only USDC to WETH swaps on approved routers are permitted.",
])
METHODS = json.dumps(["exactInputSingle", "multicall"])
VALID_INTENT = json.dumps({
    "method": "exactInputSingle",
    "target": "uniswap-v3-router.eth",
    "payload": json.dumps({"tokenIn": "USDC", "tokenOut": "WETH", "amount": 2500, "maxSlippageBps": 25}, separators=(",", ":")),
}, separators=(",", ":"))


@pytest.fixture(autouse=True)
def _fresh():
    reset(gl)
    yield


def as_addr(addr: str):
    gl.message.sender_address = gl.Address(addr)


def make_mandate(c, quota=50000, tx_cap=20, ttl=3600):
    as_addr(PRINCIPAL)
    return c.register_mandate(gl.Address(OPERATOR), gl.Address(EXECUTOR), RULES, METHODS, quota, tx_cap, ttl)


# -- 1. Verbatim quote grounding & unescaped payload matching (10 tests) --


def test_25_quote_grounding_accepts_unescaped_inner_json_key_value():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    gl.llm_reply = {
        "assessments": [
            {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": '"maxSlippageBps":25'},
            {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": '"tokenIn":"USDC"'},
        ]
    }
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 300)
    t = c.get_ticket(tid)
    assert t["state"] == "ACTIVE"
    assert all(a["grounded"] is True for a in t["assessments"])


def test_26_quote_grounding_accepts_rule_text_excerpt():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    gl.llm_reply = {
        "assessments": [
            {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": "must not exceed 50 bps"},
            {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "uniswap-v3-router.eth"},
        ]
    }
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 300)
    assert c.get_ticket(tid)["state"] == "ACTIVE"


def test_27_fabricating_quote_downgrades_pass_solid_to_ambiguous_and_denies():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    gl.llm_reply = {
        "assessments": [
            {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": "hallucinated non-existent quote"},
            {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "USDC"},
        ]
    }
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 300)
    t = c.get_ticket(tid)
    assert t["state"] == "DENIED"
    assert t["assessments"][0]["outcome"] == "AMBIGUOUS"
    assert t["assessments"][0]["grounded"] is False
    assert c.get_mandate(mid)["locked_quota"] == 0


def test_28_moderate_certainty_with_grounded_quote_still_denies_ticket():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    gl.llm_reply = {
        "assessments": [
            {"index": 0, "outcome": "PASS", "certainty": "moderate", "quote": '"maxSlippageBps":25'},
            {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "USDC"},
        ]
    }
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 300)
    assert c.get_ticket(tid)["state"] == "DENIED"
    assert c.get_stats()["denied_tickets_count"] == 1


def test_29_explicit_fail_verdict_denies_ticket_without_locking_quota():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    gl.llm_reply = {
        "assessments": [
            {"index": 0, "outcome": "FAIL", "certainty": "solid", "quote": '"maxSlippageBps":25'},
            {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "USDC"},
        ]
    }
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 300)
    assert c.get_ticket(tid)["state"] == "DENIED"
    assert c.get_mandate(mid)["locked_quota"] == 0


def test_30_normalize_assessments_tolerates_extra_llm_keys():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    gl.llm_reply = {
        "assessments": [
            {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": '"maxSlippageBps":25', "reason": "within 50 bps"},
            {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "USDC", "confidence": 0.99},
        ]
    }
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 300)
    assert c.get_ticket(tid)["state"] == "ACTIVE"


def test_31_normalize_assessments_orders_out_of_order_rule_indices():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    gl.llm_reply = {
        "assessments": [
            {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "USDC"},
            {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": '"maxSlippageBps":25'},
        ]
    }
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 300)
    t = c.get_ticket(tid)
    assert [a["index"] for a in t["assessments"]] == [0, 1]


def test_32_normalize_assessments_rejects_duplicate_or_missing_indices():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    gl.llm_reply = {
        "assessments": [
            {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": "USDC"},
            {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": "USDC"},
        ]
    }
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="Duplicate or out-of-bounds"):
        c.issue_ticket(mid, 1, VALID_INTENT, 1000, 300)


def test_33_validator_consensus_accepts_different_quotes_with_same_outcome():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    gl.validator_queue = [
        {
            "assessments": [
                {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": '"maxSlippageBps":25'},
                {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "USDC"},
            ]
        },
        {
            "assessments": [
                {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": "exceed 50 bps"},
                {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "uniswap-v3-router.eth"},
            ]
        },
    ]
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 300)
    assert c.get_ticket(tid)["state"] == "ACTIVE"


def test_34_validator_consensus_rejects_conflicting_outcomes():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    gl.validator_queue = [
        {
            "assessments": [
                {"index": 0, "outcome": "PASS", "certainty": "solid", "quote": '"maxSlippageBps":25'},
                {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "USDC"},
            ]
        },
        {
            "assessments": [
                {"index": 0, "outcome": "FAIL", "certainty": "solid", "quote": '"maxSlippageBps":25'},
                {"index": 1, "outcome": "PASS", "certainty": "solid", "quote": "USDC"},
            ]
        },
    ]
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="Validator check failed"):
        c.issue_ticket(mid, 1, VALID_INTENT, 1000, 300)


# -- 2. Deadline-split settlement & sweep_expired_ticket (10 tests) --


def test_35_one_second_before_deadline_redeem_succeeds_and_sweep_fails():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 60)
    exp = c.get_ticket(tid)["expires_at"]
    gl.clock = exp - 1
    gl.message.timestamp = gl.clock
    sched = c.get_ticket_schedule(tid)
    assert sched["can_redeem"] is True and sched["can_sweep"] is False
    as_addr(STRANGER)
    with pytest.raises(UserError, match="not been reached"):
        c.sweep_expired_ticket(tid)
    as_addr(EXECUTOR)
    c.redeem_ticket(tid, VALID_INTENT)
    assert c.get_ticket(tid)["state"] == "REDEEMED"


def test_36_at_deadline_redeem_fails_and_permissionless_sweep_succeeds():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 60)
    exp = c.get_ticket(tid)["expires_at"]
    gl.clock = exp
    gl.message.timestamp = gl.clock
    sched = c.get_ticket_schedule(tid)
    assert sched["can_redeem"] is False and sched["can_sweep"] is True
    as_addr(EXECUTOR)
    with pytest.raises(UserError, match="sweep_expired_ticket"):
        c.redeem_ticket(tid, VALID_INTENT)
    as_addr(STRANGER)
    res = c.sweep_expired_ticket(tid)
    assert res["state"] == "EXPIRED" and res["released_quota"] == 1000
    assert c.get_mandate(mid)["locked_quota"] == 0


def test_37_schedule_never_offers_both_can_redeem_and_can_sweep():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 120)
    start = c.get_ticket(tid)["issued_at"]
    end = c.get_ticket(tid)["expires_at"]
    for t in range(start, end + 30, 15):
        gl.clock = t
        gl.message.timestamp = t
        s = c.get_ticket_schedule(tid)
        assert not (s["can_redeem"] and s["can_sweep"])


def test_38_ticket_expiry_is_clamped_to_parent_mandate_expiry():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c, ttl=120)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 3600)
    assert c.get_ticket(tid)["expires_at"] == c.get_mandate(mid)["expires_at"]


def test_39_sweep_expired_ticket_cannot_be_called_twice():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 60)
    advance(gl, 60)
    as_addr(STRANGER)
    c.sweep_expired_ticket(tid)
    with pytest.raises(UserError, match="Only ACTIVE tickets"):
        c.sweep_expired_ticket(tid)


def test_40_sweep_expired_ticket_rejects_redeemed_or_denied_tickets():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    t1 = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 60)
    as_addr(EXECUTOR)
    c.redeem_ticket(t1, VALID_INTENT)
    advance(gl, 100)
    with pytest.raises(UserError, match="Only ACTIVE tickets"):
        c.sweep_expired_ticket(t1)


def test_41_swept_quota_can_be_reused_by_subsequent_ticket():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c, quota=1000, tx_cap=1)
    as_addr(OPERATOR)
    t1 = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 60)
    advance(gl, 60)
    c.sweep_expired_ticket(t1)
    t2 = c.issue_ticket(mid, 2, VALID_INTENT, 1000, 60)
    assert c.get_ticket(t2)["state"] == "ACTIVE"


def test_42_cancelled_quota_can_be_reused_by_subsequent_ticket():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c, quota=1000, tx_cap=1)
    as_addr(OPERATOR)
    t1 = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 600)
    c.cancel_reservation(t1)
    t2 = c.issue_ticket(mid, 2, VALID_INTENT, 1000, 600)
    assert c.get_ticket(t2)["state"] == "ACTIVE"


def test_43_expired_mandate_refuses_new_tickets():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c, ttl=120)
    advance(gl, 120)
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="terminated or expired"):
        c.issue_ticket(mid, 1, VALID_INTENT, 1000, 60)


def test_44_stranger_can_cancel_reservation_after_deadline():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 60)
    advance(gl, 60)
    as_addr(STRANGER)
    c.cancel_reservation(tid)
    assert c.get_ticket(tid)["state"] == "RELEASED"


# -- 3. Pagination, input bounds, canonicalization & fuzz invariants (16 tests) --


def test_45_list_mandates_pagination():
    c = mod.IntentMandateGuard()
    for _ in range(5):
        make_mandate(c)
    p1 = c.list_mandates(0, 2)
    assert p1["total"] == 5 and len(p1["items"]) == 2 and p1["has_more"] is True
    p2 = c.list_mandates(4, 5)
    assert len(p2["items"]) == 1 and p2["has_more"] is False


def test_46_list_tickets_and_list_mandate_tickets_pagination():
    c = mod.IntentMandateGuard()
    m1 = make_mandate(c)
    m2 = make_mandate(c)
    as_addr(OPERATOR)
    c.issue_ticket(m1, 1, VALID_INTENT, 500, 300)
    c.issue_ticket(m2, 1, VALID_INTENT, 500, 300)
    c.issue_ticket(m1, 2, VALID_INTENT, 500, 300)
    all_t = c.list_tickets(0, 10)
    assert all_t["total"] == 3 and len(all_t["items"]) == 3
    m1_t = c.list_mandate_tickets(m1, 0, 10)
    assert m1_t["total"] == 2 and [x["id"] for x in m1_t["items"]] == [1, 3]


def test_47_page_limit_clamps_oversized_or_zero_requests():
    c = mod.IntentMandateGuard()
    make_mandate(c)
    assert c.list_mandates(0, 0)["limit"] == 20
    assert c.list_mandates(0, 9999)["limit"] == 100


def test_48_parse_intent_rejects_extra_or_missing_keys():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="method, target, and payload keys only"):
        c.issue_ticket(mid, 1, json.dumps({"method": "exactInputSingle", "target": "x"}), 100, 60)
    with pytest.raises(UserError, match="method, target, and payload keys only"):
        c.issue_ticket(mid, 1, json.dumps({"method": "exactInputSingle", "target": "x", "payload": "{}", "extra": 1}), 100, 60)


def test_49_parse_intent_rejects_oversized_payload():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    huge = json.dumps({"method": "exactInputSingle", "target": "x", "payload": "a" * 6001})
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="Invalid intent field boundaries"):
        c.issue_ticket(mid, 1, huge, 100, 60)


def test_50_ticket_ttl_bounds_enforced():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="Invalid ticket weight or TTL"):
        c.issue_ticket(mid, 1, VALID_INTENT, 100, 29)
    with pytest.raises(UserError, match="Invalid ticket weight or TTL"):
        c.issue_ticket(mid, 1, VALID_INTENT, 100, 86401)


def test_51_ticket_weight_zero_rejected():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="Invalid ticket weight or TTL"):
        c.issue_ticket(mid, 1, VALID_INTENT, 0, 60)


def test_52_redeem_accepts_reordered_json_keys_with_identical_canonical_intent():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    parsed = json.loads(VALID_INTENT)
    reordered = json.dumps({"payload": parsed["payload"], "target": parsed["target"], "method": parsed["method"]})
    as_addr(EXECUTOR)
    out = c.redeem_ticket(tid, reordered)
    assert out["weight"] == 2500


def test_53_proof_hash_binds_chain_id_contract_and_nonce():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    t1 = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 600)
    t2 = c.issue_ticket(mid, 2, VALID_INTENT, 1000, 600)
    assert c.get_ticket(t1)["proof_hash"] != c.get_ticket(t2)["proof_hash"]


def test_54_audit_round_records_sha256_and_evaluated_char_count():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 600)
    audit = c.get_audit_round(tid)
    assert len(audit["intent_sha256"]) == 64 and audit["chars_evaluated"] > 100


def test_55_global_stats_track_all_state_transitions():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c, quota=10000, tx_cap=10)
    as_addr(OPERATOR)
    t1 = c.issue_ticket(mid, 1, VALID_INTENT, 1000, 60)
    t2 = c.issue_ticket(mid, 2, VALID_INTENT, 2000, 60)
    t3 = c.issue_ticket(mid, 3, VALID_INTENT, 3000, 600)
    as_addr(EXECUTOR)
    c.redeem_ticket(t1, VALID_INTENT)
    c.record_execution_receipt(t1, "a" * 64, "0xtx1")
    as_addr(PRINCIPAL)
    c.cancel_reservation(t3)
    advance(gl, 65)
    as_addr(STRANGER)
    c.sweep_expired_ticket(t2)
    stats = c.get_stats()
    assert stats["active_tickets_count"] == 0
    assert stats["redeemed_tickets_count"] == 1
    assert stats["released_tickets_count"] == 1
    assert stats["expired_tickets_count"] == 1
    assert stats["receipts_count"] == 1
    assert stats["total_locked_quota"] == 0
    assert stats["total_used_quota"] == 1000


def test_56_invariant_helpers_detect_corrupted_quota():
    c = mod.IntentMandateGuard()
    with pytest.raises(UserError, match="INVARIANT_HALT"):
        c._assert_mandate_invariants({
            "locked_quota": 600,
            "used_quota": 500,
            "quota_cap": 1000,
            "locked_txs": 1,
            "used_txs": 0,
            "tx_cap": 5,
        })


def test_57_invariant_helpers_detect_corrupted_tx_cap():
    c = mod.IntentMandateGuard()
    with pytest.raises(UserError, match="INVARIANT_HALT"):
        c._assert_mandate_invariants({
            "locked_quota": 100,
            "used_quota": 100,
            "quota_cap": 1000,
            "locked_txs": 3,
            "used_txs": 3,
            "tx_cap": 5,
        })


def test_58_random_lifecycle_fuzz_preserves_quota_conservation():
    rng = random.Random(42)
    c = mod.IntentMandateGuard()
    mid = make_mandate(c, quota=20000, tx_cap=50, ttl=10000)
    active_ids = []
    for step in range(1, 35):
        action = rng.choice(["issue", "redeem", "cancel", "sweep"])
        if action == "issue":
            as_addr(OPERATOR)
            try:
                tid = c.issue_ticket(mid, step, VALID_INTENT, 500, 120)
                active_ids.append(tid)
            except UserError:
                pass
        elif action == "redeem" and active_ids:
            tid = rng.choice(active_ids)
            as_addr(EXECUTOR)
            try:
                c.redeem_ticket(tid, VALID_INTENT)
                active_ids.remove(tid)
            except UserError:
                pass
        elif action == "cancel" and active_ids:
            tid = rng.choice(active_ids)
            as_addr(PRINCIPAL)
            try:
                c.cancel_reservation(tid)
                active_ids.remove(tid)
            except UserError:
                pass
        elif action == "sweep" and active_ids:
            advance(gl, 130)
            tid = rng.choice(active_ids)
            as_addr(STRANGER)
            try:
                c.sweep_expired_ticket(tid)
                active_ids.remove(tid)
            except UserError:
                pass
        m = c.get_mandate(mid)
        s = c.get_stats()
        assert m["locked_quota"] + m["used_quota"] <= m["quota_cap"]
        assert m["locked_quota"] == s["total_locked_quota"]
        assert m["used_quota"] == s["total_used_quota"]


def test_59_addr_to_hex_handles_all_input_representations():
    assert mod._addr_to_hex(gl.Address(PRINCIPAL)) == PRINCIPAL
    assert mod._addr_to_hex(int(PRINCIPAL, 16)) == PRINCIPAL
    assert mod._addr_to_hex(str(int(PRINCIPAL, 16))) == PRINCIPAL
    assert mod._addr_to_hex(PRINCIPAL.upper()) == PRINCIPAL


def test_60_contract_source_uses_user_error_and_contains_no_bare_exceptions():
    src = (ROOT / "contracts" / "IntentMandateGuard.py").read_text(encoding="utf-8")
    assert "raise Exception" not in src
    assert src.count("gl.vm.UserError") >= 25
