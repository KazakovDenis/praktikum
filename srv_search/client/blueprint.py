from flask import Blueprint, jsonify, request
from ..app import logger


client = Blueprint('client', __name__)


@client.route('info', methods=['GET'])
def info():
    """Returns client's user agent"""
    logger.info(f'{request.method} request FROM: {request.remote_addr}')
    user_agent = request.user_agent.to_header()
    return jsonify(user_agent=user_agent)
