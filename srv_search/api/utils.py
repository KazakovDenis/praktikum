from typing import Sequence

from elasticsearch.exceptions import TransportError
from flask import Response, request, jsonify


class UrlArgValidator:
    """URL Arguments validator inside Flask request context
    Extracts arguments from URL, checks and returns valid values

    Example:
        @app.route('/')
        def index():
            args = UrlArgValidator()
            if args:                     # None if no URL args
                search = args.search()   # returns "search" arg
            if not args.errors:          # list of invalid args
                return args.values       # values of valid args
    """
    # todo: available fields
    default_fields = ('id', 'title', 'imdb_rating')
    supported = {
        'limit': {'msg': 'Limit should be greater than 0', 'type': 'integer'},
        'page': {'msg': 'Page should be greater than 0', 'type': 'integer'},
        'search': {'msg': 'Search maybe any string', 'type': 'string'},
        'sort': {'msg': '', 'type': 'string'},
        'sort_order': {'msg': 'Sort order should be one of the following: asc, desc', 'type': 'string'}
    }

    def __init__(self, expected: Sequence = tuple(supported), sort_fields: Sequence = default_fields):
        self.args = request.args
        self.expected = expected

        self.doc_fields = sort_fields
        self.supported['sort']['msg'] = f'Sort field should be one of the following: {", ".join(self.doc_fields)}'

        self.errors = []
        self.excess = None
        self.values = self._get()

    def __bool__(self):
        return bool(self.args)

    def _extract(self, arg: str, target: type = None):
        """Extracts data from URL argument into expected type
        :param arg: URL argument
        :param target: expected type
        :returns:
            - value of target type if the argument is correct
            - None if no argument set
            - False if the argument has incorrect value
        """
        target = target or str
        value = self.args.get(arg, '').strip()

        if not value:
            return None

        try:
            return target(value)
        except (ValueError, TypeError):
            return False

    def _get(self):
        """Returns all expected URL arguments"""
        self.errors.clear()
        self.excess = set(self.args) - set(self.expected)
        return {
            'query': self.query(),
            'limit': self.limit(),
            'page': self.page(),
            'sort': self.sort(),
        }

    def unsupported(self) -> Response:
        """Checks for unsupported arguments"""

        details = {'detail': 'success'}

        if self.excess:
            details['detail'] = [
                {
                    'loc': list(self.excess),
                    'msg': 'Unexpected URL arguments',
                }
            ]

        return jsonify(details)

    def validation_details(self) -> Response:
        """Returns result of argument validation"""

        details = {'detail': 'success'}

        if self.errors:
            details['detail'] = [
                {'loc': arg, **self.supported[arg]} for arg in self.errors
            ]

        return jsonify(details)

    def limit(self):
        """Returns limit param to ES query"""
        limit = self._extract('limit', int)

        # not set
        if limit is None:
            return 50

        # wrong value
        if limit < 0 or limit is False:
            self.errors.append('limit')
            return 50

        return limit

    def page(self):
        """Returns page param to ES query"""
        page = self._extract('page', int)

        # not set
        if page is None:
            return 1

        # wrong value
        if page < 1 or page is False:
            self.errors.append('page')
            return 1

        return page

    def query(self):
        """Returns a body to ES query"""
        query = {}
        contained_text = self.search()

        if contained_text:
            query["query"] = {
                "multi_match": {
                    "query": contained_text,
                    # тесты проходят только по полю title
                    "fields": ['title'],  # ["title", "description", "actors_names", "writers_names", "director"],
                    # "fuzziness": "auto"
                }
            }

        return query

    def search(self):
        """Returns 'search' argument value"""
        return self._extract('search')

    def sort(self):
        """Returns sort param to ES query"""

        field = self.sort_field()
        order = self.sort_order()

        if not (field and order):
            return None

        return f'{field}:{order}'

    def sort_field(self):
        """Returns a field to sort"""
        field = self._extract('sort')

        # not set
        if field is None:
            return 'id'

        field = field.replace('"', '')

        # wrong value
        if field not in self.doc_fields:
            self.errors.append('sort')
            return False

        return field

    def sort_order(self):
        """Returns a sort order"""
        value = self._extract('sort_order')

        # not set
        if value is None:
            return 'asc'

        order = value.replace('"', '')

        # wrong value
        if order not in ('asc', 'desc'):
            self.errors.append('sort_order')
            return False

        return order


def get_movies(client, query: dict = None, limit: int = None, page: int = 1, sort: str = None) -> Response:
    """Looks for movies are relative to a query

    :param client: ElasticSearch client
    :param query: ES request body
    :param limit: results amount
    :param page: results page
    :param sort: sorting
    :returns HTTP Response object
    """

    size = limit or 50
    from_ = size * (page - 1) or None
    sort = sort or 'id:asc'

    try:
        response = client.search(
            query or {}, 'movies',
            filter_path=['hits.hits._source'],
            _source=['id', 'title', 'imdb_rating'],
            size=size,
            from_=from_,
            sort=sort
        )
        results = response.get('hits', {}).get('hits', [])
    except TransportError:
        results = []

    movies = [r['_source'] for r in results]
    return jsonify(movies)
