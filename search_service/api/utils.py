from elasticsearch.exceptions import TransportError
from flask import Response, request, jsonify


class UrlArgValidator:

    vocab = str.maketrans({'"': ''})
    fields = ('id', 'title', 'imdb_rating')    # 'description', 'director', 'actors_names', 'writers_names'

    def __init__(self):
        self.args = request.args
        self.values = self._get()
        self.errors = []

    def __bool__(self):
        return bool(self.args)

    def __iter__(self):
        return iter(self.values)

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
        return (
            self.search(),
            self.limit(),
            self.page(),
            self.sort()
        )

    def validation_details(self) -> Response:
        """Returns result of argument validation"""

        details = {}

        if self.errors:
            details["detail"] = [
                {
                    "loc": self.errors,
                    # todo: msg & type
                    "msg": "value is not a valid integer",
                    "type": "type_error.integer"
                }
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

    def search(self):
        """Returns a body to ES query"""

        query = {}
        contained_text = self._extract('search')

        if contained_text:
            query["query"] = {
                "multi_match": {
                    "query": contained_text,
                    "fields": ["title", "description", "actors_names", "writers_names", "director"],
                    "fuzziness": "auto"
                }
            }

        return query

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

        field = field.translate(self.vocab)

        # wrong value
        if field not in self.fields:
            self.errors.append('sort')
            return False

        return field

    def sort_order(self):
        """Returns a sort order"""
        value = self._extract('sort_order')

        # not set
        if value is None:
            return 'asc'

        order = value.translate(self.vocab)

        # wrong value
        if order not in ('asc', 'desc'):
            self.errors.append('sort_order')
            return False

        return order


def get_movies(client, query=None, limit=None, page=1, sort=None) -> Response:
    """Looks for movies are relative to a query"""

    size = limit or 50
    from_ = size * (page - 1) or None
    sort = sort or 'imdb_rating:desc'

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
