from openg2p_fastapi_common.service import BaseService

from ..implementations import WarehouseAllocatorRefImpl
from ..interface import WarehouseAllocator


class WarehouseAllocatorFactory(BaseService):
    def get_warehouse_allocator(self) -> WarehouseAllocator:
        return WarehouseAllocatorRefImpl.get_component()
