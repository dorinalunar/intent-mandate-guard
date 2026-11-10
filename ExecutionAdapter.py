"""ExecutionAdapter: repository-source downstream execution adapter for IntentMandateGuard.

Consumes ACTIVE single-use tickets via IntentMandateGuard.redeem_ticket(), cryptographically
verifies that the redeemed payload matches the exact target, method, and calldata to be
dispatched, and records verifiable external action enforcement.
"""
import hashlib
import json
from IntentMandateGuard import PROTOCOL_TAG, to_canonical_json, parse_intent_payload


class ExecutionAdapterError(Exception):
    """Raised when ticket redemption or payload-to-action verification fails."""


def build_canonical_calldata(target: str, method: str, payload_str: str) -> str:
    """Constructs the exact deterministic calldata envelope dispatched to the target."""
    parsed_payload = json.loads(payload_str)
    envelope = {
        "target": target.strip(),
        "method": method.strip(),
        "params": parsed_payload,
    }
    return to_canonical_json(envelope)


class IntentExecutionAdapter:
    """Downstream execution adapter that enforces 1:1 equivalence between a redeemed
    IntentMandateGuard ticket and the external action / calldata performed.
    """

    def __init__(self, guard_contract, chain_id: int = 61999, contract_address: str = ""):
        self.guard = guard_contract
        self.chain_id = int(chain_id)
        self.contract_address = str(contract_address)
        self.executed_actions = []
        self.consumed_proofs = set()

    def consume_and_execute(
        self,
        ticket_id: int,
        target: str,
        method: str,
        calldata_payload: str,
        action_handler=None,
    ) -> dict:
        """1. Packages the proposed external action into a canonical intent JSON.
        2. Consumes the ticket on IntentMandateGuard via redeem_ticket().
        3. Proves the redeemed payload and SHA-256 proof_hash match the exact action.
        4. Executes the external effect and logs the verifiable execution receipt.
        """
        proposed_intent = {
            "method": method,
            "target": target,
            "payload": calldata_payload,
        }
        intent_json = to_canonical_json(proposed_intent)

        # Validate structure before redemption
        validated_intent = parse_intent_payload(intent_json)

        # Fetch pre-redemption ticket state to verify anchor metadata
        ticket_before = self.guard.get_ticket(ticket_id)

        # Consume the ticket on-chain (reverts if not executor, not ACTIVE, expired, or mismatched)
        redemption = self.guard.redeem_ticket(ticket_id, intent_json)

        proof_hash = redemption.get("proof_hash")
        redeemed_intent = redemption.get("intent")
        redeemed_weight = redemption.get("weight")

        if not proof_hash or proof_hash in self.consumed_proofs:
            raise ExecutionAdapterError("[ADAPTER_HALT] Missing or already-consumed proof hash")

        # Prove that the redeemed intent is identical to the external action parameters
        if redeemed_intent != validated_intent:
            raise ExecutionAdapterError(
                "[ADAPTER_HALT] Redeemed intent does not match external action payload"
            )

        if (
            redeemed_intent["target"] != target
            or redeemed_intent["method"] != method
            or redeemed_intent["payload"] != calldata_payload
        ):
            raise ExecutionAdapterError(
                "[ADAPTER_HALT] Field-level mismatch between redeemed ticket and target calldata"
            )

        # Recompute cryptographic anchor hash independently to prove anchor integrity
        expected_anchor = {
            "protocol": PROTOCOL_TAG,
            "chain_id": int(ticket_before["anchor"]["chain_id"]),
            "contract": str(ticket_before["anchor"]["contract"]),
            "mandate_id": int(ticket_before["mandate_id"]),
            "seq_nonce": int(ticket_before["seq_nonce"]),
            "executor": str(ticket_before["anchor"]["executor"]),
            "weight": int(redeemed_weight),
            "intent": validated_intent,
        }
        recomputed_proof = hashlib.sha256(
            to_canonical_json(expected_anchor).encode("utf-8")
        ).hexdigest()

        if recomputed_proof != proof_hash:
            raise ExecutionAdapterError(
                "[ADAPTER_HALT] Cryptographic proof_hash verification failed"
            )

        # Construct exact deterministic calldata and dispatch external action
        exact_calldata = build_canonical_calldata(target, method, calldata_payload)
        calldata_sha256 = hashlib.sha256(exact_calldata.encode("utf-8")).hexdigest()

        external_output = (
            action_handler(target, method, exact_calldata)
            if callable(action_handler)
            else {"dispatched": True, "calldata": exact_calldata}
        )

        self.consumed_proofs.add(proof_hash)

        execution_record = {
            "ticket_id": int(ticket_id),
            "mandate_id": int(ticket_before["mandate_id"]),
            "state_after": self.guard.get_ticket(ticket_id)["state"],
            "proof_hash": proof_hash,
            "recomputed_proof_hash": recomputed_proof,
            "proof_verified": True,
            "target": target,
            "method": method,
            "payload": calldata_payload,
            "exact_calldata": exact_calldata,
            "calldata_sha256": calldata_sha256,
            "weight_consumed": int(redeemed_weight),
            "external_effect": external_output,
        }
        self.executed_actions.append(execution_record)
        return execution_record
