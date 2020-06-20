from flask import Flask
from flask_script import Manager
from common import get_logger

from .config import *
from .api.blueprint import api
from .client.blueprint import client


app = Flask(__package__)
app.config.from_object(Config)
app.register_blueprint(api, url_prefix='/api/v1/')
app.register_blueprint(client, url_prefix='/client/')

manager = Manager(app)
logger = get_logger(__package__, LOG_FILE)
