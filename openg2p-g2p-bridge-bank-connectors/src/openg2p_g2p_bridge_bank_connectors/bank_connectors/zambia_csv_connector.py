import io
import logging
from typing import List

from minio import Minio
from minio.error import S3Error

from ..bank_interface.bank_connector_interface import (
    BankConnectorInterface,
    BlockFundsResponse,
    CheckFundsResponse,
    DisbursementPaymentPayload,
    PaymentResponse,
    PaymentStatus,
)
from openg2p_g2p_bridge_models.models import (
    FundsAvailableWithBankEnum,
    FundsBlockedWithBankEnum,
)
from ..config import Settings
from ..helpers import ZambiaCSVHelper

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


class ZambiaCSVConnector(BankConnectorInterface):
    
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
   
    def check_funds(self, account_number, currency, amount) -> CheckFundsResponse:
        """Not implemented for CSV connector - passing for now."""
        _logger.info("check_funds not implemented for ZambiaCSVConnector")
        return CheckFundsResponse(
            status=FundsAvailableWithBankEnum.FUNDS_AVAILABLE, error_code=""
        )

    def block_funds(self, account_number, currency, amount) -> BlockFundsResponse:
        """Not implemented for CSV connector - passing for now."""
        _logger.info("block_funds not implemented for ZambiaCSVConnector")
        return BlockFundsResponse(
            status=FundsBlockedWithBankEnum.FUNDS_BLOCK_SUCCESS, block_reference_no="FUNDS_BLOCKED", error_code=""
        )

    def initiate_payment(self, payment_payloads: List[DisbursementPaymentPayload]) -> PaymentResponse:
        """
        Process payment payloads by creating a CSV file and uploading to Minio.

        Args:
            payment_payloads: List of DisbursementPaymentPayload objects

        Returns:
            PaymentResponse indicating success or failure
        """
        try:
            if not payment_payloads:
                _logger.error("No payment payloads provided")
                return PaymentResponse(status=PaymentStatus.ERROR, error_code="No payment payloads provided")

            _logger.info(f"Processing {len(payment_payloads)} payment payloads for CSV generation")

            # Generate filename using helper
            filename = ZambiaCSVHelper.generate_filename(payment_payloads[0])

            # Create CSV content using helper
            csv_content = ZambiaCSVHelper.create_csv_content(payment_payloads)

            # Upload to Minio
            self.upload_csv_to_minio(filename, csv_content)

            _logger.info(f"Successfully uploaded CSV file: {filename}")
            return PaymentResponse(status=PaymentStatus.SUCCESS, error_code="")

        except Exception as e:
            _logger.error(f"Error in initiate_payment: {str(e)}")
            return PaymentResponse(status=PaymentStatus.ERROR, error_code=str(e))

    def retrieve_reconciliation_id(
        self, bank_reference: str, customer_reference: str, narratives: str
    ) -> str:
        """Not implemented for CSV connector - passing for now."""
        _logger.info("retrieve_reconciliation_id not implemented for ZambiaCSVConnector")
        return customer_reference

    def retrieve_beneficiary_name(self, narratives: str) -> str:
        """Not implemented for CSV connector - passing for now."""
        _logger.info("retrieve_beneficiary_name not implemented for ZambiaCSVConnector")
        return ""

    def retrieve_reversal_reason(self, narratives: str) -> str:
        """Not implemented for CSV connector - passing for now."""
        _logger.info("retrieve_reversal_reason not implemented for ZambiaCSVConnector")
        return ""
