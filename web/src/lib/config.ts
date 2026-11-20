export const CHAIN_ID = 61997;
export const RPC_URL = "https://studio-dev.genlayer.com/api";
export const STUDIO_URL =
  "https://studio-dev.genlayer.com/?import-contract=0xACA0da3b7b6CC25d8B65040f325F98603beAD072";
export const EXPLORER_BASE = "https://explorer-studio-dev.genlayer.com";

export const CONTRACT_ADDRESS = "0xACA0da3b7b6CC25d8B65040f325F98603beAD072";
export const EXPLORER = `${EXPLORER_BASE}/address/${CONTRACT_ADDRESS}`;
export const GITHUB = "https://github.com/dorinalunar/intent-mandate-guard";

export const DEFAULT_OPERATOR = "0x38409cca5f5ca70f3fe189638a87862318b478dd";
export const DEFAULT_EXECUTOR = "0x38409cca5f5ca70f3fe189638a87862318b478dd";

export const DEPLOY_TX =
  "0xab2461e23b7243a21ad85a9e1ebb992d864db8a6986ce8d3028bdb746263a299";
export const CALL_TX_1 =
  "0xe1b424e54ccdab4e1721c6a5f17de7f36060a7247f83c38ec49116007ff8cfd4";
export const CALL_TX_2 =
  "0x0a687de7d4ddcecd0a3c02a83a29972ba42af15931b6709886e57fc6a611d2c5";

export function txUrl(hash: string): string {
  return hash ? `${EXPLORER_BASE}/tx/${hash}` : EXPLORER;
}
