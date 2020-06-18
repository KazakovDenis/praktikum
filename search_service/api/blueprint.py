from flask import Blueprint


api = Blueprint('api', __name__)


@api.route('video')
def video():
    return '<h1>Video endpoint</h1>'
