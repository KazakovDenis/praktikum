from elasticsearch.exceptions import NotFoundError
from flask import Blueprint, jsonify, request

from ..app import es, logger
from ..utils import catch
from .utils import UrlArgValidator, get_movies


api = Blueprint('api', __name__)


@api.route('movies', methods=['GET'])
@api.route('movies/', methods=['GET'])
@catch
def movies():
    """Searches appropriate movies"""

    args = UrlArgValidator()

    # No arguments set
    if not args:
        return get_movies(es)

    # Arguments have wrong values
    if args.errors:
        return args.validation_details(), 422

    result = get_movies(es, *args)

    return result, (200 if result else 404)


@api.route('movies/<movie_id>', methods=['GET'])
@catch
def movie_detail(movie_id):
    """Looks for an info by movie id"""
    logger.info(f'{request.method} request FROM: {request.remote_addr}')

    try:
        response = es.get('movies', movie_id)['_source']
        return jsonify(response), 200

    except NotFoundError:
        logger.debug(f'Movie with id = {movie_id} not found')
        return jsonify('Movie not found'), 404
