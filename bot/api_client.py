from __future__ import annotations

import logging
from typing import Any

import httpx

from config import settings

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


class APIClient:
    """Async HTTP client for the Marketing Studio FastAPI backend."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.API_BASE_URL).rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=_TIMEOUT,
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        data: Any = None,
        files: Any = None,
        content_type_override: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        try:
            client = await self._get_client()
            headers = {} if not content_type_override else {"Content-Type": None}
            resp = await client.request(
                method,
                path,
                json=json,
                params=params,
                data=data,
                files=files,
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "HTTP %s %s returned %s: %s",
                method,
                path,
                exc.response.status_code,
                exc.response.text[:500],
            )
            return None
        except httpx.RequestError as exc:
            logger.error("Request to %s %s failed: %s", method, path, exc)
            return None

    # ── User endpoints ──────────────────────────────────────────────────

    async def create_user(
        self, telegram_id: int, username: str | None, first_name: str | None
    ) -> dict[str, Any] | None:
        return await self._request(
            "POST",
            "/api/users",
            json={
                "telegram_id": telegram_id,
                "username": username or "",
                "first_name": first_name or "",
            },
        )

    # ── Job endpoints ───────────────────────────────────────────────────

    async def create_job(
        self,
        user_id: str,
        workflow_type: str,
        input_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        return await self._request(
            "POST",
            "/api/jobs",
            json={
                "user_id": user_id,
                "workflow_type": workflow_type,
                "input_data": input_data,
            },
        )

    async def get_job_status(self, job_id: str) -> dict[str, Any] | None:
        return await self._request("GET", f"/api/jobs/{job_id}")

    async def get_job_assets(self, job_id: str) -> list[dict[str, Any]] | None:
        result = await self._request("GET", f"/api/jobs/{job_id}/assets")
        if isinstance(result, dict):
            return result.get("items", [])
        return result

    # ── File upload ─────────────────────────────────────────────────────

    async def upload_file(
        self, file_bytes: bytes, filename: str
    ) -> dict[str, Any] | None:
        return await self._request(
            "POST",
            "/api/upload",
            files={"file": (filename, file_bytes)},
            content_type_override=True,
        )


api_client = APIClient()
