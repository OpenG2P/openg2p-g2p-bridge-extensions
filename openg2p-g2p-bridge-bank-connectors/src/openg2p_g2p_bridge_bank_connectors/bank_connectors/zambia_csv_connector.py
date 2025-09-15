import logging
from typing import List

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
from ..minio import MinioUploader

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


class ZambiaCSVConnector(BankConnectorInterface):
    def __init__(self):
        """Initialize the Zambia CSV Connector with helpers and minio uploader."""
        super().__init__()
        self.minio_uploader = MinioUploader().get_component()

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
            status=FundsBlockedWithBankEnum.FUNDS_BLOCKED, error_code=""
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
            self.minio_uploader.upload_csv_to_minio(filename, csv_content)

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
