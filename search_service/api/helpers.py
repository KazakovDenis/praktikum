from flask import request
from common import check_type


def get_search_args() -> tuple:
    """Extracts args from query string and converts it to ElasticSearch query format"""
    get = request.args.get

    # search query
    contained_text = check_type(get('search'), str)
    query = {
        "query": {
            "match": {
                "title": {"query": contained_text, "fuzziness": "auto"}
            }
        },
    } if contained_text else {}

    # sorting
    vocab = str.maketrans({'"': ''})
    sort_field = check_type(get('sort'), str, default='imdb_rating').translate(vocab)
    sort_order = check_type(get('sort_order'), str, default='desc').translate(vocab)
    sort = f'{sort_field}:{sort_order}'

    # pagination
    limit = check_type(get('limit'), int, default=10)
    page = check_type(get('page'), int, default=1)

    return query, sort, limit, page
