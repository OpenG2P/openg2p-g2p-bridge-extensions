from openg2p_fastapi_common.service import BaseService

from ..implementations.zambia_mapper import ZambiaMapper
from ..interface.mapper_interface import MapperInterface


class MapperFactory(BaseService):
    @staticmethod
    def get_mapper() -> MapperInterface:
        return ZambiaMapper.get_component()
