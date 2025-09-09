from sqlalchemy import create_engine

from .config import Settings

_config = Settings.get_config()


def construct_db_datasource(db_driver, db_username, db_password, db_hostname, db_port, db_dbname) -> str:
    datasource = ""
    if db_driver:
        datasource += f"{db_driver}://"
    if db_username:
        datasource += f"{db_username}:{db_password}@"
    if db_hostname:
        datasource += db_hostname
    if db_port:
        datasource += f":{db_port}"
    if db_dbname:
        datasource += f"/{db_dbname}"
    return datasource


def get_engine():
    db_datasource_pbms = construct_db_datasource(
        _config.db_driver_pbms,
        _config.db_username_pbms,
        _config.db_password_pbms,
        _config.db_hostname_pbms,
        _config.db_port_pbms,
        _config.db_dbname_pbms,
    )
    db_engine_pbms = create_engine(db_datasource_pbms)
    return {"db_engine_pbms": db_engine_pbms}
