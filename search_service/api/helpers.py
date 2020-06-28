from elasticsearch.exceptions import TransportError
from flask import request, jsonify


class UrlArgument:

    vocab = str.maketrans({'"': ''})
    fields = ('id', 'title', 'imdb_rating', 'description', 'director', 'actors', 'writers')

    def __init__(self):
        self.args = request.args
        self.status = 200

    def __bool__(self):
        return bool(self.args)

    def _extract(self, arg, target=None):

        target = target or str
        value = self.args.get(arg, '').strip()

        try:
            return target(value)
        except (ValueError, TypeError):
            return False

    def get(self):
        """Returns all expected URL arguments"""
        return (
            self.search(),
            self.limit(),
            self.page(),
            self.sort()
        )

    def limit(self):
        """Returns limit param to ES query"""
        limit = self._extract('limit', int)

        if limit < 0:
            self.status = 422
            return 50

        return limit

    def page(self):
        """Returns page param to ES query"""
        page = self._extract('page', int)

        if not page:
            return 1

        if page < 1:
            self.status = 422
            return 1

        return page

    def search(self):
        """Returns body to ES query"""

        query = {}
        contained_text = self._extract('search')

        if contained_text:
            query["query"] = {
                "multi_match": {
                    "query": contained_text,
                    "fields": ["title"],  # ["title", "description"],
                    # "fuzziness": "auto"
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
        if not field:
            return 'imdb_rating'

        field = field.translate(self.vocab)

        # wrong value
        if field not in self.fields:
            self.status = 422
            return False

        return field

    def sort_order(self):
        """Returns a sort order"""
        value = self._extract('sort_order')

        # not set
        if not value:
            return 'desc'

        order = value.translate(self.vocab)

        # wrong value
        if order not in ('asc', 'desc'):
            self.status = 422
            return False

        return order


def get_movies(client, query=None, limit=None, page=1, sort=None):
    """Looks for movies are relative to a query"""

    size = limit or 50
    from_ = size * (page - 1) or None
    sort = sort or 'imdb_rating:desc'

    try:
        response = client.search(
            query or {}, 'movies',
            filter_path=['hits.hits._source'],
            _source=['id', 'title', 'imdb_rating'],
            size=limit,
            from_=from_,
            sort=sort
        )
        results = response.get('hits', {}).get('hits', [])
    except TransportError:
        results = []

    return jsonify([r['_source'] for r in results])
