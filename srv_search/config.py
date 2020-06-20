import os
from common import LOG_DIR


# logger
LOG_LEVEL = 20
LOG_FILE = os.path.join(LOG_DIR, 'search_srv.log')


# app
class Config:
    DEBUG = True
