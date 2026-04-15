# Architecture — Marketing Studio Bot

## System Diagram

```
                        ┌─────────────────────────────────────────────────────────────┐
                        │                    USER CHANNELS                            │
                        │                                                             │
                        │   ┌──────────┐         ┌──────────────┐                     │
                        │   │ Telegram │         │   iMessage   │                     │
                        │   │   App    │         │  (iPhone /   │                     │
                        │   │          │         │   macOS)     │                     │
                        │   └────┬─────┘         └──────┬───────┘                     │
                        └────────┼──────────────────────┼─────────────────────────────┘
                                 │                      │
                                 ▼                      ▼
                        ┌────────────────┐    ┌──────────────────┐
                        │  Telegram Bot  │    │  Photon iMessage │
                        │  (Python)      │    │  Bridge (TS/Bun) │
                        │                │    │                  │
                        │  • ConvHandler │    │  • State Machine │
                        │  • Polling /   │    │  • @photon-ai/   │
                        │    Webhook     │    │    imessage-kit  │
                        └───────┬────────┘    └────────┬─────────┘
                                │     HTTP / JSON      │
                                └──────────┬───────────┘
                                           ▼
                        ┌──────────────────────────────────────┐
                        │         FastAPI Backend               │
                        │                                      │
                        │  ┌────────────┐  ┌────────────────┐  │
                        │  │  REST API  │  │  Webhook       │  │
                        │  │  Endpoints │  │  Receiver      │  │
                        │  └─────┬──────┘  └───────┬────────┘  │
                        │        │                 │           │
                        │        ▼                 ▼           │
                        │  ┌──────────────────────────────┐   │
                        │  │       Service Layer          │   │
                        │  │  • User management           │   │
                        │  │  • Job orchestration         │   │
                        │  │  • Asset management          │   │
                        │  │  • Analysis scoring          │   │
                        │  └─────────────┬────────────────┘   │
                        │                │                     │
                        │        ┌───────┴───────┐             │
                        │        ▼               ▼             │
                        │  ┌──────────┐   ┌───────────┐       │
                        │  │PostgreSQL│   │   Redis   │       │
                        │  │  (data)  │   │  (broker) │       │
                        │  └──────────┘   └─────┬─────┘       │
                        └───────────────────────┼──────────────┘
                                                │
                                                ▼
                        ┌──────────────────────────────────────┐
                        │        Celery Workers                │
                        │                                      │
                        │  ┌──────────────────────────────┐   │
                        │  │   Video Generation Pipeline  │   │
                        │  │  ┌────────┐ ┌──────┐ ┌─────┐│   │
                        │  │  │Scraper │ │FFmpeg│ │ AI  ││   │
                        │  │  │(bs4)   │ │      │ │Gen  ││   │
                        │  │  └────────┘ └──────┘ └─────┘│   │
                        │  └──────────────────────────────┘   │
                        │                                      │
                        │  ┌──────────────────────────────┐   │
                        │  │   Clip Extraction Pipeline   │   │
                        │  │  ┌──────┐ ┌───────┐ ┌─────┐ │   │
                        │  │  │yt-dlp│ │Whisper│ │Score│ │   │
                        │  │  │      │ │       │ │     │ │   │
                        │  │  └──────┘ └───────┘ └─────┘ │   │
                        │  └──────────────────────────────┘   │
                        │                │                     │
                        │                ▼                     │
                        │  ┌──────────────────────────────┐   │
                        │  │   Storage (local / S3)       │   │
                        │  └──────────────────────────────┘   │
                        └──────────────────────────────────────┘
                                                │
                                                ▼
                        ┌──────────────────────────────────────┐
                        │       Nuxt 3 Dashboard               │
                        │  • Job history & status              │
                        │  • Asset gallery & video player      │
                        │  • Analysis scores & insights        │
                        │  • Analytics overview                │
                        └──────────────────────────────────────┘
```

---

## Component Descriptions

### Telegram Bot (`bot/`)

