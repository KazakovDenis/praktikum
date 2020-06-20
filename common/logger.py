from logging import getLogger, Logger, FileHandler, Formatter
import os


# defaults
LOG_LEVEL = 20
LOG_DIR = os.path.join(os.curdir, 'log')
LOG_FORMAT = "[%(asctime)s] @%(name)s  %(levelname)s in %(module)s: %(message)s"
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str, file: str, fmt: str = LOG_FORMAT, level: int = LOG_LEVEL) -> Logger:
    """Creates a unified logger

    :param name: logger name
    :param file: output log file
    :param fmt: output format
    :param level: logging level
    :return: Logger object
    """
    logger = getLogger(name)
    handler = FileHandler(file, encoding='utf-8')
    logger.setLevel(level)
    handler.setLevel(level)
    handler.setFormatter(Formatter(fmt))
    logger.addHandler(handler)
    return logger
