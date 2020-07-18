"""
A module with a creator of targets for Vegeta
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import choice, shuffle
from sqlite3 import connect
from string import Template
from typing import AnyStr, Dict, Union, List, Iterator, Iterable
from urllib.parse import urlencode, urlparse, urlunparse, urljoin

from common import op, SEARCH_SRV_DIR, SEARCH_SRV_URL
from practice.sprint_1.etl.etl_requests import DB_ADDRESS, MovieDataExtractor


@dataclass
class VegetaTarget:
    url: str
    headers: Union[Dict[str, str], str] = ''
    body: AnyStr = ''


class VegetaTargetFactory(ABC):
    """A class to create VegetaTarget object"""

    def __init__(self, headers: Union[Dict[str, str], str] = '', body: AnyStr = ''):
        self.headers = headers
        self.body = body
        self.params: List[str] = []

    def create(self, add_args: Dict[str, Iterable] = None) -> VegetaTarget:
        """Creates a target object
        :param add_args: additional arguments {'name': ['values']}
        """
        self.update_params()

        if add_args and isinstance(add_args, dict):
            for key, values in add_args.items():
                self._add_random(key, values)
        elif not isinstance(add_args, dict):
            raise ValueError('Additional arguments should be of dict type')

        url = self._get_url_params()
        headers = self._get_headers()
        body = self._get_body()

        return VegetaTarget(url, headers, body)

    @abstractmethod
    def update_params(self):
        """Fills self.params to create query string"""

    def _add_random(self, name, values):
        """Appends random url argument to self.params
        :param name: a name of URL parameter
        :param values: values to choose one from
        """
        if value := choice(values):
            arg = urlencode({name: value})
            self.params.append(arg)

    def _get_body(self) -> str:
        # not implemented
        return self.body

    def _get_headers(self) -> str:
        # not implemented
        return self.headers

    def _get_url_params(self) -> str:
        """Returns URL query string"""
        return '?' + '&'.join(self.params)


class SearchServiceTargetFactory(VegetaTargetFactory):
    """A class to create VegetaTarget object for Full text search service"""

    def update_params(self):
        """Fills self.params to create query string"""
        self.params.clear()
        self._add_search()
        self._add_limit()
        self._add_page()
        self._add_sort()
        self._add_sort_order()

    def _add_limit(self):
        """Adds pages limit argument"""
        values = (None, 10, 20, 50)
        self._add_random('limit', values)

    def _add_page(self):
        """Adds page number argument"""
        values = (None, 3, 7, 15)
        self._add_random('page', values)

    def _add_sort(self):
        """Adds sorting argument"""
        values = (None, 'id', 'title', 'imdb_rating')
        self._add_random('sort', values)

    def _add_sort_order(self):
        """Adds sort order argument"""
        values = (None, 'asc', 'desc')
        self._add_random('sort_order', values)

    def _add_search(self):
        """Adds search argument"""
        # implemented by self.create additional arguments


class VegetaTargetsWriter:
    """Vegeta targets file creator"""

    def __init__(self, target_list: Iterable[VegetaTarget], base_url: str = None):
        """Constructor
        :param target_list: a sequence of VegetaTarget objects
        :param base_url: target's base_url
        """
        self.base_url = base_url or ''
        self.template = Template(f'GET $url$headers$body\n\n')
        self.targets = self._get_targets(target_list)

    def _get_targets(self, target_list: Iterable[VegetaTarget]) -> Iterator:
        """Prepares targets list to write to a file
        :param target_list: a sequence of VegetaTarget objects
        :return: an iterator of targets
        """
        str_targets = [self.to_str(target) for target in target_list]
        shuffle(str_targets)
        return iter(str_targets)

    def to_file(self, file: str):
        """Starts extracting targets and writes it to a file
        :param file: a file with Vegeta targets
        """
        with open(file, 'w') as f:
            f.writelines(self.targets)

    def get_headers(self, target: VegetaTarget) -> str:
        """Converts target headers to string"""
        if not isinstance(target.headers, str):
            raise NotImplementedError('Unable to build targets with non-string headers yet')

        if target.headers:
            return '\n' + target.headers

        return ''

    def get_body(self, target: VegetaTarget) -> str:
        """Converts target body to string"""
        if not isinstance(target.body, str):
            raise NotImplementedError('Unable to build targets with non-string body yet')

        if target.body:
            return '\n' + target.body

        return ''

    def get_url(self, target: VegetaTarget) -> str:
        """Converts url"""
        parsed = urlparse(target.url)
        base = urlparse(self.base_url)

        result = (
            parsed.scheme or base.scheme,
            parsed.netloc or base.netloc,
            parsed.path or base.path,
            parsed.params or base.params,
            parsed.query or base.query,
            parsed.fragment or base.fragment
        )

        return urlunparse(result)

    def to_str(self, target: VegetaTarget) -> str:
        """Converts VegetaTarget object to string"""
        target_str = self.template.substitute(
            url=self.get_url(target),
            headers=self.get_headers(target),
            body=self.get_body(target)
        )
        return target_str


if __name__ == '__main__':

    # getting high rated movies
    with connect(DB_ADDRESS) as db:
        extractor = MovieDataExtractor(db)
        high_rated = [
            extractor.get_movie(m_id)
            for m_id in extractor.get_movies_ids('imdb_rating > 7')
        ]

    # creating objects for Vegeta targets
    factory = SearchServiceTargetFactory()
    search_args, persons = [], set()

    for movie in high_rated:
        # getting movie by title or description
        short_title = movie.title[:len(movie.title) // 2]
        short_description = movie.description[:len(movie.description) // 2] if movie.description else None
        search_args.append({'search': [None, movie.title, short_title, short_description]})

        # getting actors and writers
        for person in [*movie.actors, *movie.writers]:
            persons.add(person.name)

    # getting search args by actors and writers
    for person in persons:
        search_args.append({'search': [None, person]})

    # writing targets to the file
    # https://github.com/KazakovDenis/praktikum/blob/master/search_service/tests/load/targets.txt
    targets = map(factory.create, search_args)
    filename = op.join(SEARCH_SRV_DIR, 'tests', 'load', 'targets.txt')
    base_url = urljoin(SEARCH_SRV_URL, '/api/v1/movies')
    vegeta_writer = VegetaTargetsWriter(targets, base_url)
    vegeta_writer.to_file(filename)
