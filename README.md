# Marketing Studio Bot

**A chat-first AI marketing studio for e-commerce brands.** Generate scroll-stopping video ads and clip long-form content into viral shorts — all from Telegram or iMessage.

---

## Overview

Marketing Studio Bot is a multi-channel conversational AI tool that helps e-commerce brands create professional marketing videos in minutes. Users interact through Telegram or iMessage to:

1. **Generate Video Ads** — Provide a product URL, images, and description; receive a polished promotional video with AI-driven analysis scores.
2. **Clip Into Shorts** — Submit a YouTube URL or upload a long video; receive 2–3 optimized short clips ranked by engagement potential.

A full-stack dashboard lets teams review assets, track jobs, and analyze performance.

---

## Features

- **Conversational workflow** — guided step-by-step via Telegram or iMessage
- **AI video generation** — product page scraping, scene composition, voice-over
- **Smart clipping** — transcript-aware clip selection using Whisper + engagement scoring
- **Multi-channel** — Telegram bot + Photon iMessage bridge sharing one backend
- **Analysis dashboard** — hook score, CTA score, pacing, platform fit, engagement
- **Background processing** — Celery workers with Redis for async job execution
- **Asset management** — local or S3-compatible storage with per-job organization
- **Real-time status** — poll from chat or check the web dashboard

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Telegram Bot** | Python 3.11, python-telegram-bot 21.6, httpx |
| **iMessage Bridge** | TypeScript, Bun, @photon-ai/imessage-kit 2.1 |
| **Backend API** | Python 3.11, FastAPI 0.115, SQLAlchemy 2.0, Pydantic 2.9 |
| **Task Queue** | Celery 5.4 + Redis 7 |
| **Database** | PostgreSQL 16 |
| **Video Processing** | FFmpeg, yt-dlp, OpenAI Whisper |
| **Frontend Dashboard** | Nuxt 3, Vue 3, Tailwind CSS |
| **Deployment** | Docker Compose (dev), Railway / Render / Vercel (prod) |

---

## Project Structure

```
marketing-studio-bot/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   └── health.py       # Health check endpoint
│   │   ├── models/
│   │   │   ├── asset.py        # Asset ORM model
│   │   │   ├── analysis.py     # Analysis ORM model
│   │   │   ├── bot_session.py  # Bot session + WorkflowType enum
│   │   │   ├── job.py          # Job ORM model + JobStatus enum
│   │   │   ├── user.py         # User ORM model
│   │   │   └── workflow_request.py
│   │   ├── schemas/
│   │   │   ├── asset.py        # Asset Pydantic schemas
│   │   │   ├── bot.py          # Telegram webhook schemas
│   │   │   ├── job.py          # Job Pydantic schemas
│   │   │   └── analytics.py    # Analytics schemas
│   │   ├── config.py           # Backend settings
│   │   └── database.py         # Async SQLAlchemy engine
│   └── requirements.txt
│
├── bot/                        # Telegram bot
│   ├── handlers/
│   │   ├── start.py            # /start and /help commands
│   │   ├── workflow_a.py       # Generate Video conversation
│   │   ├── workflow_b.py       # Clip Into Shorts conversation
│   │   └── status.py           # /status command
│   ├── api_client.py           # httpx client for backend API
│   ├── config.py               # Bot settings
│   ├── main.py                 # Entry point (polling + webhook)
│   ├── Dockerfile
│   └── requirements.txt
│
├── photon-bridge/              # iMessage bridge (Photon SDK)
│   ├── src/
│   │   ├── index.ts            # SDK initialization + message loop
│   │   ├── api-client.ts       # fetch-based backend client
│   │   └── workflows.ts        # Conversation state machine
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
├── frontend/                   # Nuxt 3 dashboard
│   ├── app.vue
│   ├── nuxt.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── docker-compose.yml          # Full-stack local dev
├── ARCHITECTURE.md             # Detailed architecture doc
├── .env.example                # Environment variable template
├── .gitignore
└── README.md                   # ← You are here
```

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Backend + Telegram bot |
| Node.js / Bun | 18+ / 1.0+ | Frontend + Photon bridge |
| PostgreSQL | 16+ | Primary database |
| Redis | 7+ | Celery broker + cache |
| FFmpeg | 6+ | Video processing |
| yt-dlp | latest | YouTube download |
| Docker & Compose | latest | Local orchestration (optional) |

---

## Quick Start

### Option A: Docker Compose (recommended)

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN and other secrets

# 2. Start everything
docker compose up --build

# Services available:
#   Backend API   → http://localhost:8000
#   Frontend      → http://localhost:3000
#   PostgreSQL    → localhost:5432
#   Redis         → localhost:6379
```

### Option B: Manual Setup

**1. Database & Redis**

```bash
# Start Postgres and Redis (or use managed services)
docker run -d --name pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=marketing_studio -p 5432:5432 postgres:16-alpine
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

**2. Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env  # edit with your values
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**3. Celery Worker**

```bash
cd backend
celery -A app.worker worker --loglevel=info
```

**4. Telegram Bot**

```bash
cd bot
pip install -r requirements.txt
python main.py --mode polling
```

**5. Frontend**

```bash
cd frontend
npm install
npm run dev
```

**6. Photon iMessage Bridge (optional, macOS only)**

