# Photon iMessage Bridge — Marketing Studio Bot

An optional iMessage channel for the Marketing Studio Bot, built with
[Photon's @photon-ai/imessage-kit](https://photon.sh) SDK. This bridge connects
to the **same FastAPI backend** as the Telegram bot, providing a seamless
multi-channel experience.

## Why iMessage?

Many e-commerce founders and marketers live in the Apple ecosystem. The Photon
bridge lets them access the full Marketing Studio workflow — generate video ads
and clip shorts — directly from iMessage without installing another app.

> **Photon Hackathon Track:** This module was built specifically for the Photon
> prize track, demonstrating a production-quality iMessage integration that
> extends an existing AI product to a new channel.

## Prerequisites

| Requirement | Notes |
|---|---|
| **macOS** | iMessage bridge requires a Mac (Photon SDK constraint) |
| **Bun ≥ 1.0** | Runtime (Node 18+ also works, but Bun is recommended) |
| **Photon API Key** | Sign up at [photon.sh](https://photon.sh) |
| **Backend running** | The FastAPI backend must be reachable at `API_BASE_URL` |

## Setup

1. **Install dependencies**

   ```bash
   cd photon-bridge
   bun install
   ```

2. **Configure environment variables**

   Copy the root `.env.example` and fill in:

   ```env
   PHOTON_API_KEY=your-photon-api-key
   PHOTON_PHONE_NUMBER=+1XXXXXXXXXX
   API_BASE_URL=http://localhost:8000
   ```

3. **Start the bridge**

   ```bash
   # Development (auto-reload)
   bun dev

   # Production
   bun start
   ```

## Architecture

```
┌──────────┐    iMessage     ┌──────────────────┐    HTTP     ┌───────────┐
│  iPhone / │ ──────────────▶ │  Photon Bridge   │ ──────────▶ │  FastAPI  │
│  macOS    │ ◀────────────── │  (this module)   │ ◀────────── │  Backend  │
└──────────┘                 └──────────────────┘             └───────────┘
```

The bridge maintains in-memory conversation state per sender and routes messages
through the same workflow state machine used across all channels. It calls the
backend REST API for user management, job creation, polling, and asset retrieval.

## Supported Commands

| Command | Description |
|---|---|
| `/generate` | Start the video ad generation workflow |
| `/clip` | Start the clip-into-shorts workflow |
| `/status` | Check job status |
| `/cancel` | Cancel the current workflow |
| `/help` | Show available commands |

## Multi-Channel Architecture

The Photon bridge is designed as a thin adapter layer. All business logic and
AI processing live in the FastAPI backend. This means:

- **Consistent experience** across Telegram and iMessage
- **Single source of truth** for jobs, assets, and user data
- **Easy to extend** — add WhatsApp, Discord, or Slack by writing another adapter

## License

MIT
