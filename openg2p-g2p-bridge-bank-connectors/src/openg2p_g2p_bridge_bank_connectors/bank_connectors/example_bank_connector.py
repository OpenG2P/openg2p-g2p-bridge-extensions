import logging
from typing import List, Optional

import httpx
from openg2p_g2p_bridge_models.models import (
    FundsAvailableWithBankEnum,
    FundsBlockedWithBankEnum,
)
from pydantic import BaseModel

from ..bank_interface.bank_connector_interface import (
    BankConnectorInterface,
    BlockFundsResponse,
    CheckFundsResponse,
    DisbursementPaymentPayload,
    PaymentResponse,
    PaymentStatus,
)
from ..config import Settings

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


class BankPaymentPayload(BaseModel):
    payment_reference_number: str
    remitting_account: str
    remitting_account_currency: str
    payment_amount: float
    funds_blocked_reference_number: str
    beneficiary_name: str

    beneficiary_account: str
    beneficiary_account_currency: str
    beneficiary_account_type: str
    beneficiary_bank_code: str
    beneficiary_branch_code: str

    beneficiary_mobile_wallet_provider: Optional[str] = None
    beneficiary_phone_no: Optional[str] = None

    beneficiary_email: Optional[str] = None
    beneficiary_email_wallet_provider: Optional[str] = None

    narrative_1: Optional[str] = None
    narrative_2: Optional[str] = None
    narrative_3: Optional[str] = None
    narrative_4: Optional[str] = None
    narrative_5: Optional[str] = None
    narrative_6: Optional[str] = None

    payment_date: str


