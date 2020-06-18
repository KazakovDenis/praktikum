import os


# common
ROOT = os.path.abspath(os.curdir)

# logger
LOG_LEVEL = 20
LOG_DIR = os.path.join(ROOT, 'log')
LOG_FILE = os.path.join(LOG_DIR, 'search_srv.log')
LOG_FORMAT = "[%(asctime)s] @%(name)s  %(levelname)s in %(module)s: %(message)s"
os.makedirs(LOG_DIR, exist_ok=True)


# app
class Config:
    DEBUG = True