A Python application using `python-telegram-bot` v21.6 with `ConversationHandler`
for multi-step workflows. Runs in **polling mode** for development and **webhook
mode** for production. Communicates with the backend exclusively through HTTP.

### Photon iMessage Bridge (`photon-bridge/`)

A TypeScript module using `@photon-ai/imessage-kit` to receive and send iMessages.
Maintains conversation state in an in-memory `Map` keyed by sender phone number.
Shares the same backend API as the Telegram bot.

### FastAPI Backend (`backend/`)

The core API server. Handles user management, job creation, asset storage, and
analysis retrieval. Uses async SQLAlchemy with PostgreSQL and dispatches heavy
work to Celery.

### Celery Workers

Background task processors that run the compute-heavy pipelines:
- **Video generation:** page scraping, image processing, FFmpeg composition, AI analysis
- **Clip extraction:** yt-dlp download, Whisper transcription, segment scoring, FFmpeg clipping

### Frontend Dashboard (`frontend/`)

Nuxt 3 + Vue 3 + Tailwind CSS. Displays job history, asset gallery, video player,
and analysis scores. Communicates with the backend REST API.

---

## Data Flow: Workflow A — Generate Video

```
1. User sends /generate in Telegram or iMessage
2. Bot collects: product URL → product images → product description
3. Bot POSTs to backend:
   POST /api/jobs
   {
     "user_id": "uuid",
     "workflow_type": "generate_video",
     "input_data": {
       "product_url": "https://example.com/product",
       "product_images": ["url1", "url2"],
       "product_text": "Premium wireless earbuds..."
     }
   }
4. Backend creates Job (status: "queued") and dispatches Celery task
5. Celery worker picks up the task:
   a. Scrape product page for additional metadata (BeautifulSoup)
   b. Download and optimize product images
   c. Generate video scenes using AI + FFmpeg
   d. Compose final video with transitions, text overlays, music
   e. Run analysis pipeline:
      - Hook score (first 3 seconds attention grab)
      - CTA score (call-to-action effectiveness)
      - Pacing score (scene rhythm and timing)
      - Platform fit score (format/aspect ratio for target platform)
      - Engagement score (composite)
   f. Upload assets to storage (local or S3)
   g. Update Job status to "completed" with output_data
6. Bot polls GET /api/jobs/{id} until status is "completed"
7. Bot fetches assets via GET /api/jobs/{id}/assets
8. Bot sends video file + analysis summary to user
```

---

## Data Flow: Workflow B — Clip Into Shorts

```
1. User sends /clip in Telegram or iMessage
2. Bot collects: YouTube URL or video file upload
3. Bot POSTs to backend:
   POST /api/jobs
   {
     "user_id": "uuid",
     "workflow_type": "clip_shorts",
     "input_data": {
       "youtube_url": "https://youtube.com/watch?v=..."
     }
   }
4. Backend creates Job (status: "queued") and dispatches Celery task
5. Celery worker picks up the task:
   a. Download video via yt-dlp (or use uploaded file)
   b. Transcribe audio with Whisper → timestamped transcript
   c. Analyze transcript segments for engagement potential:
      - Emotional peaks (sentiment analysis)
      - Hook-worthy openings
      - Self-contained narrative arcs
      - Quotable / shareable moments
   d. Select top 2–3 segments
   e. Extract clips with FFmpeg (with fade in/out)
   f. Score each clip:
      - engagement_score (0–1)
      - clip_selection_reason (text explanation)
   g. Upload clip assets to storage
   h. Update Job status to "completed"
6. Bot polls for completion
7. Bot sends each clip as a video file with:
   - Engagement score bar chart
   - Selection reason
   - Duration
```

---

## Database Schema

### users

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK, default gen |
| `telegram_id` | BIGINT | UNIQUE, NOT NULL |
| `username` | VARCHAR(255) | nullable |
| `first_name` | VARCHAR(255) | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL, default now() |
| `updated_at` | TIMESTAMPTZ | NOT NULL, auto-update |

