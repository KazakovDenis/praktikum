from elasticsearch.exceptions import NotFoundError
from flask import Blueprint, jsonify, request
from ..app import es, logger


api = Blueprint('api', __name__)


@api.route('movies')
def search():
    q = request.args.get('q')
    return '<h1>Movies endpoint</h1>'


@api.route('movies/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Looks for movie by id"""
    logger.info(f'{request.method} request FROM: {request.remote_addr}')
    try:
        response = es.get('movies', movie_id)['_source']
        return jsonify(result=response), 200
    except NotFoundError:
        logger.debug(f'Movie with id = {movie_id} not found')
        return jsonify(result='Not found'), 404
