from openg2p_fastapi_common.config import Settings as BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="g2p_bridge_mapper_connectors_", env_file=".env", extra="allow"
    )

    # SPAR Mapper configuration
    spar_mapper_url: str = "http://localhost:8000/mapper/resolve"
    spar_mapper_api_sign_enabled: bool = True
    spar_mapper_api_sign_crypto_helper_name: str = "spar_mapper_crypto"
