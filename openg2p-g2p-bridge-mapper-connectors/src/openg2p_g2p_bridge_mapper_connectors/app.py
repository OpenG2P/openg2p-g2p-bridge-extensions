# ruff: noqa: E402


from openg2p_fastapi_common.app import Initializer as BaseInitializer

from .factory import MapperFactory
from .implementations.zambia_mapper import ZambiaMapper


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        MapperFactory()
        ZambiaMapper()
