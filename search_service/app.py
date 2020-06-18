from flask import Flask
from flask_script import Manager

from .config import *
from .client.blueprint import client


app = Flask('Search service')
app.config.from_object(Config)
app.register_blueprint(client, url_prefix='/client/')

manager = Manager(app)
