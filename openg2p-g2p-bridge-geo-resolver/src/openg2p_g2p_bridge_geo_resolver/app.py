# ruff: noqa: E402

from .config import Settings

_config = Settings.get_config()

from openg2p_fastapi_common.app import Initializer as BaseInitializer

from .factory import GeoResolutionFactory
from .implementations import FarmerGeoResolverImpl


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        GeoResolutionFactory()
        FarmerGeoResolverImpl()
