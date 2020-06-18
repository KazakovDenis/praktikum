from flask import Flask
from flask_script import Manager

from .config import *


app = Flask(__name__)
app.config.from_object(Config)
manager = Manager(app)
