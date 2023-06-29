from pydantic import BaseModel, Extra
from pydantic import validator
from typing import Any

class ConfigModel(BaseModel):
    enable_debug: bool = False
    mongo_db_name: str
    mongo_table_name: str
    mongo_url: str = "mongodb://127.0.0.1:27017/apitest?retryWrites=true&w=majority"
    log_file: str | None
    log_stdout: bool = False
    syslog_address: str | None
    syslog_port: int = 514
    fastapi_address: str = "127.0.0.1"
    fastapi_port: int = "8888"
    fastapi_cert: str | None
    enable_tls: bool = False
    tz: str = "Asia/Tokyo"
    logger: Any
    loop: Any

    @validator("enable_tls", always=True)
    def update_enable_tls(cls, v, values, config, **kwargs):
        return True if values["fastapi_cert"] else False

    class Config():
        extra = Extra.forbid

