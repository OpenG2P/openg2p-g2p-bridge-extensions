from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_mapper_lib.schemas import ResolveRequest, ResolveResponse


class MapperInterface(BaseService):
    def resolve(
        self,
        resolve_request: ResolveRequest
    ) -> ResolveResponse | None:
        """
        Resolve the given request from Mapper and return the ResolveResponse.
        """
        pass
