# ruff: noqa: E402


from openg2p_fastapi_common.app import Initializer as BaseInitializer
from openg2p_fastapi_common.utils.crypto import KeymanagerCryptoHelper

from .factory import MapperFactory
from .implementations import SPARMapper
from .client import SPARMapperClient


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        MapperFactory()
        SPARMapperClient()
        SPARMapper()
        KeymanagerCryptoHelper()

