"""
A module with a creator of targets for Vegeta
"""
from dataclasses import dataclass
from string import Template
from typing import AnyStr, Dict, Iterator, Union

from common import op, SEARCH_SRV_DIR, SEARCH_SRV_URL


@dataclass
class VegetaTarget:
    url: str
    headers: Union[Dict[str, str], str] = ''
    body: AnyStr = ''


class VegetaTargetsWriter:

    def __init__(self, netloc: str, target_list: list):
        """Constructor
        :param netloc: target's host:port
        :param target_list: a list of VegetaTarget objects
        """
        self.template = Template(f'GET {netloc}$url$headers$body\n\n')
        self.targets = self._get_targets(target_list)

    def _get_targets(self, target_list: list) -> Iterator:
        """Prepares targets list to write to a file
        :param target_list: a list of VegetaTarget objects
        :return: an iterator of targets
        """
        return (self.to_str(target) for target in target_list)

    def create(self, file: str):
        """Starts extracting targets and writes it to a file
        :param file: a file with Vegeta targets
        """
        with open(file, 'w') as file:
            file.writelines(self.targets)

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

    def to_str(self, target: VegetaTarget) -> str:
        """Converts VegetaTarget object to string"""
        target_str = self.template.substitute(
            url=target.url,
            headers=self.get_headers(target),
            body=self.get_body(target)
        )
        return target_str


if __name__ == '__main__':
    targets = []
    filename = op.join(SEARCH_SRV_DIR, 'tests', 'load', 'targets.txt')
    vegeta_writer = VegetaTargetsWriter(SEARCH_SRV_URL, targets)
    vegeta_writer.create(filename)
