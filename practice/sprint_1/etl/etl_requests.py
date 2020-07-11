from json import loads as json_loads
from os.path import join
from re import search as re_search
from sqlite3 import connect, Connection
from typing import List

import requests as http

from common import ETL_DIR, ES_HOSTS


CR_INDEX_SCR = join(ETL_DIR, 'create_index.json')
DB_ADDRESS = join(ETL_DIR, 'db.sqlite')


class ESLoader:

    def __init__(self, url: str):
        self.url = url[0] if isinstance(url, list) else url

    def load_to_es(self, records: List[dict], index_name: str):
        """
        Метод для сохранения записей в ElasticSearch.
        :param records: список данных на запись, который должен быть следующего вида:
        [
            {
                "id": "tt123456",
                "genre": ["Action", "Horror"],
                "writers": [
                    {
                        "id": "123456",
                        "name": "Great Divider"
                    },
                    ...
                ],
                "actors": [
                    {
                        "id": "123456",
                        "name": "Poor guy"
                    },
                    ...
                ],
                "actors_names": ["Poor guy", ...],
                "writers_names": [ "Great Divider", ...],
                "imdb_rating": 8.6,
                "title": "A long time ago ...",
                "director": ["Daniel Switch", "Carmen B."],
                "description": "Long and boring description"
            }
        ]
        Если значения нет или оно N/A, то нужно менять на None
        В списках значение N/A надо пропускать
        :param index_name: название индекса, куда будут сохраняться данные
        """
        # Ваша реализация здесь


class ETL:

    def __init__(self, conn: Connection, es_loader: ESLoader):
        self.es_loader = es_loader
        self.conn = conn

    def create_index(self, index_name: str):
        """Creates the movie index in ElasticSearch server"""

        with open(CR_INDEX_SCR, 'r') as file:
            body = json_loads(file.read())

        url = self.es_loader.url + '/' + index_name

        response = http.put(url, body)
        # ingore 400

        return response

    def load(self, index_name: str):
        """
        Основной метод для нашего ETL.
        Обязательно используйте метод load_to_es, это будет проверяться
        :param index_name: название индекса, в который будут грузиться данные
        """
        # Ваша реализация ETL здесь


db = connect(DB_ADDRESS)
loader = ESLoader(ES_HOSTS)
etl = ETL(db, loader)


if __name__ == '__main__':
    etl.load('movies')
