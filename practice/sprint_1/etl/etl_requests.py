import sqlite3
from typing import List


class ESLoader:

    def __init__(self, url: str):
        self.url = url

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

    def __init__(self, conn: sqlite3.Connection, es_loader: ESLoader):
        self.es_loader = es_loader
        self.conn = conn

    def load(self, index_name: str):
        """
        Основной метод для нашего ETL.
        Обязательно используйте метод load_to_es, это будет проверяться
        :param index_name: название индекса, в который будут грузиться данные
        """
        # Ваша реализация ETL здесь
