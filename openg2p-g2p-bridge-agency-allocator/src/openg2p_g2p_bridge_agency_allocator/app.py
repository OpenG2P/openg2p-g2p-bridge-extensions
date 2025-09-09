# ruff: noqa: E402


from openg2p_fastapi_common.app import Initializer as BaseInitializer

from .factory import AgencyAllocatorFactory
from .implementations import AgencyAllocatorRefImpl


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        AgencyAllocatorFactory()
        AgencyAllocatorRefImpl()
