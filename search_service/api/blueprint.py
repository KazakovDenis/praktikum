from elasticsearch.exceptions import NotFoundError
from flask import Blueprint, jsonify, request

from ..app import es, logger
from .helpers import get_search_args


api = Blueprint('api', __name__)


@api.route('movies', methods=['GET'])
def search():
    """Search """
    query, sort, limit, page = get_search_args()

    results = es.search(
        query, 'movies',
        filter_path=['hits.hits._source'],
        _source=['id', 'title', 'imdb_rating'],
        size=limit,
        from_=limit * page,
        sort=sort
    ).get('hits', {}).get('hits', [])

    return jsonify([r['_source'] for r in results])


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
