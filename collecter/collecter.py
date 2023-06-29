#!/usr/bin/env python

import sys
import asyncio
from set_config import set_config
from main import do_main

__prog = "collector"

def log_start(config):
    config.logger.info(f"Starting {__prog}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    config = set_config(__prog, loop, sys.argv[1:])
    log_start(config)
    loop.run_until_complete(do_main(config))

