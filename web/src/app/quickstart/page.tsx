"use client";

import { PageShell } from "@/components/SiteChrome";
import { CONTRACT_ADDRESS, DEFAULT_OPERATOR } from "@/lib/config";

export default function QuickstartPage() {
  return (
    <PageShell
      active="/quickstart/"
      title="Quickstart"
      lead="Run the full IntentMandateGuard v3.0 lifecycle on GenLayer Studio Dev (chain 61997)."
    >
      <pre className="code">{`// Live Contract: ${CONTRACT_ADDRESS}

1. register_mandate(
  operator="${DEFAULT_OPERATOR}",
  executor="${DEFAULT_OPERATOR}",
  rules_json='["Maximum slippage tolerance must not exceed 50 bps.", "Only USDC to WETH swaps on approved routers are permitted."]',
  methods_json='["exactInputSingle", "multicall"]',
  quota_cap=50000,
  tx_cap=10,
  ttl_seconds=3600
)

2. issue_ticket(
  mandate_id=1,
  seq_nonce=1,
  intent_json='{"method":"exactInputSingle","target":"uniswap-v3-router.eth","payload":"{\"tokenIn\":\"USDC\",\"tokenOut\":\"WETH\",\"amount\":2500,\"maxSlippageBps\":25}"}',
  weight=2500,
  ttl_seconds=600
)

3. redeem_ticket(ticket_id=1, intent_json=...)

4. record_execution_receipt(
  ticket_id=1,
  calldata_sha256="9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
  external_tx_ref="0x0a687de7d4ddcecd0a3c02a83a29972ba42af15931b6709886e57fc6a611d2c5"
)`}</pre>
    </PageShell>
  );
}
