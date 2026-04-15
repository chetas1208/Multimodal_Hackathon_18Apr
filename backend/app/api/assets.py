from __future__ import annotations

import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.asset import Asset, AssetType
from app.schemas.asset import AssetList, AssetResponse

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=AssetList)
async def list_assets(
    asset_type: AssetType | None = None,
    job_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Asset)
    count_query = select(func.count(Asset.id))

    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
        count_query = count_query.where(Asset.asset_type == asset_type)
    if job_id:
        query = query.where(Asset.job_id == job_id)
        count_query = count_query.where(Asset.job_id == job_id)
    if user_id:
        query = query.where(Asset.user_id == user_id)
        count_query = count_query.where(Asset.user_id == user_id)

    total = (await db.execute(count_query)).scalar() or 0
    pages = max(1, math.ceil(total / per_page))

    query = query.order_by(Asset.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    items = list(result.scalars().all())

    return AssetList(
        items=[AssetResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetResponse.model_validate(asset)


@router.get("/{asset_id}/download")
async def download_asset(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    import os

    if not os.path.isfile(asset.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=asset.file_path,
        filename=os.path.basename(asset.file_path),
        media_type="application/octet-stream",
    )


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await db.delete(asset)
