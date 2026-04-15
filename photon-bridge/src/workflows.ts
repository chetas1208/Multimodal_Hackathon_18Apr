import {
  createUser,
  createJob,
  getJobStatus,
  getJobAssets,
  uploadFile,
} from "./api-client.js";

type WorkflowStep =
  | "idle"
  | "generate:waiting_url"
  | "generate:waiting_images"
  | "generate:waiting_text"
  | "generate:processing"
  | "clip:waiting_source"
  | "clip:processing";

interface ConversationState {
  step: WorkflowStep;
  backendUserId?: string;
  productUrl?: string;
  productImages: string[];
  productText?: string;
  clipSource?: { type: "url" | "file"; value: string };
  currentJobId?: string;
}

const conversations = new Map<string, ConversationState>();

function getState(sender: string): ConversationState {
  if (!conversations.has(sender)) {
    conversations.set(sender, { step: "idle", productImages: [] });
  }
  return conversations.get(sender)!;
}

function resetState(sender: string): void {
  conversations.set(sender, { step: "idle", productImages: [] });
}

const HELP_TEXT = [
  "🎬 Marketing Studio Bot (iMessage)",
  "━━━━━━━━━━━━━━━━━━━━━━━━",
  "",
  "Your AI-powered marketing studio, right here in iMessage.",
  "",
  "Commands:",
  "  /generate — Create a promotional video ad",
  "  /clip    — Turn a long video into short clips",
  "  /status  — Check job status",
  "  /cancel  — Cancel current workflow",
  "  /help    — Show this message",
  "",
  "Send /generate or /clip to get started!",
].join("\n");

async function ensureUser(
  state: ConversationState,
  sender: string
): Promise<string | null> {
  if (state.backendUserId) return state.backendUserId;

  const idNum = hashSender(sender);
  const result = await createUser(idNum, sender, sender.split("@")[0] || "iMessage User");
  if (result && typeof result.id === "string") {
    state.backendUserId = result.id;
    return result.id;
  }
  return null;
}

function hashSender(sender: string): number {
  let hash = 0;
  for (let i = 0; i < sender.length; i++) {
    hash = (hash * 31 + sender.charCodeAt(i)) | 0;
  }
  return Math.abs(hash);
}

async function pollJob(jobId: string): Promise<Record<string, unknown> | null> {
  const POLL_INTERVAL = 3000;
  const TIMEOUT = 120_000;
  let elapsed = 0;

  while (elapsed < TIMEOUT) {
    await new Promise((r) => setTimeout(r, POLL_INTERVAL));
    elapsed += POLL_INTERVAL;

    const status = await getJobStatus(jobId);
    if (!status) continue;

    if (status.status === "completed" || status.status === "failed") {
      return status as unknown as Record<string, unknown>;
    }
  }
  return await getJobStatus(jobId) as unknown as Record<string, unknown>;
}

export async function handleMessage(
  sender: string,
  text: string
): Promise<string[]> {
  const trimmed = text.trim();
  const state = getState(sender);

  if (trimmed === "/cancel") {
    resetState(sender);
    return ["❌ Workflow cancelled. Send /generate or /clip to start over."];
  }

  if (trimmed === "/help" || trimmed === "/start") {
    resetState(sender);
    return [HELP_TEXT];
  }

  if (trimmed.startsWith("/status")) {
    return await handleStatus(state, trimmed);
  }

  if (trimmed === "/generate") {
    state.step = "generate:waiting_url";
    state.productImages = [];
    state.productUrl = undefined;
    state.productText = undefined;
    return [
      "🛍️ Let's create a video ad!\n\nFirst, send me your product URL (e.g. a Shopify or Amazon link).",
    ];
  }

  if (trimmed === "/clip") {
    state.step = "clip:waiting_source";
    state.clipSource = undefined;
    return [
      "✂️ Let's clip your video into shorts!\n\nSend me a YouTube URL or describe where to find your video.",
    ];
  }

  switch (state.step) {
    case "generate:waiting_url":
      return handleGenerateUrl(state, trimmed);
    case "generate:waiting_images":
      return handleGenerateImages(state, trimmed);
    case "generate:waiting_text":
      return handleGenerateText(state, sender, trimmed);
    case "clip:waiting_source":
      return handleClipSource(state, sender, trimmed);
    default:
      return [HELP_TEXT];
  }
}

