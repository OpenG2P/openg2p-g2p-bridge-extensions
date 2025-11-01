import asyncio
import logging
from datetime import datetime

from openg2p_fastapi_common.schemas import G2PRequestHeader
from openg2p_spar_models.schemas.resolve import (
    ResolveRequest as SparResolveRequest,
    ResolveRequestBody,
    ResolveRequestPayload,
    ResolveResponse as SparResolveResponse,
    SingleResolveRequest,
)

from ..client import SPARMapperClient
from ..interface.mapper_interface import MapperInterface
from ..schemas import ResolveRequest, ResolveResponse, ResolveResult

_logger = logging.getLogger("spar_mapper_impl")


class SPARMapper(MapperInterface):
    def __init__(self):
        super().__init__()
        self.client = SPARMapperClient.get_component()

    async def resolve(self, resolve_request: ResolveRequest) -> ResolveResponse | None:
        """
        Resolve the given request from SPAR Mapper and return the result.

        Args:
            resolve_request: ResolveRequest object containing beneficiary_ids

        Returns:
            ResolveResponse object with a list of results (id, fa, name)
            or None if the request fails
        """
        _logger.info(
            f"Received resolve request with {len(resolve_request.beneficiary_ids)} disbursement IDs"
        )
        _logger.info(f"Disbursement IDs: {resolve_request.beneficiary_ids}")

        try:
            # Convert custom ResolveRequest to SPAR ResolveRequest
            spar_request = self._convert_to_spar_request(resolve_request)

            _logger.info(f"Converted to SPAR request with transaction_id: {spar_request.request_body.request_payload.transaction_id}")
        
            # Await the async resolve_request in an async context
            spar_resolve_response: SparResolveResponse = await self.client.resolve_request(spar_request)

            _logger.info("Resolve request completed successfully")
            _logger.info(
                f"Response status: {spar_resolve_response.response_header.response_status}, "
                f"Transaction ID: {spar_resolve_response.response_body.response_payload.transaction_id}"
                f"Response: {spar_resolve_response}"
            )

            # Convert SPAR ResolveResponse to custom ResolveResponse
            resolve_response = self._convert_from_spar_response(spar_resolve_response)

            _logger.info(f"Returning {len(resolve_response.results)} resolve results")
            return resolve_response

        except Exception as e:
            _logger.error(f"Failed to resolve the request: {e}", exc_info=True)
            return None

    def _convert_to_spar_request(self, resolve_request: ResolveRequest) -> SparResolveRequest:
        """
        Convert custom ResolveRequest to SPAR ResolveRequest.

        Args:
            resolve_request: Custom ResolveRequest with beneficiary_ids

        Returns:
            SparResolveRequest with full G2P structure
        """
        # Create SingleResolveRequest for each disbursement ID
        # Note: SPAR schema has id and fa as strings, not lists
        single_resolve_requests = [
            SingleResolveRequest(
                reference_id=disbursement_id,
                timestamp=datetime.now().isoformat(),  # timestamp is a string in SPAR schema
                id=disbursement_id,  # id is a string field
                fa="",  
                scope="details",  # Default scope
                locale="en",
            )
            for disbursement_id in resolve_request.beneficiary_ids
        ]

        # Create the request payload
        request_payload = ResolveRequestPayload(
            transaction_id=f"txn_{int(datetime.now().timestamp())}",
            resolve_request=single_resolve_requests,
        )

        # Create the request body
        request_body = ResolveRequestBody(request_payload=request_payload)

        # Create the request header
        request_header = G2PRequestHeader(
            sender_app_mnemonic="g2p_bridge",
            sender_app_url="",
            request_id=f"req_{int(datetime.now().timestamp())}",
            request_timestamp=datetime.now(),
        )

        # Create the full SPAR request
        spar_request = SparResolveRequest(
            request_header=request_header,
            request_body=request_body,
        )

        return spar_request

    def _convert_from_spar_response(
        self, spar_response: SparResolveResponse
    ) -> ResolveResponse:
        """
        Convert SPAR ResolveResponse to custom ResolveResponse.

        Args:
            spar_response: SPAR ResolveResponse with full G2P structure

        Returns:
            ResolveResponse object with a list of results
        """
        results = []

        for single_response in spar_response.response_body.response_payload.resolve_response:
            id_value = single_response.id

            fa_value = single_response.fa

            name_value = single_response.account_provider_info.name if single_response.account_provider_info else None

            result = ResolveResult(
                id=id_value,
                fa=fa_value,
                name=name_value,
            )

            results.append(result)

            _logger.debug(
                f"Converted result: id={id_value}, fa={fa_value}, name={name_value}, "
                f"status={single_response.status}, status_reason={single_response.status_reason_code}"
            )

        return ResolveResponse(results=results)
