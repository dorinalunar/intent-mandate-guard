# IntentMandateGuard v3.0 Demo Flow

Contract: `0xcB45206f7162BFc5427Df038F750B1F3705e0c5a` (GenLayer Studio Dev, chain `61997`)

```text
1. register_mandate(
     operator="0x38409cca5f5ca70f3fe189638a87862318b478dd",
     executor="0x38409cca5f5ca70f3fe189638a87862318b478dd",
     rules_json='["Maximum slippage tolerance must not exceed 50 bps.", "Only USDC to WETH swaps on approved routers are permitted."]',
     methods_json='["exactInputSingle", "multicall"]',
     quota_cap=50000,
     tx_cap=10,
     ttl_seconds=3600
   ) -> returns mandate_id = 1

2. issue_ticket(
     mandate_id=1,
     seq_nonce=1,
     intent_json='{"method":"exactInputSingle","target":"uniswap-v3-router.eth","payload":"{\"tokenIn\":\"USDC\",\"tokenOut\":\"WETH\",\"amount\":2500,\"maxSlippageBps\":25}"}',
     weight=2500,
     ttl_seconds=600
   ) -> returns ticket_id = 1 (state = ACTIVE)

3. redeem_ticket(
     ticket_id=1,
     intent_json='{"method":"exactInputSingle","target":"uniswap-v3-router.eth","payload":"{\"tokenIn\":\"USDC\",\"tokenOut\":\"WETH\",\"amount\":2500,\"maxSlippageBps\":25}"}'
   ) -> state = REDEEMED

4. record_execution_receipt(
     ticket_id=1,
     calldata_sha256="9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
     external_tx_ref="0x62048c591d8e3814b006bfbe813a9f0a69c2d6833943c56f881d8b814967886d"
   )
```
