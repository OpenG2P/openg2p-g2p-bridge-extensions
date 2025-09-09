from openg2p_fastapi_common.service import BaseService

from ..implementations import AgencyAllocatorRefImpl
from ..interface import AgencyAllocator


class AgencyAllocatorFactory(BaseService):
    @staticmethod
    def get_agency_allocator() -> AgencyAllocator:
        return AgencyAllocatorRefImpl.get_component()
