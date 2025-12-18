from functools import lru_cache

from minio import Minio

from app.core.config import get_settings


class MinioNotConfiguredError(RuntimeError):
    """Raised when MinIO related settings are not provided."""


@lru_cache(maxsize=1)
def get_minio_client() -> Minio:
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
    """Create the bucket if it does not exist.

    This can be called on startup or lazily before first use.
    """
    settings = get_settings()
    name = bucket_name or settings.minio_bucket
    if not name:
        raise MinioNotConfiguredError("MinIO bucket name is not configured.")

    client = get_minio_client()

    found = client.bucket_exists(name)
    if not found:
        client.make_bucket(name)


