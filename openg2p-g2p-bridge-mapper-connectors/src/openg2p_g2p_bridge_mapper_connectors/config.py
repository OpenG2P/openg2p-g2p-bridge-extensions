from openg2p_fastapi_common.config import Settings as BaseSettings
from pydantic_settings import SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="g2p_bridge_mapper_connectors_", env_file=".env", extra="allow"
    )

    # registry database connection settings
    db_driver_registry: str = "postgresql"
    db_username_registry: str = "postgres"
    db_password_registry: str = "postgres"
    db_hostname_registry: str = "localhost"
    db_port_registry: int = 5432
    db_dbname_registry: str = "registrydb"
