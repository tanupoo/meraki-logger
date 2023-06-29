from pydantic import BaseModel, Extra
from pydantic import validator
from typing import Any

class ConfigModel(BaseModel):
    enable_debug: bool = False
    collect_interval: int = 300
    mongo_db_name: str
    mongo_table_name: str
    mongo_url: str = "mongodb://127.0.0.1:27017/apitest?retryWrites=true&w=majority"
    pg_db_name: str
    pg_table_name: str
    pg_username: str
    pg_password: str
    log_file: str | None
    log_stdout: bool = False
    syslog_address: str | None
    syslog_port: int = 514
    tz: str = "Asia/Tokyo"
    logger: Any
    loop: Any

    class Config():
        extra = Extra.forbid

