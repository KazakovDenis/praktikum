import json
from flask import Blueprint, Response, request
from ..app import logger


client = Blueprint('client', __name__)


@client.route('info')
def info():
    logger.info(f'REQUEST FROM: {request.remote_addr}')
    user_agent = request.user_agent.to_header()
    content = json.dumps({'user_agent': user_agent})
    response = Response(content, content_type='application/json')
    return response
