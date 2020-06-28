from elasticsearch.exceptions import NotFoundError
from flask import Blueprint, jsonify, request

from ..app import es, logger
from .helpers import UrlArgument, get_movies


api = Blueprint('api', __name__)


@api.route('movies', methods=['GET'])
@api.route('movies/', methods=['GET'])
def movies():
    """Searches appropriate movies"""

    args = UrlArgument()

    # No arguments set
    if not args:
        return get_movies(es)

    query, limit, page, sort = args.get()
    status = args.status

    # Arguments have wrong values
    if status != 200:
        return jsonify([]), status

    result = get_movies(es, query, limit, page, sort)

    # No results for the query
    if not result:
        status = 404

    return result, status


@api.route('movies/<movie_id>', methods=['GET'])
def movie_detail(movie_id):
    """Looks for an info by movie id"""
    logger.info(f'{request.method} request FROM: {request.remote_addr}')
    try:
        response = es.get('movies', movie_id)['_source']
        return jsonify(result=response), 200
    except NotFoundError:
        logger.debug(f'Movie with id = {movie_id} not found')
        return jsonify(result='Not found'), 404
