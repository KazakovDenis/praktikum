import os.path as op


__all__ = 'ROOT', 'ES_HOSTS', 'DB_ADDRESS', 'JSON_DIR'

ROOT = op.abspath(op.curdir)
ES_HOSTS = ['http://127.0.0.1:9200']
DB_ADDRESS = op.join(ROOT, 'practice', 'sprint_1', 'db.sqlite')
JSON_DIR = op.join(ROOT, 'practice', 'sprint_1')
