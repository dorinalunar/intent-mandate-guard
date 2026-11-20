# GenLayer Studio Dev Operator Guide

* **Live Contract (`v3.0`):** [`0xcB45206f7162BFc5427Df038F750B1F3705e0c5a`](https://explorer-studio-dev.genlayer.com/address/0xcB45206f7162BFc5427Df038F750B1F3705e0c5a)
* **Studio URL:** https://studio-dev.genlayer.com/run-debug

## Quick Run Checklist

1. **Register Mandate (`register_mandate`)**:
   * `operator`: `0x38409cca5f5ca70f3fe189638a87862318b478dd`
   * `executor`: `0x38409cca5f5ca70f3fe189638a87862318b478dd`
   * `rules_json`: `["Maximum slippage tolerance must not exceed 50 bps.", "Only USDC to WETH swaps on approved routers are permitted."]`
   * `methods_json`: `["exactInputSingle", "multicall"]`
   * `quota_cap`: `50000`, `tx_cap`: `10`, `ttl_seconds`: `3600`
2. **Issue Ticket (`issue_ticket`)**:
   * `mandate_id`: `1`, `seq_nonce`: `1`, `weight`: `2500`, `ttl_seconds`: `600`
   * `intent_json`: `{"method":"exactInputSingle","target":"uniswap-v3-router.eth","payload":"{\"tokenIn\":\"USDC\",\"tokenOut\":\"WETH\",\"amount\":2500,\"maxSlippageBps\":25}"}`
3. **Redeem Ticket (`redeem_ticket`)**:
   * `ticket_id`: `1`, `intent_json`: exact same canonical intent JSON
4. **Record Receipt (`record_execution_receipt`)**:
   * `ticket_id`: `1`, `calldata_sha256`: 64-char hex digest, `external_tx_ref`: downstream tx hash
5. **Sweep Expired Ticket (`sweep_expired_ticket`)**:
   * Permissionless cleanup once `expires_at` is reached or `terminate_mandate` is called
