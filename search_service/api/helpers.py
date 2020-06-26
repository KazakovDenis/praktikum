from flask import request


def check_type(var, target_type: type):

    if isinstance(var, target_type):
        return var
    else:
        return target_type()


def get_search_args() -> tuple:
    """Extracts args from query string and converts it to ElasticSearch query format"""

    # convert
    title = request.args.get('search', '')
    query = {
        "query": {
            "match": {
                "title": {
                    "query": title,
                    "fuzziness": "auto"
                }
            }
        },
    } if title else {}

    # todo: type check
    vocab = str.maketrans({'"': ''})
    sort_field = request.args.get('sort', 'imdb_rating').translate(vocab)
    sort_order = request.args.get('sort_order', 'desc').translate(vocab)

    # result
    sort = f'{sort_field}:{sort_order}'
    limit = int(request.args.get('limit', 10))
    page = int(request.args.get('page', 1))

    return query, sort, limit, page
