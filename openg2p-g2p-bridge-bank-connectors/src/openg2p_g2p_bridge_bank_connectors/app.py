# ruff: noqa: E402

from .config import Settings

_config = Settings.get_config()

from openg2p_fastapi_common.app import Initializer as BaseInitializer

from .bank_connectors import BankConnectorFactory, ExampleBankConnector


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        BankConnectorFactory()
        ExampleBankConnector()
