import os


ROOT = os.path.abspath(os.curdir)
LOG_LEVEL = 30
LOG_FORMAT = "[%(asctime)s] @%(name)s  %(levelname)s in %(module)s: %(message)s"


class Config:
    DEBUG = False
