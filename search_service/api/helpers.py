from typing import Any
from flask import request


def check_type(var: Any, target: type, default: Any = None) -> Any:
    """Check that type of variable is appropriate
    :param var: variable to check
    :param target: type that should be
    :param default: default variable value
    :returns target type instance
    """
    if isinstance(var, target):
        return var
    elif default:
        return default
    else:
        return target()


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
