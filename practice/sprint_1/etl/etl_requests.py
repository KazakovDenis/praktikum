from abc import ABC, abstractmethod
from contextlib import closing
from dataclasses import dataclass
import json
from math import ceil
from os.path import join
from re import search as re_search
from sqlite3 import connect, Connection
from typing import List, Iterator, Tuple
from urllib.parse import urljoin

import requests

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
    genre: List[str]
    imdb_rating: float
    description: str
    director: List[str]
    actors: List[Actor]
    actors_names: str
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
            return (r[0] for r in cursor.fetchall())

    def get_movie(self, movie_id: str) -> Movie:
        """Returns a movie by id"""
        movie_data = self._extract_raw_data(movie_id)
        return Movie(**movie_data)

    def get_actors(self, movie_id: str) -> Tuple[Actor]:
        """Returns tuple of movie actors"""
        return tuple(
            Actor(**record) for record in self._extract_actors(movie_id)
        )

    def get_writers(self, movie_id: str) -> Tuple[Writer]:
        """Returns tuple of movie writers"""
        movie_data = self._extract_raw_data(movie_id)
        return tuple(
            Writer(**record) for record in self._extract_writers(movie_data)
        )

    def extract_one(self, movie_id: str) -> dict:
        """Returns one movie data prepared to load to ElasticSearch"""
        data = self._extract_raw_data(movie_id)
        return self.transform(data)

    def extract(self) -> List[dict]:
        """Returns all movies data prepared to load to ElasticSearch"""
        return [self.extract_one(movie_id) for movie_id in self.get_movies_ids()]

    def _extract_raw_data(self, movie_id: str) -> dict:
        """Extracts all information about the movie from DB
        :param movie_id: movie id from DB
        :return: dict with the movie info
        """

        query = """\
            SELECT 
                   imdb_rating, 
                   genre, 
                   title, 
                   plot as description, 
                   director, 
                   writers
                FROM movies
                WHERE id = ?
                GROUP BY id;
            """

        with closing(self.db.execute(query, [movie_id])) as cursor:
            rating, genre, title, description, director, writers = cursor.fetchone()

        raw_data = {
            "id": movie_id,
            "imdb_rating": rating,
            "genre": genre or '',
            "title": title,
            "description": description,
            "director": director or '',
            "actors_names": '',
            "writers_names": '',
            "actors": '',
            "writers": writers
        }
        return raw_data

    def _extract_actors(self, movie_id: str) -> List[dict]:
        """Extracts the movie writers from DB
        :param movie_id: movie id from DB
        :return: data with writers ids and names
        """
        query = """\
            SELECT a.id, a.name
                FROM actors a
                JOIN movie_actors ma ON a.id = ma.actor_id
                JOIN movies m        ON m.id = ma.movie_id
                WHERE m.id = ?
                ORDER BY a.id ASC;
            """

        with closing(self.db.execute(query, [movie_id])) as cursor:
            actors = [
                {'id': r[0], 'name': r[1] if r[1] != 'N/A' else None}
                for r in cursor.fetchall()
            ]
        return actors

    def _extract_writers(self, movie_data: dict) -> List[dict]:
        """Extracts the movie writers from DB
        :param movie_data: data from db
        :return: data with writers ids and names
        """
        writers_ids = map(
            lambda writer: str(writer.get('id', '')),
            json.loads(movie_data.get('writers') or '[]')
        )
        ids_str = "', '".join(writers_ids)
        writers = []

        if ids_str:
            query = f"SELECT * FROM writers WHERE id IN ('{ids_str}') ORDER BY id ASC;"
            with closing(self.db.execute(query)) as cursor:
                writers = [
                    {'id': r[0], 'name': r[1] if r[1] != 'N/A' else None}
                    for r in cursor.fetchall()
                ]
        return writers

    @staticmethod
    def _get_names(data: List[dict]) -> str:
        """Extracts names from actors / writers data"""
        name_iter = map(lambda r: r.get('name') or '', data)
        return ', '.join(name_iter)

    @staticmethod
    def _get_list_from_str(value: str) -> list:
        """Returns a list of clean values from str"""
        if value == 'N/A':
            return []

        return value.split(', ')

    def transform(self, movie: dict) -> dict:
        """Converts the movie data to be uploaded to ElasticSearch server
        :param movie: Movie object with raw data
        :return: prepared movie data
        """

        tmp = re_search(r'\d+.\d+', str(movie['imdb_rating']))
        rating = float(tmp.group()) if tmp else 0.0

        director = self._get_list_from_str(movie['director'])
        genre = self._get_list_from_str(movie['genre'])

        actors = self._extract_actors(movie['id'])
        actors_names = self._get_names(actors)

        writers = self._extract_writers(movie)
        writers_names = self._get_names(writers)

        movie.update({
            'imdb_rating': rating,
            'actors': actors,
            'actors_names': actors_names,
            'director': director,
            'genre': genre,
            'writers': writers,
            'writers_names': writers_names,
        })
        return movie


class ESLoader:

    def __init__(self, url: str):
        self.url = url

    def create_index(self, index_name: str, payload_file: str) -> requests.Response:
        """Creates the movie index in ElasticSearch server"""

        with open(payload_file, 'rb') as file:
            body = file.read()

        url = urljoin(self.url, index_name)
        headers = {'Content-Type': 'application/json'}
        return requests.put(url, body, headers=headers)

    @staticmethod
    def get_bulk(records: List[dict], index_name: str) -> str:
        """Подготовливает данные для bulk-запроса в ElasticSearch"""

        payload = ''

        for record in records:
            head = {'index': {'_index': index_name, '_id': record['id']}}
            head = json.dumps(head)
            record = json.dumps(record)
            payload += f'{head}\n{record}\n'

        return payload

    def load_to_es(self, records: List[dict], index_name: str, bulk_len: int = 100) -> List[dict]:
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

        packets = ceil(len(records) / bulk_len)
        url = urljoin(self.url, '_bulk?filter_path=items.*.error')
        headers = {'Content-Type': 'application/x-ndjson'}
        with_errors = []

        with requests.session() as client:

            for i in range(packets):
                start, end = i * bulk_len, (i + 1) * bulk_len
                bulk = self.get_bulk(records[start:end], index_name)
                response = client.post(url, data=bulk, headers=headers)
                errors = response.json().get('items', [])
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
        if requests.get(self.loader.url).status_code != 200:
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
