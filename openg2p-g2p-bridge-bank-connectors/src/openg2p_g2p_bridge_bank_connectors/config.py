from openg2p_fastapi_common.config import Settings as BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="g2p_bridge_bank_connectors_", env_file=".env", extra="allow"
    )

    db_dbname: str = "openg2p_g2p_bridge_db"


    funds_available_check_url_example_bank: str = (
        "https://example-bank.dev.openg2p.org/api/example-bank/check_funds"
    )
    funds_block_url_example_bank: str = "https://example-bank.dev.openg2p.org/api/example-bank/block_funds"
    funds_disbursement_url_example_bank: str = (
        "https://example-bank.dev.openg2p.org/api/example-bank/initiate_payment"
    )
    bank_simulator_code: str = "EXAMPLE-BANK"