function handleGenerateUrl(state: ConversationState, text: string): string[] {
  if (!text.startsWith("http")) {
    return ["That doesn't look like a URL. Please send a link starting with http:// or https://."];
  }
  state.productUrl = text;
  state.step = "generate:waiting_images";
  return [
    "✅ Got your product URL!\n\n" +
      "Now send me product image URLs (one per message, up to 5).\n" +
      'When done, type "done" or send your product description directly.',
  ];
}

function handleGenerateImages(state: ConversationState, text: string): string[] {
  const lower = text.toLowerCase();
  if (lower === "done" || lower === "/done") {
    if (state.productImages.length === 0) {
      return ["You haven't sent any images yet. Send an image URL or type your product description to skip."];
    }
    state.step = "generate:waiting_text";
    return [
      `✅ ${state.productImages.length} image(s) received!\n\nNow describe your product in a few sentences.`,
    ];
  }

  if (text.startsWith("http")) {
    if (state.productImages.length >= 5) {
      state.step = "generate:waiting_text";
      return ["You've hit the 5-image max.\n\nNow describe your product in a few sentences."];
    }
    state.productImages.push(text);
    return [`📸 Image ${state.productImages.length}/5 received! Send more or type "done".`];
  }

  if (text.length >= 10) {
    state.step = "generate:waiting_text";
    return await_generate_text_inline(state, text);
  }

  return ['Send an image URL, type "done", or send your product description (10+ chars).'];
}

function await_generate_text_inline(state: ConversationState, text: string): string[] {
  state.productText = text;
  state.step = "generate:processing";
  return [
    `📋 Here's what I've got:\n` +
      `🔗 URL: ${state.productUrl}\n` +
      `🖼️ Images: ${state.productImages.length}\n` +
      `📝 Description: ${text.slice(0, 120)}${text.length > 120 ? "..." : ""}\n\n` +
      `⏳ Processing your video ad... This may take a few minutes.`,
  ];
}

async function handleGenerateText(
  state: ConversationState,
  sender: string,
  text: string
): Promise<string[]> {
  if (text.length < 10) {
    return ["Please provide a more detailed description (at least a couple of sentences)."];
  }

  state.productText = text;
  state.step = "generate:processing";

  const confirmMsg =
    `📋 Here's what I've got:\n` +
    `🔗 URL: ${state.productUrl}\n` +
    `🖼️ Images: ${state.productImages.length}\n` +
    `📝 Description: ${text.slice(0, 120)}${text.length > 120 ? "..." : ""}\n\n` +
    `⏳ Processing your video ad... This may take a few minutes.`;

  const userId = await ensureUser(state, sender);
  if (!userId) {
    resetState(sender);
    return [confirmMsg, "❌ Could not authenticate with the server. Please try /start again."];
  }

  const job = await createJob(userId, "generate_video", {
    product_url: state.productUrl,
    product_images: state.productImages,
    product_text: state.productText,
  });

  if (!job) {
    resetState(sender);
    return [confirmMsg, "❌ Failed to create the job. The server might be down."];
  }

  state.currentJobId = job.id;
  const result = await pollJob(job.id);
  resetState(sender);

  if (result && result.status === "completed") {
    return [confirmMsg, formatGenerateResults(result)];
  } else if (result && result.status === "failed") {
    return [confirmMsg, `❌ Job failed: ${result.error_message || "Unknown error"}`];
  }
  return [confirmMsg, `⏱️ Job is still processing. Check back with: /status ${job.id}`];
}

function formatGenerateResults(job: Record<string, unknown>): string {
  const output = (job.output_data as Record<string, unknown>) || {};
  const analysis = (output.analysis as Record<string, number>) || {};
  const lines = ["🎬 Your video ad is ready!"];

  const scores = [
    ["Hook", analysis.hook_score],
    ["CTA", analysis.cta_score],
    ["Pacing", analysis.pacing_score],
    ["Platform Fit", analysis.platform_fit_score],
    ["Engagement", analysis.engagement_score],
  ];

  const hasScores = scores.some(([, v]) => v !== undefined);
  if (hasScores) {
    lines.push("\n📊 Analysis Scores:");
    for (const [label, val] of scores) {
      if (val !== undefined) {
        const n = Number(val);
        const filled = "█".repeat(Math.round(n * 10));
        const empty = "░".repeat(10 - Math.round(n * 10));
        lines.push(`  ${label}: ${filled}${empty} ${n.toFixed(1)}/1.0`);
      }
    }
  }

  const explanation = (output.explanation as string) || (analysis as Record<string, unknown>).explanation;
  if (explanation) lines.push(`\n💡 Insights: ${explanation}`);

  return lines.join("\n");
}

