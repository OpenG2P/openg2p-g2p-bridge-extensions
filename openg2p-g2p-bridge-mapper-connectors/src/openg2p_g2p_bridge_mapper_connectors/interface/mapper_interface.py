from openg2p_fastapi_common.service import BaseService

from ..schemas import ResolveRequest, ResolveResponse


class MapperInterface(BaseService):
    async def resolve(self, resolve_request: ResolveRequest) -> ResolveResponse | None:
        """
        Resolve the given request from Mapper and return the Response.
        """
        pass
