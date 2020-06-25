from flask import Blueprint, request
from ..app import es, logger


api = Blueprint('api', __name__)


@api.route('movies')
def search():
    q = request.args.get('q')
    return '<h1>Movies endpoint</h1>'


@api.route('movies/<movie_id>')
def get_movie(movie_id):

    query = """{
        "query": {
            "term":  { "id": "%s" }
        }
    }""" % movie_id
    result = es.search(query, index='movies')
    return result['hits']['hits'][0]['_source']