async function handleClipSource(
  state: ConversationState,
  sender: string,
  text: string
): Promise<string[]> {
  if (!text.startsWith("http")) {
    return ["Please send a valid YouTube URL or video link."];
  }

  state.clipSource = { type: "url", value: text };
  state.step = "clip:processing";

  const confirmMsg = "✅ Got your video link!\n\n⏳ Analyzing and clipping your video... This may take a few minutes.";

  const userId = await ensureUser(state, sender);
  if (!userId) {
    resetState(sender);
    return [confirmMsg, "❌ Could not authenticate. Please try /start first."];
  }

  const job = await createJob(userId, "clip_shorts", { youtube_url: text });
  if (!job) {
    resetState(sender);
    return [confirmMsg, "❌ Failed to create the clipping job. The server might be down."];
  }

  state.currentJobId = job.id;
  const result = await pollJob(job.id);
  resetState(sender);

  if (result && result.status === "completed") {
    const assets = await getJobAssets(job.id);
    return [confirmMsg, formatClipResults(result, assets)];
  } else if (result && result.status === "failed") {
    return [confirmMsg, `❌ Clipping failed: ${result.error_message || "Unknown error"}`];
  }
  return [confirmMsg, `⏱️ Still processing. Check status with: /status ${job.id}`];
}

function formatClipResults(
  job: Record<string, unknown>,
  assets: Array<Record<string, unknown>>
): string {
  const output = (job.output_data as Record<string, unknown>) || {};
  const clips = (output.clips as Array<Record<string, unknown>>) || [];
  const lines = [`✂️ Clipping complete! Found ${assets.length} clip(s):\n`];

  for (let i = 0; i < assets.length; i++) {
    const asset = assets[i];
    const analysis = clips[i] || {};
    const engagement =
      analysis.engagement_score ??
      ((asset.metadata as Record<string, unknown>) || {}).engagement_score ??
      "N/A";
    const reason =
      (analysis.selection_reason as string) ||
      ((asset.metadata as Record<string, unknown>) || {}).clip_selection_reason ||
      "";

    lines.push(`🎬 Clip ${i + 1}`);
    if (asset.duration) lines.push(`  ⏱️ Duration: ${Number(asset.duration).toFixed(1)}s`);
    if (engagement !== "N/A") {
      const n = Number(engagement);
      const filled = "█".repeat(Math.round(n * 10));
      const empty = "░".repeat(10 - Math.round(n * 10));
      lines.push(`  📊 Engagement: ${filled}${empty} ${n.toFixed(1)}/1.0`);
    }
    if (reason) lines.push(`  💡 Why: ${reason}`);
    const url = asset.file_url || asset.file_path;
    if (url) lines.push(`  📎 ${url}`);
    lines.push("");
  }

  return lines.join("\n");
}

async function handleStatus(
  state: ConversationState,
  text: string
): Promise<string[]> {
  const parts = text.split(/\s+/);
  const jobId = parts[1] || state.currentJobId;

  if (!jobId) {
    return ["ℹ️ Usage: /status <job_id>\n\nRun a workflow first and the bot will remember your latest job."];
  }

  const job = await getJobStatus(jobId);
  if (!job) {
    return [`⚠️ Could not find job ${jobId}. It may not exist or the server is unreachable.`];
  }

  const emoji: Record<string, string> = {
    queued: "🕐",
    processing: "⏳",
    completed: "✅",
    failed: "❌",
  };

  const lines = [
    `${emoji[job.status] || "❓"} Job Status`,
    "",
    `ID: ${job.id}`,
    `Workflow: ${job.workflow_type.replace("_", " ")}`,
    `Status: ${job.status}`,
    `Created: ${job.created_at?.slice(0, 19).replace("T", " ")}`,
  ];

  if (job.started_at) lines.push(`Started: ${job.started_at.slice(0, 19).replace("T", " ")}`);
  if (job.completed_at) lines.push(`Completed: ${job.completed_at.slice(0, 19).replace("T", " ")}`);
  if (job.error_message) lines.push(`\n⚠️ Error: ${job.error_message}`);

  return [lines.join("\n")];
}