class ExampleBankConnector(BankConnectorInterface):
    def check_funds(self, account_number, currency, amount) -> CheckFundsResponse:
        _logger.info(
            f"Checking funds availability for account_number: {account_number}, currency: {currency}, amount: {amount}"
        )
        try:
            with httpx.Client() as client:
                request_data = {
                    "account_number": account_number,
                    "account_currency": currency,
                    "total_funds_needed": amount,
                }
                response = client.post(_config.funds_available_check_url_example_bank, json=request_data)
                response.raise_for_status()

                data = response.json()
                if data["status"] == "success":
                    _logger.info(
                        f"Funds available for account_number: {account_number}, currency: {currency}, amount: {amount}"
                    )
                    return CheckFundsResponse(
                        status=FundsAvailableWithBankEnum.FUNDS_AVAILABLE, error_code=""
                    )
                _logger.info(
                    f"Funds not available for account_number: {account_number}, currency: {currency}, amount: {amount}"
                )
                return CheckFundsResponse(
                    status=FundsAvailableWithBankEnum.FUNDS_NOT_AVAILABLE, error_code=""
                )
        except httpx.HTTPStatusError as e:
            _logger.error(
                f"Error checking funds availability for account_number: {account_number}, currency: {currency}, amount: {amount}"
            )
            return CheckFundsResponse(status=FundsAvailableWithBankEnum.PENDING_CHECK, error_code=str(e))

    def block_funds(self, account_number, currency, amount) -> BlockFundsResponse:
        _logger.info(
            f"Blocking funds for account_number: {account_number}, currency: {currency}, amount: {amount}"
        )
        try:
            with httpx.Client() as client:
                request_data = {
                    "account_number": account_number,
                    "currency": currency,
                    "amount": amount,
                }
                response = client.post(_config.funds_block_url_example_bank, json=request_data)
                response.raise_for_status()

                data = response.json()
                if data["status"] == "success":
                    _logger.info(
                        f"Funds blocked for account_number: {account_number}, currency: {currency}, amount: {amount}"
                    )
                    return BlockFundsResponse(
                        status=FundsBlockedWithBankEnum.FUNDS_BLOCK_SUCCESS,
                        block_reference_no=data["block_reference_no"],
                        error_code="",
                    )
                _logger.error(
                    f"Funds block failed for account_number: {account_number}, currency: {currency}, amount: {amount}"
                )
                return BlockFundsResponse(
                    status=FundsBlockedWithBankEnum.FUNDS_BLOCK_FAILURE,
                    block_reference_no="",
                    error_code=data.get("error_code", ""),
                )
        except httpx.HTTPStatusError as e:
            _logger.error(
                f"Error blocking funds for account_number: {account_number}, currency: {currency}, amount: {amount}"
            )
            return BlockFundsResponse(
                status=FundsBlockedWithBankEnum.FUNDS_BLOCK_FAILURE,
                block_reference_no="",
                error_code=str(e),
            )

    def initiate_payment(
        self, disbursement_payment_payloads: List[DisbursementPaymentPayload]
    ) -> PaymentResponse:
        _logger.info(f"Initiating payment for {len(disbursement_payment_payloads)} disbursements")
        try:
            with httpx.Client() as client:
                bank_payment_payloads = []
                for disbursement_payment_payload in disbursement_payment_payloads:
                    bank_payment_payload: BankPaymentPayload = BankPaymentPayload(
                        payment_reference_number=disbursement_payment_payload.disbursement_id,
                        remitting_account=disbursement_payment_payload.remitting_account,
                        remitting_account_currency=disbursement_payment_payload.remitting_account_currency,
                        payment_amount=disbursement_payment_payload.payment_amount,
                        funds_blocked_reference_number=disbursement_payment_payload.funds_blocked_reference_number,
                        beneficiary_name=disbursement_payment_payload.beneficiary_name,
                        beneficiary_account=disbursement_payment_payload.beneficiary_account,
                        beneficiary_account_currency=disbursement_payment_payload.beneficiary_account_currency,
                        beneficiary_account_type=disbursement_payment_payload.beneficiary_account_type,
                        beneficiary_bank_code=disbursement_payment_payload.beneficiary_bank_code,
                        beneficiary_branch_code=disbursement_payment_payload.beneficiary_branch_code,
                        beneficiary_mobile_wallet_provider=disbursement_payment_payload.beneficiary_mobile_wallet_provider,
                        beneficiary_phone_no=disbursement_payment_payload.beneficiary_phone_no,
                        beneficiary_email=disbursement_payment_payload.beneficiary_email,
                        beneficiary_email_wallet_provider=disbursement_payment_payload.beneficiary_email_wallet_provider,
                        payment_date=disbursement_payment_payload.payment_date,
                        narrative_1=disbursement_payment_payload.disbursement_narrative,
                        narrative_2=disbursement_payment_payload.benefit_program_mnemonic,
                        narrative_3=disbursement_payment_payload.cycle_code_mnemonic,
                        narrative_4=disbursement_payment_payload.beneficiary_id,
                        narrative_5="",
                        narrative_6="",
                    )
                    bank_payment_payloads.append(bank_payment_payload.model_dump())

                request_data = bank_payment_payloads
                _logger.info(f"Request data: {request_data}")
                _logger.info("Total payments to be initiated: %s", len(request_data))
                _logger.info("Initiating payment with Example Bank")

                response = client.post(_config.funds_disbursement_url_example_bank, json=request_data)
                response.raise_for_status()

                data = response.json()
                if data["status"] == "success":
                    _logger.info("Payment initiated successfully")
                    return PaymentResponse(status=PaymentStatus.SUCCESS, error_code="")
                _logger.error("Payment initiation failed")
                return PaymentResponse(status=PaymentStatus.ERROR, error_code=data.get("error_message", ""))
        except httpx.HTTPStatusError as e:
            _logger.error(f"Error initiating payment: {e}")
            return PaymentResponse(status=PaymentStatus.ERROR, error_code=str(e))

    def retrieve_reconciliation_id(
        self, bank_reference: str, customer_reference: str, narratives: str
    ) -> str:
        _logger.info(
            f"Retrieving reconciliation id for bank_reference: {bank_reference}, customer_reference: {customer_reference}"
        )
        return customer_reference

    def retrieve_beneficiary_name(self, narratives: str) -> str:
        _logger.info(f"Retrieving beneficiary name from narratives: {narratives}")
        return narratives[3]

    def retrieve_reversal_reason(self, narratives: str) -> str:
        _logger.info(f"Retrieving reversal reason from narratives: {narratives}")
        return narratives[-1]
