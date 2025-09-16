from openg2p_fastapi_common.service import BaseService

from ..bank_interface.bank_connector_interface import BankConnectorInterface
from ..config import Settings
from .zambia_csv_connector import ZambiaCSVConnector

_config = Settings.get_config()


class BankConnectorFactory(BaseService):
    def get_bank_connector(self, sponsor_bank_code: str) -> BankConnectorInterface:
        return ZambiaCSVConnector.get_component()
