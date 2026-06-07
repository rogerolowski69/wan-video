"""MinIO / S3-compatible object storage for generation artifacts."""

from __future__ import annotations

import mimetypes
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from paths import OUTPUT_DIR, PROJECT_ROOT

OUTPUT_PREFIX = "output/"


def is_minio_enabled() -> bool:
    return bool(os.environ.get("MINIO_ENDPOINT") and os.environ.get("MINIO_BUCKET"))


def _bucket() -> str:
    return os.environ.get("MINIO_BUCKET", "wan-video")


@lru_cache(maxsize=1)
def _client() -> Any:
    import boto3
    from botocore.client import Config

    return boto3.client(
        "s3",
        endpoint_url=os.environ["MINIO_ENDPOINT"],
        aws_access_key_id=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
        aws_secret_access_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin"),
        config=Config(signature_version="s3v4"),
        region_name=os.environ.get("MINIO_REGION", "us-east-1"),
    )


def normalize_storage_key(file_path: str) -> str:
    key = file_path.replace("\\", "/").lstrip("/")
    if key.startswith("output/"):
        return key
    return f"{OUTPUT_PREFIX}{Path(key).name}"


def upload_file(local_path: Path, key: str | None = None) -> str:
    object_key = key or normalize_storage_key(local_path.name)
    content_type = mimetypes.guess_type(local_path.name)[0] or "application/octet-stream"
    with local_path.open("rb") as handle:
        _client().put_object(
            Bucket=_bucket(),
            Key=object_key,
            Body=handle,
            ContentType=content_type,
        )
    return object_key


def persist_artifact(local_path: Path) -> str:
    rel = _relative_output_path(local_path)
    if is_minio_enabled():
        upload_file(local_path, rel)
    return rel


def artifact_public_url(file_path: str) -> str:
    key = normalize_storage_key(file_path)
    public_base = os.environ.get("MINIO_PUBLIC_URL", "").rstrip("/")
    if is_minio_enabled() and public_base:
        return f"{public_base}/{key}"
    return f"/api/files/{key}"


def fetch_object(key: str) -> tuple[bytes, str]:
    normalized = normalize_storage_key(key)
    response = _client().get_object(Bucket=_bucket(), Key=normalized)
    body: bytes = response["Body"].read()
    content_type = response.get("ContentType") or mimetypes.guess_type(normalized)[0] or "application/octet-stream"
    return body, content_type


def read_local_artifact(key: str) -> tuple[bytes, str] | None:
    normalized = normalize_storage_key(key)
    local = PROJECT_ROOT / normalized
    if not local.is_file():
        fallback = OUTPUT_DIR / Path(normalized).name
        if fallback.is_file():
            local = fallback
        else:
            return None
    content_type = mimetypes.guess_type(local.name)[0] or "application/octet-stream"
    return local.read_bytes(), content_type


def ensure_bucket() -> None:
    if not is_minio_enabled():
        return
    from botocore.exceptions import ClientError

    client = _client()
    bucket = _bucket()
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError:
        client.create_bucket(Bucket=bucket)


def _relative_output_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        rel = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        rel = resolved.as_posix()
    if not rel.startswith("output/"):
        rel = f"{OUTPUT_PREFIX}{path.name}"
    return rel
