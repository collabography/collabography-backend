from datetime import timedelta
from functools import lru_cache

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings


class MinioNotConfiguredError(RuntimeError):
    """Raised when MinIO related settings are not provided."""


@lru_cache(maxsize=1)
def get_minio_client() -> Minio:
    """MinIO 클라이언트 반환"""
    settings = get_settings()

    if not settings.minio_endpoint or not settings.minio_access_key or not settings.minio_secret_key:
        raise MinioNotConfiguredError("MinIO settings are not fully configured.")

    endpoint = settings.minio_endpoint
    # Minio client expects host:port without scheme; secure flag controls http/https.
    if endpoint.startswith("http://"):
        endpoint = endpoint[len("http://") :]
    elif endpoint.startswith("https://"):
        endpoint = endpoint[len("https://") :]

    return Minio(
        endpoint=endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


async def ensure_bucket_exists(bucket_name: str | None = None) -> None:
    """버킷이 없으면 생성"""
    settings = get_settings()
    name = bucket_name or settings.minio_bucket
    if not name:
        raise MinioNotConfiguredError("MinIO bucket name is not configured.")

    client = get_minio_client()

    try:
        found = client.bucket_exists(name)
        if not found:
            client.make_bucket(name)
    except S3Error as e:
        raise RuntimeError(f"Failed to ensure bucket exists: {e}") from e


def get_presigned_put_url(
    object_key: str,
    expires: timedelta = timedelta(hours=1),
    content_type: str = "application/octet-stream",
) -> str:
    """Presigned PUT URL 발급 (업로드용)"""
    settings = get_settings()
    bucket = settings.minio_bucket
    if not bucket:
        raise MinioNotConfiguredError("MinIO bucket name is not configured.")

    client = get_minio_client()

    try:
        url = client.presigned_put_object(
            bucket_name=bucket,
            object_name=object_key,
            expires=expires,
        )
        return url
    except S3Error as e:
        raise RuntimeError(f"Failed to generate presigned PUT URL: {e}") from e


def get_presigned_get_url(
    object_key: str,
    expires: timedelta = timedelta(hours=1),
) -> str:
    """Presigned GET URL 발급 (다운로드용)"""
    settings = get_settings()
    bucket = settings.minio_bucket
    if not bucket:
        raise MinioNotConfiguredError("MinIO bucket name is not configured.")

    client = get_minio_client()

    try:
        url = client.presigned_get_object(
            bucket_name=bucket,
            object_name=object_key,
            expires=expires,
        )
        return url
    except S3Error as e:
        raise RuntimeError(f"Failed to generate presigned GET URL: {e}") from e

