from app.storage.minio_client import get_minio_client


def check_minio() -> None:
    """Check MinIO availability by listing buckets once.

    Raises:
        Exception: for any configuration, connectivity, or auth error.
    """

    client = get_minio_client()
    # A simple call that requires auth and connectivity.
    list(client.list_buckets())


