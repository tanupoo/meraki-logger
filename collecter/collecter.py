#!/usr/bin/env python

import sys
import asyncio
from set_config import set_config
from api import api

def log_start(config):
    config.logger.info("Starting collector")

if __name__ == "__main__":
    from uvicorn import Config, Server
    loop = asyncio.new_event_loop()
    config = set_config("server", loop, sys.argv[1:])
    log_start(config)
    loop.run_until_complete(api(config))
else:
    loop = asyncio.new_event_loop()
    config = set_config("server", loop)
    log_start(config)
    app = api(config)


