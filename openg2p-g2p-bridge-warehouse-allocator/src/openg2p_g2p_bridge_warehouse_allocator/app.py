# ruff: noqa: E402


from openg2p_fastapi_common.app import Initializer as BaseInitializer

from .factory import WarehouseAllocatorFactory
from .implementations import WarehouseAllocatorRefImpl


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        WarehouseAllocatorFactory()
        WarehouseAllocatorRefImpl()
