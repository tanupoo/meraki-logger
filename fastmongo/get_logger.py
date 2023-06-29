import logging
from logging.handlers import SysLogHandler

LOG_FORMAT = "%(asctime)s.%(msecs)d %(lineno)d %(levelname)s %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

def get_logger(prog_name=None, logfile=None, stdout=False, syslog=None,
               debug=False):
    """
    logfile: a file name for logging.
    stdout: False, or True,
    syslog: None, or syslog server's address and port. i.e. ( "addr", port )
    debug: set log level to DEBUG, otherwise set to INFO.
    """
    def get_logging_handler(channel):
        channel.setFormatter(logging.Formatter(fmt=LOG_FORMAT,
                                               datefmt=LOG_DATE_FORMAT))
        if debug:
            channel.setLevel(logging.DEBUG)
        else:
            channel.setLevel(logging.INFO)
        return channel
    # set logger.
    logger = logging.getLogger(prog_name)
    if logfile is not None:
        logger.addHandler(get_logging_handler(logging.FileHandler(logfile)))
    if stdout is True:
        logger.addHandler(get_logging_handler(logging.StreamHandler()))
    if syslog is not None:
        logger.addHandler(SysLogHandler(address=syslog))

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.info("enabled DEBUG mode")
    else:
        logger.setLevel(logging.INFO)

    if stdout is True:
        logger.addHandler(get_logging_handler(logging.StreamHandler()))
    if logfile is not None:
        logger.addHandler(get_logging_handler(logging.FileHandler(logfile)))
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("DEBUG mode")
    else:
        logger.setLevel(logging.INFO)
    return logger

