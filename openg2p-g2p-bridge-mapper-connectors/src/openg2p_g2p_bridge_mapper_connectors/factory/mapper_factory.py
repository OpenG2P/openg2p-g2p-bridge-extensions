from openg2p_fastapi_common.service import BaseService

from ..implementations.spar_mapper import SPARMapper
from ..interface.mapper_interface import MapperInterface


class MapperFactory(BaseService):
    @staticmethod
    def get_mapper() -> MapperInterface:
        return SPARMapper.get_component()
