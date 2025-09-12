import logging

from openg2p_g2pconnect_mapper_lib.client import MapperResolveClient
from openg2p_g2pconnect_mapper_lib.schemas import ResolveRequest, ResolveResponse

from ..config import Settings
from ..interface.mapper_interface import MapperInterface

_config = Settings.get_config()
_logger = logging.getLogger("spar_mapper_impl")


class SPARMapper(MapperInterface):
    def resolve(self, resolve_request: ResolveRequest) -> ResolveResponse | None:
        """
        Resolve the given request from Mapper and return the result.
        """
        _logger.info(f"Received resolve request: {resolve_request}")
        resolve_client = MapperResolveClient.get_component()
        try:
            resolve_response = resolve_client.resolve_request(resolve_request)
            _logger.info("Resolve request completed successfully")
        except Exception as e:
            _logger.error(f"Failed to resolve the request: {e}")
            return None

        _logger.info(f"Returning resolve response: {resolve_response}")
        return resolve_response
