from logging import getLogger, FileHandler, Formatter
from ..config import LOG_LEVEL, LOG_FILE, LOG_FORMAT


logger = getLogger('search_service')
handler = FileHandler(LOG_FILE, encoding='utf-8')
logger.setLevel(LOG_LEVEL)
handler.setLevel(LOG_LEVEL)
handler.setFormatter(Formatter(LOG_FORMAT))
logger.addHandler(handler)
