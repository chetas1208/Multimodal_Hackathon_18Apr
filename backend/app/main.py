from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import api_router
from app.config import settings
from app.database import Base, engine, get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.models  # noqa: F401 — ensure all models are registered

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created / verified")

    media_path = settings.STORAGE_LOCAL_PATH
    os.makedirs(media_path, exist_ok=True)
    os.makedirs(os.path.join(media_path, "uploads"), exist_ok=True)
    os.makedirs(os.path.join(media_path, "generated"), exist_ok=True)
    os.makedirs(os.path.join(media_path, "clips"), exist_ok=True)
    os.makedirs(os.path.join(media_path, "youtube"), exist_ok=True)
    os.makedirs(os.path.join(media_path, "demo"), exist_ok=True)

    yield

    await engine.dispose()


app = FastAPI(
    title="Marketing Studio Bot API",
    description="Chat-first AI marketing studio for e-commerce brands",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

media_path = settings.STORAGE_LOCAL_PATH
os.makedirs(media_path, exist_ok=True)
app.mount("/media", StaticFiles(directory=media_path), name="media")


@app.post("/api/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    from app.seed import seed_demo_data

    result = await seed_demo_data(db)
    return {"message": "Demo data seeded successfully", "counts": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
