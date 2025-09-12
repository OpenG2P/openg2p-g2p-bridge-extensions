import io
import logging

from minio import Minio
from minio.error import S3Error
from openg2p_fastapi_common.service import BaseService

from .config import Settings

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


class MinioUploader(BaseService):
    """Utility class for handling Minio operations."""

    def __init__(self):
        """Initialize the Minio client."""
        self.minio_client = Minio(
            _config.minio_endpoint,
            access_key=_config.minio_access_key,
            secret_key=_config.minio_secret_key,
            secure=_config.minio_secure,
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Ensure the minio bucket exists."""
        try:
            if not self.minio_client.bucket_exists(_config.minio_bucket_name):
                self.minio_client.make_bucket(_config.minio_bucket_name)
                _logger.info(f"Created bucket: {_config.minio_bucket_name}")
        except S3Error as e:
            _logger.error(f"Error ensuring bucket exists: {e}")
            raise

    def upload_csv_to_minio(self, filename: str, csv_content: str):
        """
        Upload CSV content to Minio.

        Args:
            filename: Name of the file to upload
            csv_content: CSV content as string
        """
        try:
            # Create the full object path
            object_path = f"{_config.zambia_csv_folder_path}/{filename}"

            # Convert string to bytes
            csv_bytes = csv_content.encode("utf-8")

            # Upload to Minio
            self.minio_client.put_object(
                bucket_name=_config.minio_bucket_name,
                object_name=object_path,
                data=io.BytesIO(csv_bytes),
                length=len(csv_bytes),
                content_type="text/csv",
            )

            _logger.info(f"Successfully uploaded {filename} to {_config.minio_bucket_name}/{object_path}")

        except S3Error as e:
            _logger.error(f"Error uploading to Minio: {e}")
            raise
