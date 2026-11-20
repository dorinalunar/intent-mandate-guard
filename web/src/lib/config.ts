export const CHAIN_ID = 61997;
export const RPC_URL = "https://studio-dev.genlayer.com/api";
export const STUDIO_URL = "https://studio-dev.genlayer.com/run-debug";
export const EXPLORER_BASE = "https://explorer-studio-dev.genlayer.com";

export const CONTRACT_ADDRESS = "0xcB45206f7162BFc5427Df038F750B1F3705e0c5a";
export const EXPLORER = `${EXPLORER_BASE}/address/${CONTRACT_ADDRESS}`;
export const GITHUB = "https://github.com/dorinalunar/intent-mandate-guard";

export const DEFAULT_OPERATOR = "0x38409cca5f5ca70f3fe189638a87862318b478dd";
export const DEFAULT_EXECUTOR = "0x38409cca5f5ca70f3fe189638a87862318b478dd";

export const DEPLOY_TX = "0x6b88abc0bf8f373281f6d8bebd8c1291b7f163b5f641306914408bde48a3853c";
export const CALL_TX_1 = "0x94151a08f4a0bed67e2fd44ac44e26f9008fbad12aa14d51686d9364b52b5b28";
export const CALL_TX_2 = "0x62048c591d8e3814b006bfbe813a9f0a69c2d6833943c56f881d8b814967886d";

export function txUrl(hash: string): string {
  return hash ? `${EXPLORER_BASE}/tx/${hash}` : EXPLORER;
}
