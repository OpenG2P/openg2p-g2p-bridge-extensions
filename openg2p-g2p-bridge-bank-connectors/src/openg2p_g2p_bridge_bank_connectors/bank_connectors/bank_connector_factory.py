from openg2p_fastapi_common.service import BaseService

from ..bank_interface.bank_connector_interface import BankConnectorInterface
from .example_bank_connector import ExampleBankConnector

from ..config import Settings

_config = Settings.get_config()

class BankConnectorFactory(BaseService):
    def get_bank_connector(self, sponsor_bank_code: str) -> BankConnectorInterface:
        if sponsor_bank_code == _config.bank_simulator_code:
            return ExampleBankConnector.get_component()
        else:
            raise NotImplementedError(f"Bank {sponsor_bank_code} is not supported. Supported bank: {_config.bank_simulator_code}")
