"""
A module with a creator of targets for Vegeta
"""
from collections import namedtuple
from random import shuffle
from string import Template
from typing import AnyStr, Dict, Union
from urllib.parse import urlparse

from common import op, SEARCH_SRV_DIR, SEARCH_SRV_URL
from practice.sprint_1.etl.etl_requests import *


ParseResult = namedtuple('ParseResult', 'scheme netloc path params query fragment')


@dataclass
class VegetaTarget:
    url: str
    headers: Union[Dict[str, str], str] = ''
    body: AnyStr = ''


class VegetaTargetsWriter:
    """Vegeta targets file creator"""

    def __init__(self, base_url: str, target_list: list):
        """Constructor
        :param base_url: target's base_url
        :param target_list: a list of VegetaTarget objects
        """
        self.base_url = base_url
        self.template = Template(f'GET $url$headers$body\n\n')
        self.targets = self._get_targets(target_list)

    def _get_targets(self, target_list: list) -> Iterator:
        """Prepares targets list to write to a file
        :param target_list: a list of VegetaTarget objects
        :return: an iterator of targets
        """
        str_targets = [self.to_str(target) for target in target_list]
        shuffle(str_targets)
        return iter(str_targets)

    def create(self, file: str):
        """Starts extracting targets and writes it to a file
        :param file: a file with Vegeta targets
        """
        with open(file, 'w') as f:
            f.writelines(self.targets)

    def get_headers(self, target: VegetaTarget) -> str:
        """Converts target headers to string"""
        if not isinstance(target.headers, str):
            raise NotImplementedError('Unable to build targets with non-string headers yet')
        return '\n' + target.headers

    def get_body(self, target: VegetaTarget) -> str:
        """Converts target body to string"""
        if not isinstance(target.body, str):
            raise NotImplementedError('Unable to build targets with non-string body yet')
        return '\n' + target.body

    def get_url(self, target: VegetaTarget) -> str:
        """Converts url"""
        parsed = urlparse(target.url)

        if not parsed.netloc:
            base = urlparse(self.base_url)
            parsed = ParseResult(base.scheme, base.netloc, *parsed[2:])

        return parsed.geturl()

    def to_str(self, target: VegetaTarget) -> str:
        """Converts VegetaTarget object to string"""
        target_str = self.template.substitute(
            url=self.get_url(target),
            headers=self.get_headers(target),
            body=self.get_body(target)
        )
        return target_str


if __name__ == '__main__':

    with connect(DB_ADDRESS) as db:
        movie_extractor = MovieDataExtractor(db)
        high_rated = [
            movie_extractor.get_movie(m_id)
            for m_id in movie_extractor.get_movies_ids('imdb_rating > 7')
        ]

    targets = []
    for movie in high_rated:
        targets.append(VegetaTarget())

    filename = op.join(SEARCH_SRV_DIR, 'tests', 'load', 'targets.txt')
    vegeta_writer = VegetaTargetsWriter(SEARCH_SRV_URL, targets)
    vegeta_writer.create(filename)
