#!/usr/bin/env python

import sys
import asyncio
from set_config import set_config
from api import api

def log_start(config):
    config.logger.info("Starting collector listening on {}://{}:{}/"
                       .format("https" if config.fastapi_cert else "http",
                               config.fastapi_address if config.fastapi_address
                               else "*",
                               config.fastapi_port))

if __name__ == "__main__":
    from uvicorn import Config, Server
    loop = asyncio.new_event_loop()
    config = set_config("server", loop, sys.argv[1:])
    log_start(config)
    server = Server(Config(app=api(config),
                           host=config.fastapi_address,
                           port=config.fastapi_port,
                           ssl_certfile=config.fastapi_cert
                               if config.fastapi_cert else None,
                           loop=config.loop,
                           ))
    config.loop.run_until_complete(server.serve())
else:
    loop = asyncio.get_event_loop()
    config = set_config("server", loop)
    log_start(config)
    app = api(config)
