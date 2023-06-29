from argparse import ArgumentParser
import json
from get_logger import get_logger
from os import environ
from config_model import ConfigModel

def set_config(prog_name, loop, args=None):
    def get_env_bool(optval, envkey):
        c = environ.get(envkey)
        if c is None:
            return optval
        elif c.upper() in [ "TRUE", "1" ]:
            return True
        elif c.upper() in [ "FALSE", "0" ]:
            return False
        else:
            raise ValueError(f"ERROR: {key} must be bool, but {c}")

    """
    priority order
        1. cli arguments.
        2. environment variable.
        3. config file.
    """
    if args is not None:
        ap = ArgumentParser()
        ap.add_argument("config_file", metavar="CONFIG_FILE",
                        help="specify the config file.")
        ap.add_argument("-d", action="store_true", dest="enable_debug",
                        help="enable debug mode.")
        ap.add_argument("-D", action="store_true", dest="log_stdout",
                        help="enable to show messages on the stdout.")
        opt = ap.parse_args(args)
        environ["__CONFIG_FILE"] = opt.config_file
        environ["__ENABLE_DEBUG"] = str(opt.enable_debug)
        environ["__LOG_STDOUT"] = str(opt.log_stdout)
    # load the config file.
    config_file = environ["__CONFIG_FILE"]
    try:
        config = ConfigModel.parse_obj(json.load(open(config_file)))
    except Exception as e:
        print("ERROR: {} read error. {}".format(config_file, e))
        exit(1)
    # set logger
    syslog_server = None
    if config.syslog_address is not None:
        syslog_server = (config.syslog_address,config.syslog_port)
    config.logger = get_logger(prog_name,
                              logfile=config.log_file,
                              stdout=config.log_stdout,
                              syslog=syslog_server,
                              debug=config.enable_debug)
    # overwrite the config by the cli options/env variable.
    get_env_bool(config.enable_debug, "__ENABLE_DEBUG")
    get_env_bool(config.log_stdout, "__LOG_STDOUT")
    config.loop = loop
    return config

