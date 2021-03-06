from elasticsearch.exceptions import NotFoundError
from flask import Blueprint, jsonify, request

from ..app import es, logger
from ..utils import catch
from .utils import UrlArgValidator, get_movies


api = Blueprint('api', __name__)


@api.route('movies/', methods=['GET'])
@catch
def movies():
    """Looks for relevant movies"""

    args = UrlArgValidator()

    if not args:
        return get_movies(es), 200

    if args.errors:
        return args.validation_details(), 422

    if args.excess:
        return args.unsupported(), 400

    result = get_movies(es, **args.values)

    return result, (200 if result.json else 404)


@api.route('movies/<movie_id>', methods=['GET'])
@catch
def movie_detail(movie_id):
    """Looks for all information about the movie by id"""

    logger.info(f'{request.method} request FROM: {request.remote_addr}')

    args = UrlArgValidator(expected=())
    if args:
        return args.unsupported(), 400

    response, status = 'Movie not found', 404

    try:
        response = es.get(
            'movies', movie_id, _source_excludes=['actors_names', 'writers_names']
        )['_source']
        status = 200
    except NotFoundError:
        logger.debug(f'Movie with id = {movie_id} not found')

    return jsonify(response), status
