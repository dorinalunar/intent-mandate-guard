"""Core lifecycle, role gating, address normalization, and receipt tests (24 tests)."""

import json
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
HASH_64 = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
TX_REF = "0x0a687de7d4ddcecd0a3c02a83a29972ba42af15931b6709886e57fc6a611d2c5"


@pytest.fixture(autouse=True)
def _fresh():
    reset(gl)
    yield


def as_addr(addr: str):
    gl.message.sender_address = gl.Address(addr)


def make_mandate(c, op=OPERATOR, ex=EXECUTOR, quota=50000, tx_cap=10, ttl=3600):
    as_addr(PRINCIPAL)
    return c.register_mandate(gl.Address(op), gl.Address(ex), RULES, METHODS, quota, tx_cap, ttl)


def test_01_protocol_version_tag():
    c = mod.IntentMandateGuard()
    assert c.protocol_version() == "IntentMandateGuard/v3.1"


def test_02_initial_stats_are_zeroed():
    c = mod.IntentMandateGuard()
    s = c.get_stats()
    assert s["mandates_count"] == 0 and s["tickets_count"] == 0 and s["total_locked_quota"] == 0


def test_03_register_mandate_stores_normalized_addresses():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    assert mid == 1
    m = c.get_mandate(1)
    assert m["principal"] == PRINCIPAL
    assert m["operator"] == OPERATOR
    assert m["executor"] == EXECUTOR
    assert m["quota_cap"] == 50000 and m["tx_cap"] == 10


def test_04_register_mandate_accepts_decimal_int_addresses_from_studio():
    c = mod.IntentMandateGuard()
    as_addr(PRINCIPAL)
    dec_principal = int(PRINCIPAL, 16)
    mid = c.register_mandate(dec_principal, dec_principal, RULES, METHODS, 50000, 10, 3600)
    m = c.get_mandate(mid)
    assert m["operator"] == PRINCIPAL and m["executor"] == PRINCIPAL


def test_05_register_mandate_rejects_zero_operator_or_executor():
    c = mod.IntentMandateGuard()
    as_addr(PRINCIPAL)
    zero = "0x" + "00" * 20
    with pytest.raises(UserError, match="zero address"):
        c.register_mandate(gl.Address(zero), gl.Address(EXECUTOR), RULES, METHODS, 1000, 5, 600)
    with pytest.raises(UserError, match="zero address"):
        c.register_mandate(gl.Address(OPERATOR), gl.Address(zero), RULES, METHODS, 1000, 5, 600)


@pytest.mark.parametrize("bad_rules", ["[]", json.dumps(["r"] * 7), json.dumps([""]), "not-json"])
def test_06_register_mandate_validates_rules_boundaries(bad_rules):
    c = mod.IntentMandateGuard()
    as_addr(PRINCIPAL)
    with pytest.raises(UserError):
        c.register_mandate(gl.Address(OPERATOR), gl.Address(EXECUTOR), bad_rules, METHODS, 1000, 5, 600)


@pytest.mark.parametrize("bad_methods", ["[]", json.dumps(["m"] * 9), json.dumps(["dup", "dup"]), json.dumps([""])])
def test_07_register_mandate_validates_method_allowlist(bad_methods):
    c = mod.IntentMandateGuard()
    as_addr(PRINCIPAL)
    with pytest.raises(UserError):
        c.register_mandate(gl.Address(OPERATOR), gl.Address(EXECUTOR), RULES, bad_methods, 1000, 5, 600)


@pytest.mark.parametrize("quota,tx_cap,ttl", [(0, 5, 600), (1000, 0, 600), (1000, 1000001, 600), (1000, 5, 59), (1000, 5, 2592001)])
def test_08_register_mandate_validates_caps_and_ttl(quota, tx_cap, ttl):
    c = mod.IntentMandateGuard()
    as_addr(PRINCIPAL)
    with pytest.raises(UserError):
        c.register_mandate(gl.Address(OPERATOR), gl.Address(EXECUTOR), RULES, METHODS, quota, tx_cap, ttl)


def test_09_issue_ticket_happy_path_locks_quota_and_creates_audit():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    assert tid == 1
    t = c.get_ticket(1)
    assert t["state"] == "ACTIVE" and t["weight"] == 2500
    assert len(t["proof_hash"]) == 64
    m = c.get_mandate(mid)
    assert m["locked_quota"] == 2500 and m["locked_txs"] == 1
    audit = c.get_audit_round(1)
    assert audit["approved"] is True and audit["rules_count"] == 2


def test_10_issue_ticket_only_authorized_operator():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    for who in (PRINCIPAL, EXECUTOR, STRANGER):
        as_addr(who)
        with pytest.raises(UserError, match="authorized operator"):
            c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)


def test_11_issue_ticket_rejects_reused_nonce():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    with pytest.raises(UserError, match="Sequence nonce already consumed"):
        c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)


def test_12_issue_ticket_allows_same_nonce_on_different_mandates():
    c = mod.IntentMandateGuard()
    m1 = make_mandate(c)
    m2 = make_mandate(c)
    as_addr(OPERATOR)
    assert c.issue_ticket(m1, 1, VALID_INTENT, 1000, 600) == 1
    assert c.issue_ticket(m2, 1, VALID_INTENT, 1000, 600) == 2


def test_13_issue_ticket_rejects_disallowed_method():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    bad_intent = json.dumps({"method": "approve", "target": "usdc.eth", "payload": "{}"})
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="allowlist"):
        c.issue_ticket(mid, 1, bad_intent, 1000, 600)


