from __future__ import annotations

import os
import shutil
import uuid
from abc import ABC, abstractmethod

from app.config import settings


class StorageBackend(ABC):
    @abstractmethod
    def save_file(self, source_path: str, dest_key: str) -> str:
        ...

    @abstractmethod
    def get_file(self, key: str) -> str:
        ...

    @abstractmethod
    def delete_file(self, key: str) -> bool:
        ...

    @abstractmethod
    def get_url(self, key: str) -> str:
        ...


class LocalStorage(StorageBackend):
    def __init__(self, base_path: str | None = None):
        self.base_path = base_path or settings.STORAGE_LOCAL_PATH
        os.makedirs(self.base_path, exist_ok=True)

    def save_file(self, source_path: str, dest_key: str | None = None) -> str:
        if dest_key is None:
            ext = os.path.splitext(source_path)[1]
            dest_key = f"{uuid.uuid4().hex}{ext}"
        dest = os.path.join(self.base_path, dest_key)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(source_path, dest)
        return dest_key

    def get_file(self, key: str) -> str:
        path = os.path.join(self.base_path, key)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {key}")
        return path

    def delete_file(self, key: str) -> bool:
        path = os.path.join(self.base_path, key)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def get_url(self, key: str) -> str:
        return f"/media/{key}"


class S3Storage(StorageBackend):
    def __init__(self):
        import boto3

        session_kwargs: dict = {}
        if settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY:
            session_kwargs["aws_access_key_id"] = settings.S3_ACCESS_KEY
            session_kwargs["aws_secret_access_key"] = settings.S3_SECRET_KEY

        client_kwargs: dict = {"region_name": settings.S3_REGION}
        if settings.S3_ENDPOINT:
            client_kwargs["endpoint_url"] = settings.S3_ENDPOINT

        self.client = boto3.client("s3", **session_kwargs, **client_kwargs)
        self.bucket = settings.S3_BUCKET

    def save_file(self, source_path: str, dest_key: str | None = None) -> str:
        if dest_key is None:
            ext = os.path.splitext(source_path)[1]
            dest_key = f"{uuid.uuid4().hex}{ext}"
        self.client.upload_file(source_path, self.bucket, dest_key)
        return dest_key

    def get_file(self, key: str) -> str:
        local_path = os.path.join("/tmp", os.path.basename(key))
        self.client.download_file(self.bucket, key, local_path)
        return local_path

    def delete_file(self, key: str) -> bool:
        self.client.delete_object(Bucket=self.bucket, Key=key)
        return True

    def get_url(self, key: str) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=3600,
        )


def get_storage() -> StorageBackend:
    if settings.STORAGE_BACKEND == "s3" and settings.S3_BUCKET:
        return S3Storage()
    return LocalStorage()
