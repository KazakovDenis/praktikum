import os.path as op


ROOT = op.abspath(op.curdir)
ES_HOSTS = ['http://127.0.0.1:9200']
ETL_DIR = op.join(ROOT, 'practice', 'sprint_1', 'etl')

SEARCH_SRV_DIR = op.join(ROOT, 'search_service')
SEARCH_SRV_URL = 'http://127.0.0.1:8000'
