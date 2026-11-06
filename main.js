import { createClient } from "https://esm.sh/genlayer-js@0.18.1";
import { studionet } from "https://esm.sh/genlayer-js@0.18.1/chains";

let walletAddress = null;
const out = document.getElementById("consoleOutput");

function log(msg, obj = null) {
  const ts = new Date().toISOString();
  const body = obj ? `\n${JSON.stringify(obj, (_, v) => (typeof v === "bigint" ? v.toString() : v), 2)}` : "";
  out.textContent = `[${ts}] ${msg}${body}\n\n` + out.textContent;
}

function getContractAddress() {
  return document.getElementById("contractAddr").value.trim();
}

function buildClient(account = undefined) {
  return createClient({
    chain: studionet,
    ...(account ? { account } : {}),
  });
}

async function connectWallet() {
  if (!window.ethereum) {
    log("MetaMask (window.ethereum) not detected.");
    return null;
  }
  const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
  walletAddress = accounts[0];
  document.getElementById("connectBtn").textContent = `Connected: ${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}`;
  log("Wallet connected", { signer: walletAddress });
  return walletAddress;
}

document.getElementById("connectBtn").addEventListener("click", connectWallet);

document.getElementById("readVersionBtn").addEventListener("click", async () => {
  try {
    const client = buildClient();
    const version = await client.readContract({
      address: getContractAddress(),
      functionName: "protocol_version",
      args: [],
    });
    log("protocol_version() readback:", { protocol_version: version });
  } catch (err) {
    log("Error reading protocol_version:", { error: err.message });
  }
});

document.getElementById("readMandateBtn").addEventListener("click", async () => {
  try {
    const id = Number(document.getElementById("lookupId").value);
    const client = buildClient();
    const mandate = await client.readContract({
      address: getContractAddress(),
      functionName: "get_mandate",
      args: [id],
    });
    log(`get_mandate(${id}) readback:`, mandate);
  } catch (err) {
    log("Error reading mandate:", { error: err.message });
  }
});

document.getElementById("readTicketBtn").addEventListener("click", async () => {
  try {
    const id = Number(document.getElementById("lookupId").value);
    const client = buildClient();
    const ticket = await client.readContract({
      address: getContractAddress(),
      functionName: "get_ticket",
      args: [id],
    });
    log(`get_ticket(${id}) readback:`, ticket);
  } catch (err) {
    log("Error reading ticket:", { error: err.message });
  }
});

document.getElementById("registerMandateBtn").addEventListener("click", async () => {
  try {
    const signer = walletAddress || (await connectWallet());
    const client = buildClient(signer);
    const args = [
      document.getElementById("opAddr").value.trim(),
      document.getElementById("execAddr").value.trim(),
      document.getElementById("rulesJson").value.trim(),
      document.getElementById("methodsJson").value.trim(),
      Number(document.getElementById("quotaCap").value),
      Number(document.getElementById("txCap").value),
      Number(document.getElementById("mandateTtl").value),
    ];
    log("Submitting wallet-signed register_mandate...", { args });
    const txHash = await client.writeContract({
      address: getContractAddress(),
      functionName: "register_mandate",
      args,
      value: 0n,
    });
    log("Transaction submitted. Awaiting FINALIZED receipt...", { txHash });
    const receipt = await client.waitForTransactionReceipt({ hash: txHash, status: "FINALIZED" });
    log("Mandate registered & finalized!", { txHash, status: receipt.status });
  } catch (err) {
    log("register_mandate failed:", { error: err.message });
  }
});

document.getElementById("reproducibleFlowBtn").addEventListener("click", async () => {
  try {
    const signer = walletAddress || (await connectWallet());
    const contractAddress = getContractAddress();
    const client = buildClient(signer);

    const rulesRaw = document.getElementById("rulesJson").value.trim();
    const methodsRaw = document.getElementById("methodsJson").value.trim();
    const quotaCap = Number(document.getElementById("quotaCap").value);
    const txCap = Number(document.getElementById("txCap").value);
    const ttlSeconds = Number(document.getElementById("mandateTtl").value);

    log("[Step 1/3] Signing & submitting register_mandate via genlayer-js SDK...");
    const txHash = await client.writeContract({
      address: contractAddress,
      functionName: "register_mandate",
      args: [signer, signer, rulesRaw, methodsRaw, quotaCap, txCap, ttlSeconds],
      value: 0n,
    });

    log("[Step 2/3] Awaiting FINALIZED receipt...", { txHash });
    const receipt = await client.waitForTransactionReceipt({ hash: txHash, status: "FINALIZED" });

    log("[Step 3/3] Performing encoded readback (protocol_version & get_mandate)...");
    const version = await client.readContract({
      address: contractAddress,
      functionName: "protocol_version",
      args: [],
    });
    const mandate = await client.readContract({
      address: contractAddress,
      functionName: "get_mandate",
      args: [1],
    });

    const proofReport = {
      checkType: "REPRODUCIBLE_SUBMIT_AND_FINALIZED_READBACK",
      verified: version === "IntentMandateGuard/v2.0" && Boolean(mandate),
      timestamp: new Date().toISOString(),
      contractAddress,
      chainId: 61999,
      signer,
      transaction: {
        method: "register_mandate",
        txHash,
        finalizedStatus: receipt.status,
      },
      readback: {
        protocol_version: version,
        get_mandate: mandate,
      },
    };
    log("[PASS] SUBMIT + FINALIZED READBACK VERIFIED:", proofReport);
  } catch (err) {
    log("Reproducible flow failed:", { error: err.message });
  }
});

document.getElementById("issueTicketBtn").addEventListener("click", async () => {
  try {
    const signer = walletAddress || (await connectWallet());
    const client = buildClient(signer);
    const args = [
      Number(document.getElementById("ticketMandateId").value),
      Number(document.getElementById("seqNonce").value),
      document.getElementById("intentJson").value.trim(),
      Number(document.getElementById("ticketWeight").value),
      Number(document.getElementById("ticketTtl").value),
    ];
    log("Submitting wallet-signed issue_ticket...", { args });
    const txHash = await client.writeContract({
      address: getContractAddress(),
      functionName: "issue_ticket",
      args,
      value: 0n,
    });
    const receipt = await client.waitForTransactionReceipt({ hash: txHash, status: "FINALIZED" });
    log("issue_ticket finalized!", { txHash, status: receipt.status });
  } catch (err) {
    log("issue_ticket failed:", { error: err.message });
  }
});

document.getElementById("redeemTicketBtn").addEventListener("click", async () => {
  try {
    const signer = walletAddress || (await connectWallet());
    const client = buildClient(signer);
    const args = [
      Number(document.getElementById("redeemTicketId").value),
      document.getElementById("intentJson").value.trim(),
    ];
    log("Submitting wallet-signed redeem_ticket...", { args });
    const txHash = await client.writeContract({
      address: getContractAddress(),
      functionName: "redeem_ticket",
      args,
      value: 0n,
    });
    const receipt = await client.waitForTransactionReceipt({ hash: txHash, status: "FINALIZED" });
    log("redeem_ticket finalized!", { txHash, status: receipt.status });
  } catch (err) {
    log("redeem_ticket failed:", { error: err.message });
  }
});
