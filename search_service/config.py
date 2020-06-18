import os


# common
ROOT = os.path.abspath(os.curdir)

# logger
LOG_LEVEL = 30
LOG_FILE = os.path.join(ROOT, '..', 'log', 'search_srv.log')
LOG_FORMAT = "[%(asctime)s] @%(name)s  %(levelname)s in %(module)s: %(message)s"
os.makedirs(LOG_FILE, exist_ok=True)


# app
class Config:
    DEBUG = False
