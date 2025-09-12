# ruff: noqa: E402


from openg2p_fastapi_common.app import Initializer as BaseInitializer

from .factory import MapperFactory
from .implementations import SPARMapper


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        MapperFactory()
        SPARMapper()