### jobs

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id, CASCADE |
| `workflow_type` | ENUM(`generate_video`, `clip_shorts`) | NOT NULL |
| `status` | ENUM(`queued`, `processing`, `completed`, `failed`) | NOT NULL, default `queued` |
| `input_data` | JSON | NOT NULL |
| `output_data` | JSON | nullable |
| `error_message` | TEXT | nullable |
| `started_at` | TIMESTAMPTZ | nullable |
| `completed_at` | TIMESTAMPTZ | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

### assets

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `job_id` | UUID | FK → jobs.id, CASCADE |
| `user_id` | UUID | FK → users.id, CASCADE |
| `asset_type` | ENUM(`video`, `image`, `subtitle`, `thumbnail`) | NOT NULL |
| `file_path` | TEXT | NOT NULL |
| `file_url` | TEXT | nullable |
| `file_size` | BIGINT | nullable |
| `duration` | FLOAT | nullable |
| `metadata` | JSON | nullable |
| `tags` | JSON | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |

### analyses

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `job_id` | UUID | FK → jobs.id, CASCADE |
| `asset_id` | UUID | FK → assets.id, SET NULL, nullable |
| `hook_score` | FLOAT | NOT NULL, default 0.0 |
| `cta_score` | FLOAT | NOT NULL, default 0.0 |
| `pacing_score` | FLOAT | NOT NULL, default 0.0 |
| `platform_fit_score` | FLOAT | NOT NULL, default 0.0 |
| `engagement_score` | FLOAT | NOT NULL, default 0.0 |
| `explanation` | TEXT | nullable |
| `clip_selection_reason` | TEXT | nullable |
| `platform_recommendations` | JSON | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |

### bot_sessions

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id, CASCADE |
| `workflow_type` | ENUM | NOT NULL |
| `state` | JSON | NOT NULL, default {} |
| `current_step` | VARCHAR(100) | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

---

## API Endpoint Catalog

### Health

| Method | Path | Description | Auth |
|---|---|---|---|
| `GET` | `/health` | Service health check | No |

### Users

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/api/users` | Create or fetch user by telegram_id | No |
| `GET` | `/api/users/:id` | Get user by ID | No |

### Jobs

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/api/jobs` | Create processing job | No |
| `GET` | `/api/jobs` | List jobs (paginated) | No |
| `GET` | `/api/jobs/:id` | Get job by ID | No |
| `PATCH` | `/api/jobs/:id` | Update job status | Internal |
| `GET` | `/api/jobs/:id/assets` | List assets for job | No |

### Assets

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/api/upload` | Upload file (multipart) | No |
| `GET` | `/api/assets/:id` | Get asset by ID | No |

### Analytics

| Method | Path | Description | Auth |
|---|---|---|---|
| `GET` | `/api/analytics/overview` | Aggregated dashboard stats | No |

---

## Multi-Channel Bot Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ADAPTER LAYER                                │
│                                                                  │
│  ┌─────────────────┐   ┌─────────────────┐   ┌──────────────┐  │
│  │   Telegram Bot   │   │  Photon iMessage │   │  Future:     │  │
│  │   (Python)       │   │  Bridge (TS)     │   │  WhatsApp /  │  │
│  │                  │   │                  │   │  Discord     │  │
│  │  ConversationHdl │   │  State Machine   │   │              │  │
│  └────────┬─────────┘   └────────┬─────────┘   └──────┬───────┘  │
│           │                      │                     │         │
│           └──────────────────────┼─────────────────────┘         │
│                                  │                                │
│                        ┌─────────▼─────────┐                     │
│                        │   HTTP REST API   │                     │
│                        │   (JSON over TLS) │                     │
│                        └─────────┬─────────┘                     │
└──────────────────────────────────┼───────────────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   FastAPI Backend    │
                        │   (Single source of  │
                        │    truth for all     │
                        │    channels)         │
                        └──────────────────────┘
```

