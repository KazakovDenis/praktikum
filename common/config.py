import os.path as op


__all__ = 'ROOT', 'ES_HOSTS', 'ETL_DIR'

ROOT = op.abspath(op.curdir)
ES_HOSTS = ['http://127.0.0.1:9200']
ETL_DIR = op.join(ROOT, 'practice', 'sprint_1', 'etl')
