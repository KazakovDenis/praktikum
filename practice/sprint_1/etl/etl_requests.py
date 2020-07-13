from abc import ABC, abstractmethod
from contextlib import closing
from dataclasses import asdict, dataclass
from json import loads as json_loads
from os.path import join
from re import search as re_search
from sqlite3 import connect, Connection
from typing import List, Iterator

import requests as http

from common import ETL_DIR, ES_HOSTS


INDEX = 'movies'
CR_INDEX_SCR = join(ETL_DIR, 'create_index.json')
DB_ADDRESS = join(ETL_DIR, 'db.sqlite')


@dataclass
class Actor:
    id: int
    name: str


@dataclass
class Writer:
    id: str
    name: str


@dataclass
class Movie:
    id: str
    title: str
    imdb_rating: float
    description: str
    genre: List[str]
    actors: List[Actor]
    actors_names: str
    director: List[str]
    writers: List[Writer]
    writers_names: str


class BaseExtractor(ABC):

    def __init__(self, db_conn: Connection):
        self.db = db_conn

    @abstractmethod
    def extract(self): ...

    @abstractmethod
    def transform(self, data): ...


class MovieDataExtractor(BaseExtractor):
    """The class to extract movie data from a database"""

    def get_movies_ids(self) -> Iterator:
        """Extracts ids of all movies from DB
        :return: ids of movies
        """
        query = 'SELECT id FROM movies'

        with closing(self.db.execute(query)) as cursor:
            return map(
                lambda r: r[0],
                cursor.fetchall()
            )

    def get_movie_data(self, movie_id: str) -> dict:
        """Extracts all information about the movie from DB
        :param movie_id: movie id from DB
        :return: dict with the movie info
        """

        query = """\
        SELECT 
           m.imdb_rating, 
           m.genre, 
           m.title, 
           m.plot as description, 
           m.director, 
           group_concat(a.name, ', ') as actors_names,
           null as writers_names,
           '[' || group_concat(
               json_object('id', a.id, 'name', a.name)
           ) || ']' as actors,
           m.writers
        FROM movies m
        JOIN movie_actors ma ON m.id = ma.movie_id
        JOIN actors a        ON a.id = ma.actor_id
        WHERE m.id = ?
        GROUP BY m.id;
        """

        cursor = self.db.execute(query, [movie_id])
        rating, genre, title, plot, director, \
            actors_names, writers_names, actors, writers = cursor.fetchone()
        cursor.close()

        raw_data = {
            "_id": movie_id,
            "id": movie_id,
            "imdb_rating": rating,
            "genre": genre,
            "title": title,
            "description": plot,
            "director": director,
            "actors_names": actors_names,
            "writers_names": writers_names,
            "actors": actors,
            "writers": writers
        }

        return raw_data

    def get_writers(self, movie_data: dict) -> List[dict]:
        """Extracts the movie writers from DB
        :param movie_data: data from db
        :return: data with writers ids and names
        """

        writers_data = movie_data.get('writers') or '[]'
        writers_ids = map(
            lambda w: str(w.get('id', '')),
            json_loads(writers_data)
        )
        ids_str = "', '".join(writers_ids)
        writers = []

        if ids_str:
            query = f"SELECT * FROM writers WHERE id IN ('{ids_str}') ORDER BY id ASC"
            cursor = self.db.execute(query)
            writers = [
                {'id': record[0], 'name': record[1]} for record in cursor.fetchall()
            ]
            cursor.close()

        return writers

    @staticmethod
    def get_names(data: List[dict]) -> str:
        """Extracts names from actors / writers data"""
        name_iter = map(lambda r: r.get('name', ''), data)
        return ', '.join(name_iter)

    @staticmethod
    def get_list_from_str(value: str) -> list:
        """Returns a list of clean values from str"""
        if value == 'N/A':
            return []

        return value.split(', ')

    def transform(self, data: dict) -> dict:
        """Converts the movie data to be uploaded to ElasticSearch server
        :param data: the movie data
        :return: prepared movie data
        """

        tmp = re_search(r'\d+.\d+', str(data.get('imdb_rating')))
        rating = float(tmp.group()) if tmp else 0.0

        actors = json_loads(data.get('actors') or '[]').sort(key=lambda w: w['id'])
        actors_names = data.get('actors_names') if data.get('actors_names') != 'N/A' else ''
        director = self.get_list_from_str(data.get('director', ''))
        genre = self.get_list_from_str(data.get('genre', ''))
        writers = self.get_writers(data)
        writers_names = self.get_names(writers)

        data.update({
            'imdb_rating': rating,
            'actors': actors,
            'actors_names': actors_names,
            'director': director,
            'genre': genre,
            'writers': writers,
            'writers_names': writers_names,
        })
        return data

    def extract(self):
        """Returns data prepared to load to ElasticSearch"""

        movie_list = []

        for movie_id in self.get_movies_ids():
            data = self.get_movie_data(movie_id)
            es_data = self.transform(data)
            movie_list.append(es_data)

        return movie_list


class ESLoader:

    def __init__(self, url: str):
        self.url = url
        self.client = http.session()

    def create_index(self, index_name: str, payload_file: str):
        """Creates the movie index in ElasticSearch server"""

        with open(payload_file, 'r') as file:
            body = json_loads(file.read())

        url = self.url + '/' + index_name

        response = http.put(url, body)
        # ingore 400

        return response

    def load_to_es(self, records: List[dict], index_name: str, bulk_len: int = 50):
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
        :param bulk_len: размер списка данных, единоразово отправляемых в ElasticSearch
        """

        cache, with_errors = [], []
        packets = len(records) + 1 // bulk_len
        bulk_template = f'{index_name}'

        with http.session() as client:

            for i in range(packets):
                start, end = i * bulk_len, (i + 1) * bulk_len
                bulk = records[start:end]
                response = client.put(self.url, data=bulk)
                errors = response.json().get('errors')
                with_errors.extend(errors)

        return with_errors


class ETL:
    """Механизм ETL. Получает данные из БД и загружает в ElasticSearch"""

    def __init__(self, extractor: BaseExtractor, loader: ESLoader):
        self.extractor = extractor
        self.loader = loader

    def load(self, index_name: str):
        """Основной метод для нашего ETL.
        Обязательно используйте метод load_to_es, это будет проверяться
        :param index_name: название индекса, в который будут грузиться данные
        """
        if http.get(self.loader.url).status_code != 200:
            raise ConnectionError('ElasticSearch server is not available')

        records = self.extractor.extract()
        not_uploaded = self.loader.load_to_es(records, index_name)
        return not_uploaded


if __name__ == '__main__':

    with connect(DB_ADDRESS) as db:
        es_loader = ESLoader(ES_HOSTS[0])
        es_loader.create_index(INDEX, CR_INDEX_SCR)
        movie_extractor = MovieDataExtractor(db)

        etl = ETL(movie_extractor, es_loader)
        etl.load(INDEX)