def test_14_issue_ticket_rejects_quota_or_tx_cap_overflow():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c, quota=3000, tx_cap=1)
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="exhausted"):
        c.issue_ticket(mid, 1, VALID_INTENT, 3001, 600)
    c.issue_ticket(mid, 1, VALID_INTENT, 1000, 600)
    with pytest.raises(UserError, match="exhausted"):
        c.issue_ticket(mid, 2, VALID_INTENT, 1000, 600)


def test_15_redeem_ticket_happy_path_moves_locked_to_used_quota():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    as_addr(EXECUTOR)
    out = c.redeem_ticket(tid, VALID_INTENT)
    assert out["weight"] == 2500 and len(out["proof_hash"]) == 64
    t = c.get_ticket(tid)
    assert t["state"] == "REDEEMED"
    m = c.get_mandate(mid)
    assert m["locked_quota"] == 0 and m["used_quota"] == 2500
    assert m["locked_txs"] == 0 and m["used_txs"] == 1


def test_16_redeem_ticket_rejects_payload_tampering():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    tampered = json.dumps({
        "method": "exactInputSingle",
        "target": "uniswap-v3-router.eth",
        "payload": json.dumps({"tokenIn": "USDC", "tokenOut": "WETH", "amount": 9999, "maxSlippageBps": 25}, separators=(",", ":")),
    })
    as_addr(EXECUTOR)
    with pytest.raises(UserError, match="cryptographic anchor"):
        c.redeem_ticket(tid, tampered)


def test_17_redeem_ticket_only_designated_executor():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    for who in (PRINCIPAL, OPERATOR, STRANGER):
        as_addr(who)
        with pytest.raises(UserError, match="designated executor"):
            c.redeem_ticket(tid, VALID_INTENT)


def test_18_redeem_ticket_cannot_be_redeemed_twice():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    as_addr(EXECUTOR)
    c.redeem_ticket(tid, VALID_INTENT)
    with pytest.raises(UserError, match="not eligible"):
        c.redeem_ticket(tid, VALID_INTENT)


def test_19_record_execution_receipt_happy_path_by_executor_or_operator():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    as_addr(EXECUTOR)
    c.redeem_ticket(tid, VALID_INTENT)
    rec = c.record_execution_receipt(tid, "0x" + HASH_64, TX_REF)
    assert rec["calldata_sha256"] == HASH_64 and rec["external_tx_ref"] == TX_REF
    assert c.get_execution_receipt(tid)["ticket_id"] == tid
    assert c.get_stats()["receipts_count"] == 1


def test_20_record_execution_receipt_rejects_unredeemed_duplicate_or_stranger():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    as_addr(EXECUTOR)
    with pytest.raises(UserError, match="REDEEMED"):
        c.record_execution_receipt(tid, HASH_64, TX_REF)
    c.redeem_ticket(tid, VALID_INTENT)
    as_addr(STRANGER)
    with pytest.raises(UserError, match="authorized executor or operator"):
        c.record_execution_receipt(tid, HASH_64, TX_REF)
    as_addr(OPERATOR)
    c.record_execution_receipt(tid, HASH_64, TX_REF)
    with pytest.raises(UserError, match="already recorded"):
        c.record_execution_receipt(tid, HASH_64, TX_REF)


def test_21_record_execution_receipt_validates_sha256_format():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    as_addr(EXECUTOR)
    c.redeem_ticket(tid, VALID_INTENT)
    with pytest.raises(UserError, match="64 hex"):
        c.record_execution_receipt(tid, "not-a-hash", TX_REF)
    with pytest.raises(UserError, match="transaction reference"):
        c.record_execution_receipt(tid, HASH_64, "   ")


def test_22_cancel_reservation_releases_quota_before_expiry():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    as_addr(STRANGER)
    with pytest.raises(UserError, match="principal or operator"):
        c.cancel_reservation(tid)
    as_addr(PRINCIPAL)
    c.cancel_reservation(tid)
    assert c.get_ticket(tid)["state"] == "RELEASED"
    assert c.get_mandate(mid)["locked_quota"] == 0


def test_23_terminate_mandate_blocks_new_tickets_and_enables_sweep():
    c = mod.IntentMandateGuard()
    mid = make_mandate(c)
    as_addr(OPERATOR)
    tid = c.issue_ticket(mid, 1, VALID_INTENT, 2500, 600)
    as_addr(STRANGER)
    with pytest.raises(UserError, match="principal"):
        c.terminate_mandate(mid)
    as_addr(PRINCIPAL)
    c.terminate_mandate(mid)
    as_addr(OPERATOR)
    with pytest.raises(UserError, match="terminated or expired"):
        c.issue_ticket(mid, 2, VALID_INTENT, 1000, 600)
    as_addr(STRANGER)
    swept = c.sweep_expired_ticket(tid)
    assert swept["state"] == "EXPIRED" and swept["released_quota"] == 2500


def test_24_missing_ids_raise_clean_user_errors():
    c = mod.IntentMandateGuard()
    with pytest.raises(UserError, match="Mandate ID not found"):
        c.get_mandate(999)
    with pytest.raises(UserError, match="Ticket ID not found"):
        c.get_ticket(999)
    with pytest.raises(UserError, match="Audit round not found"):
        c.get_audit_round(999)
    with pytest.raises(UserError, match="Execution receipt not found"):
        c.get_execution_receipt(999)