Each channel adapter is responsible for:
1. **Receiving messages** in its native format
2. **Managing conversation state** (ConversationHandler for Telegram, in-memory Map for iMessage)
3. **Translating** user inputs into backend API calls
4. **Formatting** backend responses for the channel

All business logic, AI processing, storage, and data management live in the backend.

---

## Job Processing Pipeline

```
Job Created (queued)
       │
       ▼
  ┌─────────┐    Celery picks up task
  │ queued  │ ──────────────────────────┐
  └─────────┘                           │
                                        ▼
                               ┌──────────────┐
                               │  processing  │
                               └──────┬───────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                  │
                    ▼                 ▼                  ▼
           ┌──────────────┐ ┌──────────────┐  ┌──────────────┐
           │   Download   │ │  Transcribe  │  │   Scrape     │
           │   (yt-dlp)   │ │  (Whisper)   │  │   (bs4)      │
           └──────┬───────┘ └──────┬───────┘  └──────┬───────┘
                  │                │                  │
                  └────────────────┼──────────────────┘
                                   │
                                   ▼
                          ┌──────────────┐
                          │   Process    │
                          │   (FFmpeg)   │
                          └──────┬───────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │   Analyze    │
                          │   (scoring)  │
                          └──────┬───────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │   Upload     │
                          │   (storage)  │
                          └──────┬───────┘
                                 │
                    ┌────────────┴───────────┐
                    ▼                        ▼
             ┌───────────┐           ┌───────────┐
             │ completed │           │  failed   │
             └───────────┘           └───────────┘
```

---

## Storage Architecture

```
media/
├── jobs/
│   ├── {job_uuid}/
│   │   ├── input/              # Uploaded product images
│   │   │   ├── product_1.jpg
│   │   │   └── product_2.jpg
│   │   ├── output/             # Generated assets
│   │   │   ├── video_ad.mp4
│   │   │   ├── clip_1.mp4
│   │   │   ├── clip_2.mp4
│   │   │   └── thumbnail.jpg
│   │   └── temp/               # Intermediate files (cleaned up)
│   └── ...
└── uploads/                    # Direct file uploads
    └── {timestamp}_{filename}
```

In production, `STORAGE_BACKEND=s3` stores files in an S3-compatible bucket with
the same directory structure. File URLs are generated as pre-signed URLs.

---

## Deployment Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         PRODUCTION                                │
│                                                                   │
│  ┌─────────┐   ┌─────────────────────┐   ┌──────────────────┐   │
│  │ Vercel  │   │  Railway / Render   │   │  Mac mini        │   │
│  │         │   │                     │   │  (self-hosted)   │   │
│  │ Frontend│   │ ┌─────────────────┐ │   │                  │   │
│  │ (Nuxt)  │   │ │  FastAPI + Uvic │ │   │ Photon iMessage  │   │
│  │         │   │ │  (backend)      │ │   │ Bridge           │   │
│  └────┬────┘   │ └─────────────────┘ │   └────────┬─────────┘   │
│       │        │ ┌─────────────────┐ │            │              │
│       │        │ │  Celery Worker  │ │            │              │
│       │        │ └─────────────────┘ │            │              │
│       │        │ ┌─────────────────┐ │            │              │
│       │        │ │  Telegram Bot   │ │            │              │
│       │        │ └─────────────────┘ │            │              │
│       │        └──────────┬──────────┘            │              │
│       │                   │                       │              │
│       └───────────────────┼───────────────────────┘              │
│                           │                                      │
│              ┌────────────┴────────────┐                         │
│              ▼                         ▼                         │
│     ┌──────────────┐         ┌──────────────┐                   │
│     │ Neon /       │         │ Upstash /    │                   │
│     │ Supabase     │         │ Railway      │                   │
│     │ (PostgreSQL) │         │ (Redis)      │                   │
│     └──────────────┘         └──────────────┘                   │
└──────────────────────────────────────────────────────────────────┘
```
