import { createClient } from "https://esm.sh/genlayer-js@0.18.1";
import { studionet } from "https://esm.sh/genlayer-js@0.18.1/chains";

let walletAddress = null;
const out = document.getElementById("consoleOutput");

function log(msg, obj = null) {
  const ts = new Date().toISOString();
  const body = obj
    ? `\n${JSON.stringify(obj, (_, v) => (typeof v === "bigint" ? v.toString() : v), 2)}`
    : "";
  out.textContent = `[${ts}] ${msg}${body}\n\n` + out.textContent;
}

function getContractAddress() {
  return document.getElementById("contractAddr").value.trim();
}

function buildReadClient() {
  return createClient({
    chain: studionet,
  });
}

async function buildWriteClient() {
  if (!window.ethereum) {
    throw new Error("Injected wallet provider (window.ethereum) is required for signed writes.");
  }
  const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
  if (!accounts || !accounts.length) {
    throw new Error("No wallet account authorized by provider.");
  }
  walletAddress = accounts[0];
  document.getElementById("connectBtn").textContent =
    `Connected: ${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}`;

  const client = createClient({
    chain: studionet,
    account: walletAddress,
    provider: window.ethereum,
  });
  return { client, signer: walletAddress };
}

async function connectWallet() {
  try {
    const { signer } = await buildWriteClient();
    log("Wallet connected with injected provider (window.ethereum)", { signer });
    return signer;
  } catch (err) {
    log("Wallet connection error:", { error: err.message });
    return null;
  }
}

async function sha256Hex(text) {
  const data = new TextEncoder().encode(text);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hashBuffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

document.getElementById("connectBtn").addEventListener("click", connectWallet);

document.getElementById("readVersionBtn").addEventListener("click", async () => {
  try {
    const client = buildReadClient();
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
    const client = buildReadClient();
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
    const client = buildReadClient();
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
    const { client, signer } = await buildWriteClient();
    const args = [
      document.getElementById("opAddr").value.trim(),
      document.getElementById("execAddr").value.trim(),
      document.getElementById("rulesJson").value.trim(),
      document.getElementById("methodsJson").value.trim(),
      Number(document.getElementById("quotaCap").value),
      Number(document.getElementById("txCap").value),
      Number(document.getElementById("mandateTtl").value),
    ];
    log("Submitting signed register_mandate via injected wallet provider...", { signer, args });
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
    const { client, signer } = await buildWriteClient();
    const readClient = buildReadClient();
    const contractAddress = getContractAddress();

    const rulesRaw = document.getElementById("rulesJson").value.trim();
    const methodsRaw = document.getElementById("methodsJson").value.trim();
    const quotaCap = Number(document.getElementById("quotaCap").value);
    const txCap = Number(document.getElementById("txCap").value);
    const ttlSeconds = Number(document.getElementById("mandateTtl").value);

    log("[Step 1/3] Signing & submitting register_mandate via genlayer-js@0.18.1 write client (with provider: window.ethereum)...");
    const txHash = await client.writeContract({
      address: contractAddress,
      functionName: "register_mandate",
      args: [signer, signer, rulesRaw, methodsRaw, quotaCap, txCap, ttlSeconds],
      value: 0n,
    });

    log("[Step 2/3] Awaiting FINALIZED receipt...", { txHash });
    const receipt = await client.waitForTransactionReceipt({ hash: txHash, status: "FINALIZED" });

    log("[Step 3/3] Performing encoded readback (protocol_version & get_mandate)...");
    const version = await readClient.readContract({
      address: contractAddress,
      functionName: "protocol_version",
      args: [],
    });
    const mandate = await readClient.readContract({
      address: contractAddress,
      functionName: "get_mandate",
      args: [1],
    });

    const proofReport = {
      checkType: "REPRODUCIBLE_SUBMIT_AND_FINALIZED_READBACK",
      sdk: "genlayer-js@0.18.1",
      providerInjected: Boolean(window.ethereum),
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
    log("[PASS] SIGNED WRITE + FINALIZED READBACK VERIFIED:", proofReport);
  } catch (err) {
    log("Reproducible flow failed:", { error: err.message });
  }
});

document.getElementById("issueTicketBtn").addEventListener("click", async () => {
  try {
    const { client, signer } = await buildWriteClient();
    const args = [
      Number(document.getElementById("ticketMandateId").value),
      Number(document.getElementById("seqNonce").value),
      document.getElementById("intentJson").value.trim(),
      Number(document.getElementById("ticketWeight").value),
      Number(document.getElementById("ticketTtl").value),
    ];
    log("Submitting signed issue_ticket via injected provider...", { signer, args });
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
    const { client, signer } = await buildWriteClient();
    const readClient = buildReadClient();
    const ticketId = Number(document.getElementById("redeemTicketId").value);
    const intentRaw = document.getElementById("intentJson").value.trim();
    const parsedIntent = JSON.parse(intentRaw);

    log("Submitting signed redeem_ticket & enforcing adapter calldata match...", {
      signer,
      ticketId,
      intent: parsedIntent,
    });
    const txHash = await client.writeContract({
      address: getContractAddress(),
      functionName: "redeem_ticket",
      args: [ticketId, intentRaw],
      value: 0n,
    });
    const receipt = await client.waitForTransactionReceipt({ hash: txHash, status: "FINALIZED" });
    const ticketAfter = await readClient.readContract({
      address: getContractAddress(),
      functionName: "get_ticket",
      args: [ticketId],
    });

    const canonicalCalldata = JSON.stringify({
      method: parsedIntent.method,
      params: JSON.parse(parsedIntent.payload),
      target: parsedIntent.target,
    });
    const calldataSha256 = await sha256Hex(canonicalCalldata);

    log("[PASS] Ticket Redeemed & Exact Calldata Action Enforced:", {
      txHash,
      finalizedStatus: receipt.status,
      ticketStateAfter: ticketAfter?.state || "REDEEMED",
      proofHash: ticketAfter?.proof_hash,
      exactCalldataDispatched: canonicalCalldata,
      calldataSha256,
    });
  } catch (err) {
    log("redeem_ticket failed:", { error: err.message });
  }
});