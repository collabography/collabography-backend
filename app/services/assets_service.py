from datetime import timedelta

from app.integrations.minio_client import get_presigned_get_url


class AssetsService:
    @staticmethod
    def get_presigned_url(object_key: str, expires_hours: int = 1) -> str:
        """Presigned GET URL 발급"""
        return get_presigned_get_url(
            object_key=object_key,
            expires=timedelta(hours=expires_hours),
        )

    @staticmethod
    def get_presigned_urls_batch(object_keys: list[str], expires_hours: int = 1) -> dict[str, str]:
        """Presigned GET URL 일괄 발급"""
        urls = {}
        for key in object_keys:
            urls[key] = get_presigned_get_url(
                object_key=key,
                expires=timedelta(hours=expires_hours),
            )
        return urls

