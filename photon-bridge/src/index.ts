import { IMessageSDK } from "@photon-ai/imessage-kit";
import { handleMessage } from "./workflows.js";

const PHOTON_API_KEY = process.env.PHOTON_API_KEY || "";
const PHOTON_PHONE_NUMBER = process.env.PHOTON_PHONE_NUMBER || "";

async function main(): Promise<void> {
  console.log("🚀 Marketing Studio iMessage Bridge starting...");

  const sdk = new IMessageSDK({
    apiKey: PHOTON_API_KEY,
    phoneNumber: PHOTON_PHONE_NUMBER,
  });

  console.log("📱 Connecting to iMessage via Photon SDK...");
  await sdk.connect();
  console.log("✅ Connected! Listening for messages...");

  sdk.on("message", async (message: { sender: string; text: string; attachments?: Array<{ data: ArrayBuffer; filename: string }> }) => {
    const { sender, text } = message;

    if (!text || text.trim().length === 0) {
      return;
    }

    console.log(`[${sender}] → ${text.slice(0, 100)}`);

    try {
      const replies = await handleMessage(sender, text);

      for (const reply of replies) {
        await sdk.send(sender, reply);
        console.log(`[${sender}] ← ${reply.slice(0, 100)}${reply.length > 100 ? "..." : ""}`);
      }
    } catch (err) {
      console.error(`Error handling message from ${sender}:`, err);
      await sdk.send(
        sender,
        "⚠️ Something went wrong processing your request. Please try again."
      );
    }
  });

  process.on("SIGINT", async () => {
    console.log("\n🛑 Shutting down iMessage bridge...");
    await sdk.disconnect();
    process.exit(0);
  });

  process.on("SIGTERM", async () => {
    console.log("\n🛑 Shutting down iMessage bridge...");
    await sdk.disconnect();
    process.exit(0);
  });
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
