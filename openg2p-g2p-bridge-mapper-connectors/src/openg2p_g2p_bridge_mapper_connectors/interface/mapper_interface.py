from typing import List

from openg2p_fastapi_common.service import BaseService

from ..schemas import ResolveRequest, ResolveResponse


class MapperInterface(BaseService):
    def resolve(self, resolve_request: ResolveRequest) -> List[ResolveResponse] | None:
        """
        Resolve the given request from Mapper and return the list of Responses.
        """
        pass