```bash
cd photon-bridge
bun install
bun dev
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | `postgresql://postgres:postgres@localhost:5432/marketing_studio` | PostgreSQL connection string |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Redis connection string |
| `SECRET_KEY` | Yes | `change-me-in-production` | Backend signing key |
| `API_HOST` | No | `0.0.0.0` | Backend listen address |
| `API_PORT` | No | `8000` | Backend listen port |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated allowed origins |
| `TELEGRAM_BOT_TOKEN` | Yes | — | Token from @BotFather |
| `TELEGRAM_WEBHOOK_URL` | Prod | — | Public HTTPS URL for webhook mode |
| `PHOTON_API_KEY` | iMessage | — | Photon SDK API key |
| `PHOTON_PHONE_NUMBER` | iMessage | — | Phone number for iMessage bridge |
| `STORAGE_BACKEND` | No | `local` | `local` or `s3` |
| `STORAGE_LOCAL_PATH` | No | `./media` | Local file storage directory |
| `S3_BUCKET` | S3 | — | S3 bucket name |
| `S3_REGION` | S3 | `us-east-1` | S3 region |
| `S3_ACCESS_KEY` | S3 | — | S3 access key |
| `S3_SECRET_KEY` | S3 | — | S3 secret key |
| `OPENAI_API_KEY` | No | — | For Whisper transcription |
| `NUXT_PUBLIC_API_BASE` | No | `http://localhost:8000` | Frontend API base URL |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/users` | Create or get user by telegram_id |
| `GET` | `/api/users/:id` | Get user details |
| `POST` | `/api/jobs` | Create a new processing job |
| `GET` | `/api/jobs/:id` | Get job status and details |
| `GET` | `/api/jobs/:id/assets` | List assets for a job |
| `GET` | `/api/jobs` | List jobs (paginated, filterable) |
| `POST` | `/api/upload` | Upload a file (multipart) |
| `GET` | `/api/analytics/overview` | Dashboard analytics summary |

---

## Database Schema

| Table | Key Columns | Purpose |
|---|---|---|
| `users` | `id`, `telegram_id`, `username`, `first_name` | User accounts |
| `jobs` | `id`, `user_id`, `workflow_type`, `status`, `input_data`, `output_data` | Processing jobs |
| `assets` | `id`, `job_id`, `asset_type`, `file_path`, `file_url`, `duration` | Generated files |
| `analyses` | `id`, `job_id`, `asset_id`, `hook_score`, `engagement_score`, `clip_selection_reason` | AI analysis results |
| `bot_sessions` | `id`, `user_id`, `workflow_type`, `state`, `current_step` | Conversation state |
| `workflow_requests` | `id`, `job_id`, `user_id` | Workflow audit trail |
| `activity_logs` | `id`, `job_id`, `user_id` | Activity audit trail |

---

## Telegram Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message + register user |
| `/generate` | Start the video ad generation workflow |
| `/clip` | Start the clip-into-shorts workflow |
| `/status [job_id]` | Check job status |
| `/done` | Finish uploading images (during /generate) |
| `/cancel` | Cancel the current workflow |
| `/help` | Show available commands |

### Example: Generate a Video Ad

```
You:   /generate
Bot:   🛍️ Let's create a video ad! Send me your product URL.
You:   https://example.com/products/wireless-earbuds
Bot:   ✅ Got your URL! Now send 1–5 product images.
You:   [sends 3 photos]
You:   /done
Bot:   ✅ 3 images received! Describe your product.
You:   Premium wireless earbuds with 40hr battery, ANC, and crystal-clear audio. Perfect for commuters.
Bot:   📋 Here's what I've got: [summary]
       ⏳ Processing your video ad...
Bot:   🎬 Your video ad is ready!
       📊 Analysis Scores:
         Hook:     ████████░░ 0.8/1.0
         CTA:      ███████░░░ 0.7/1.0
         Pacing:   █████████░ 0.9/1.0
       [sends video file]
```

---

## Photon iMessage Integration

The Photon iMessage bridge (`photon-bridge/`) is an optional module that extends
Marketing Studio to Apple's iMessage. It uses the
[@photon-ai/imessage-kit](https://photon.sh) SDK (requires macOS) and connects
to the same FastAPI backend as the Telegram bot.

**Multi-channel architecture:** Both the Telegram bot and the iMessage bridge are
thin adapter layers. All business logic, AI processing, and data storage live in
the backend. This means users get a consistent experience regardless of channel,
and adding new channels (WhatsApp, Discord, Slack) requires only a new adapter.

> Built for the **Photon Hackathon Track** — demonstrating how a single AI product
> can serve users across multiple messaging platforms with minimal additional code.

See [`photon-bridge/README.md`](photon-bridge/README.md) for setup instructions.

---

## Deployment

| Component | Recommended Platform | Notes |
|---|---|---|
| Frontend | **Vercel** | Nuxt 3 SSR or static export |
| Backend + Workers | **Railway** or **Render** | Docker-based, auto-scaling |
| Database | **Neon** or **Supabase** | Managed PostgreSQL |
| Redis | **Upstash** or **Railway** | Managed Redis |
| Telegram Bot | **Railway** | Long-running process (polling) or webhook |
| iMessage Bridge | **Mac mini** (self-hosted) | Photon requires macOS |

For production webhook mode:

```bash
# Backend receives Telegram webhooks at /api/bot/webhook
# Bot runs in webhook mode:
python main.py --mode webhook
```

---

## Demo

1. **Start the stack:** `docker compose up --build`
2. **Open Telegram:** Search for your bot by username
3. **Send `/start`** to see the welcome message
4. **Send `/generate`** and follow the prompts to create a video ad
5. **Send `/clip`** with a YouTube URL to generate short clips
6. **Visit `http://localhost:3000`** to see the dashboard with job history and analytics

---

## License

MIT
