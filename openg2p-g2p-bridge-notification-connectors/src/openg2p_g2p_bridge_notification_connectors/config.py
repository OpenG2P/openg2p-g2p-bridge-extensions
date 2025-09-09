from openg2p_fastapi_common.config import Settings as BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="g2p_bridge_notification_connectors_", env_file=".env", extra="allow"
    )

    novu_url: str = "http://localhost:3000"
    novu_api_key: str = "149f3f3dff5493729136246b9454f315"
    novu_warehouse_workflow_id: str = "warehouse-notification"
    novu_agency_workflow_id: str = "agency-notification"
    novu_beneficiary_workflow_id: str = "beneficiary-notification"
