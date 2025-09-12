import logging
from datetime import datetime
from typing import List

import orjson
from openg2p_g2pconnect_common_lib.schemas import StatusEnum
from openg2p_g2pconnect_mapper_lib.schemas import (
    ResolveRequest,
    ResolveResponse,
    ResolveResponseMessage,
    ResolveStatusReasonCode,
    SingleResolveResponse,
)
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
        Construct Financial Address (FA) in a deconstructable JSON format.
        This includes all the beneficiary details that can be parsed later.

        The FA format follows a JSON structure that can be easily deconstructed:
        {
            "partner_id": 123,
            "name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "original_name": "John Doe",
            "phone_no": "+260123456789",
            "id_value": "ZM001234567",
            "nrc": "123456/78/1",
            "fa_type": "BANK_ACCOUNT"
        }
        """
        # Construct full name from available parts
        name_parts = []
        if result.given_name:
            name_parts.append(result.given_name)
        if result.family_name:
            name_parts.append(result.family_name)

        full_name = " ".join(name_parts) if name_parts else result.name

        # Create FA data structure with all available information
        fa_data = {
            "partner_id": result.partner_id,
            "name": full_name,
            "given_name": result.given_name or "",
            "family_name": result.family_name or "",
            "original_name": result.name or "",
            "phone_no": result.phone_no or "",
            "id_value": result.id_value,
            "nrc": result.nrc or "",
            "fa_type": "BANK_ACCOUNT",
        }

        # Convert to JSON string for deconstructable format
        try:
            fa_json = orjson.dumps(fa_data).decode()
            return fa_json
        except Exception as e:
            _logger.error(f"Error constructing FA: {str(e)}")
            # Fallback to simple format if JSON encoding fails
            return f"name:{full_name},phone:{result.phone_no or 'N/A'},id:{result.id_value},nrc:{result.nrc or 'N/A'},fa_type:BANK_ACCOUNT"

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
                    # Create subquery for NRC (id_type = 2)
                    nrc_subquery = (
                        select(G2PRegistrantID.value.label("nrc_value"))
                        .where(G2PRegistrantID.partner_id == ZambiaRegistry.id)
                        .where(G2PRegistrantID.id_type == 2)
                        .limit(1)
                        .scalar_subquery()
                    )

                    query = (
                        select(
                            G2PRegistrantID.value.label("id_value"),
                            ZambiaRegistry.name,
                            ZambiaRegistry.family_name,
                            ZambiaRegistry.given_name,
                            G2PPhoneNumber.phone_no,
                            ZambiaRegistry.id.label("partner_id"),
                            G2PPhoneNumber.date_collected,
                            nrc_subquery.label("nrc"),
                        )
                        .join(ZambiaRegistry, G2PRegistrantID.partner_id == ZambiaRegistry.id)
                        .outerjoin(G2PPhoneNumber, ZambiaRegistry.id == G2PPhoneNumber.partner_id)
                        .where(G2PRegistrantID.value.in_(beneficiary_ids))
                        .where(ZambiaRegistry.is_registrant)
                        .where(
                            (G2PPhoneNumber.disabled.is_(None)) | (G2PPhoneNumber.id.is_(None))
                        )  # Include records even if no phone number exists
                        .order_by(G2PRegistrantID.value, G2PPhoneNumber.date_collected.desc())
                    )

                    # Execute bulk query
                    results = registry_session.execute(query).fetchall()
                    _logger.info(f"Bulk query returned {len(results)} results")

                    # Group results by ID and keep only the most recent phone number per ID
                    id_to_result_map = {}
                    for result in results:
                        id_value = result.id_value
                        if id_value not in id_to_result_map:
                            # First result for this ID (most recent phone due to ORDER BY)
                            id_to_result_map[id_value] = result

                    # Process all requested IDs and construct responses
                    for beneficiary_id in beneficiary_ids:
                        single_request = id_to_request_map[beneficiary_id]

                        if beneficiary_id in id_to_result_map:
                            result = id_to_result_map[beneficiary_id]

                            # Construct full name from available parts
                            name_parts = []
                            if result.given_name:
                                name_parts.append(result.given_name)
                            if result.family_name:
                                name_parts.append(result.family_name)

                            # Use constructed name if available, otherwise fall back to main name field
                            full_name = " ".join(name_parts) if name_parts else result.name

                            # Construct FA with all beneficiary details in deconstructable format
                            fa_value = self._construct_fa(result)

                            _logger.debug(f"Found beneficiary: {full_name} with phone: {result.phone_no}")

                            resolve_responses.append(
                                SingleResolveResponse(
                                    reference_id=single_request.reference_id,
                                    timestamp=datetime.now(),
                                    id=result.id_value,
                                    fa=fa_value,  # Add the constructed FA
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

        # Construct the response
        resolve_response = ResolveResponse(
            message=ResolveResponseMessage(
                transaction_id=resolve_request.message.transaction_id, resolve_response=resolve_responses
            )
        )

        _logger.info(f"Returning resolve response: {resolve_response}")
        return resolve_response
