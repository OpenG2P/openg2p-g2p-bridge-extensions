import logging
from datetime import datetime
from typing import List

from openg2p_g2pconnect_common_lib.schemas import StatusEnum, SyncResponseHeader
from openg2p_g2pconnect_mapper_lib.schemas import (
    ResolveRequest,
    ResolveResponse,
    ResolveResponseMessage,
    ResolveStatusReasonCode,
    SingleResolveResponse,
)
from openg2p_g2pconnect_mapper_lib.schemas.resolve import AccountProviderInfo
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ..config import Settings
from ..engine import get_engine
from ..interface.mapper_interface import MapperInterface
from ..models.zambia_registry import G2PPhoneNumber, G2PRegistrantID, ZambiaRegistry

_config = Settings.get_config()
_logger = logging.getLogger("zambia_mapper_impl")
_engine = get_engine()

session_maker = sessionmaker(bind=_engine.get("db_engine_registry"), expire_on_commit=False)


class ZambiaMapper(MapperInterface):
    def _construct_fa(self, result) -> str:
        """
        Construct Financial Address (FA) in a key-value format that can be parsed with regex.
        Uses only FAKeys-compatible fields for proper deconstruction.

        The FA format follows a dot-separated key:value structure:
        account_number:123.bank_code:123456/78/1.mobile_number:+260123456789.fa_type:BANK_ACCOUNT

        Field mapping:
        - account_number: partner_id (unique identifier)
        - bank_code: NRC (National Registration Card)
        - mobile_number: phone number
        - fa_type: BANK_ACCOUNT (for strategy detection)
        """
        # Create FA in key-value format using only FAKeys-compatible fields
        # Map our data to available FAKeys where possible
        try:
            fa_string = (
                f"account_number:{result.partner_id}."  # Use partner_id as account number
                f"bank_code:{result.nrc or ''}."  # Store NRC in bank_code field
                f"mobile_number:{result.phone_no or ''}."
                f"fa_type:BANK_ACCOUNT"
            )
            return fa_string
        except Exception as e:
            _logger.error(f"Error constructing FA: {str(e)}")
            # Fallback to simple format if construction fails
            return f"account_number:{result.partner_id}.mobile_number:{result.phone_no or ''}.fa_type:BANK_ACCOUNT"

    def resolve(self, resolve_request: ResolveRequest) -> ResolveResponse | None:
        """
        Resolve the given request from Mapper and return the result.

        This method performs BULK processing of beneficiary information requests.
        It collects all IDs from the resolve request and performs a single database
        query using WHERE IN clause for optimal performance.

        The bulk query JOINs between:
        - g2p_reg_id: Contains the ID values and links to partner via partner_id
        - res_partner (ZambiaRegistry): Contains beneficiary names and personal details
        - g2p_phone_number: Contains phone numbers (via partner_id reference)

        Process:
        1. Collect all valid IDs from the request
        2. Execute single bulk query with WHERE IN clause
        3. Group results by ID (keeping most recent phone per beneficiary)
        4. Construct responses for all requested IDs in batch
        5. Handle not-found cases appropriately
        """
        _logger.info(f"Received resolve request: {resolve_request}")

        resolve_responses: List[SingleResolveResponse] = []

        # Collect all beneficiary IDs and create a mapping to requests
        id_to_request_map = {}
        beneficiary_ids = []

        # Process each request to extract IDs and handle invalid cases
        for single_request in resolve_request.message.resolve_request:
            beneficiary_id = single_request.id
            if not beneficiary_id:
                # Handle case where ID is not provided
                resolve_responses.append(
                    SingleResolveResponse(
                        reference_id=single_request.reference_id,
                        timestamp=datetime.now(),
                        status=StatusEnum.rjct,
                        status_reason_code=ResolveStatusReasonCode.rjct_id_invalid,
                        status_reason_message="ID is required but not provided",
                    )
                )
            else:
                # Add to bulk processing lists
                beneficiary_ids.append(beneficiary_id)
                id_to_request_map[beneficiary_id] = single_request

        # If we have valid IDs to process, do bulk query
        if beneficiary_ids:
            _logger.info(f"Performing bulk query for {len(beneficiary_ids)} beneficiary IDs")

            with session_maker() as registry_session:
                try:
                    # Bulk query using WHERE IN clause
                    # Create alias for G2PRegistrantID to avoid conflicts
                    nrc_table = G2PRegistrantID.__table__.alias("nrc_table")

                    # Create subquery for NRC (id_type = 1)
                    nrc_subquery = (
                        select(nrc_table.c.value)
                        .where(nrc_table.c.partner_id == ZambiaRegistry.id)
                        .where(nrc_table.c.id_type == 1)
                        .limit(1)
                        .scalar_subquery()
                    )

                    query = (
                        select(
                            ZambiaRegistry.name,
                            ZambiaRegistry.family_name,
                            ZambiaRegistry.given_name,
                            G2PPhoneNumber.phone_no,
                            ZambiaRegistry.id.label("partner_id"),
                            G2PPhoneNumber.date_collected,
                            nrc_subquery.label("nrc"),
                        )
                        .outerjoin(G2PPhoneNumber, ZambiaRegistry.id == G2PPhoneNumber.partner_id)
                        .where(
                            ZambiaRegistry.id.in_(beneficiary_ids)
                        )  # Search by partner_id instead of value
                        .where(ZambiaRegistry.is_registrant)
                        .where(
                            (G2PPhoneNumber.disabled.is_(None)) | (G2PPhoneNumber.id.is_(None))
                        )  # Include records even if no phone number exists
                        .order_by(
                            ZambiaRegistry.id, G2PPhoneNumber.date_collected.desc()
                        )  # Order by partner_id
                    )

                    # Execute bulk query
                    results = registry_session.execute(query).fetchall()
                    _logger.info(f"Bulk query returned {len(results)} results")

                    # Group results by partner_id and keep only the most recent phone number per partner
                    partner_to_result_map = {}
                    for result in results:
                        partner_id = result.partner_id
                        if partner_id not in partner_to_result_map:
                            # First result for this partner_id (most recent phone due to ORDER BY)
                            partner_to_result_map[partner_id] = result

                    # Process all requested IDs and construct responses
                    for beneficiary_id in beneficiary_ids:
                        single_request = id_to_request_map[beneficiary_id]
                        # Convert beneficiary_id to int for comparison with partner_id
                        partner_id = int(beneficiary_id)

                        if partner_id in partner_to_result_map:
                            result = partner_to_result_map[partner_id]

                            # Construct full name from available parts
                            name_parts = []
                            if result.given_name:
                                name_parts.append(result.given_name)
                            if result.family_name:
                                name_parts.append(result.family_name)

                            # Use constructed name if available, otherwise fall back to main name field
                            full_name = " ".join(name_parts) if name_parts else result.name

                            # Construct FA with financial details
                            fa_value = self._construct_fa(result)

                            # Create AccountProviderInfo with beneficiary details
                            account_provider_info = AccountProviderInfo(
                                name=full_name,
                                code=str(result.partner_id),  # Use partner_id as code
                                subcode=result.nrc or None,  # Use NRC as subcode if available
                            )

                            _logger.debug(f"Found beneficiary: {full_name} with phone: {result.phone_no}")

                            resolve_responses.append(
                                SingleResolveResponse(
                                    reference_id=single_request.reference_id,
                                    timestamp=datetime.now(),
                                    id=beneficiary_id,  # Use the original partner_id from request
                                    fa=fa_value,  # Financial address with mobile number
                                    account_provider_info=account_provider_info,  # Beneficiary details
                                    status=StatusEnum.succ,
                                    status_reason_code=ResolveStatusReasonCode.succ_id_active,
                                    status_reason_message=f"Beneficiary found: {full_name}, Phone: {result.phone_no or 'N/A'}",
                                )
                            )
                        else:
                            # ID not found in database
                            _logger.debug(f"No beneficiary found for ID: {beneficiary_id}")
                            resolve_responses.append(
                                SingleResolveResponse(
                                    reference_id=single_request.reference_id,
                                    timestamp=datetime.now(),
                                    id=beneficiary_id,
                                    status=StatusEnum.succ,
                                    status_reason_code=ResolveStatusReasonCode.succ_id_not_found,
                                    status_reason_message="Beneficiary not found in registry",
                                )
                            )

                except Exception as e:
                    _logger.error(f"Error in bulk query processing: {str(e)}")
                    # If bulk query fails, create error responses for all remaining IDs
                    for beneficiary_id in beneficiary_ids:
                        single_request = id_to_request_map[beneficiary_id]
                        resolve_responses.append(
                            SingleResolveResponse(
                                reference_id=single_request.reference_id,
                                timestamp=datetime.now(),
                                status=StatusEnum.rjct,
                                status_reason_code=ResolveStatusReasonCode.rjct_id_invalid,
                                status_reason_message=f"Error processing request: {str(e)}",
                            )
                        )

        # Construct the response with required header
        header = SyncResponseHeader(
            message_id=resolve_request.header.message_id,
            message_ts=datetime.now().isoformat(),
            action="resolve",
            status=StatusEnum.succ,
            total_count=len(resolve_responses),
            completed_count=len(resolve_responses),
        )

        resolve_response = ResolveResponse(
            header=header,
            message=ResolveResponseMessage(
                transaction_id=resolve_request.message.transaction_id, resolve_response=resolve_responses
            ),
        )

        _logger.info(f"Returning resolve response: {resolve_response}")
        return resolve_response
