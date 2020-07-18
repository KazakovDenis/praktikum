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

    def get_movies_ids(self, condition_str: str = None) -> Iterator:
        """Extracts ids of all movies from DB
        :param condition_str: conditions for SQL's WHERE
        :return: ids of movies
        """
        query = 'SELECT id FROM movies'

        if condition_str:
            query += ' WHERE ' + self._check_sql(condition_str)

        with closing(self.db.execute(query)) as cursor:
            return (r[0] for r in cursor.fetchall())

    def get_movie(self, movie_id: str) -> Movie:
        """Returns a movie object by id"""
        movie_data = self.extract_one(movie_id)
        movie_data['actors'] = self.get_actors(movie_data)
        movie_data['writers'] = self.get_writers(movie_data)
        return Movie(**movie_data)

    def get_actors(self, movie_data: dict = None, movie_id: str = None) -> List[Actor]:
        """Returns a list of movie actors
        :param movie_data: if movie data already extracted
        :param movie_id: to extract actors from DB
        """
        if movie_data:
            if not isinstance(movie_data['actors'], list):
                return []
            return [Actor(**record) for record in movie_data['actors']]

        return [Actor(**record) for record in self._extract_actors(movie_id)]

    def get_writers(self, movie_data: dict = None, movie_id: str = None) -> List[Writer]:
        """Returns a list of movie writers
        :param movie_data: if movie data already extracted
        :param movie_id: to extract writers from DB
        """
        if movie_data:
            if not isinstance(movie_data['writers'], list):
                return []
            return [Writer(**record) for record in movie_data['writers']]

        movie_data = self._extract_raw_data(movie_id)
        return [Writer(**record) for record in self._extract_writers(movie_data)]

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
                   writer,
                   writers
                FROM movies
                WHERE id = ?
                GROUP BY id;
            """

        with closing(self.db.execute(query, [movie_id])) as cursor:
            rating, genre, title, description, director, writer, writers = cursor.fetchone()

        raw_data = {
            "id": movie_id,
            "imdb_rating": rating,
            "genre": genre or '',
            "title": title,
            "description": description if description != 'N/A' else None,
            "director": director or '',
            "actors_names": '',
            "writers_names": '',
            "actors": '',
            "writers": writer or json.loads(writers or '[]')
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
        writers_data = movie_data.get('writers')

        if isinstance(writers_data, list):
            writers_ids = map(
                lambda writer: str(writer.get('id', '')),
                writers_data
            )
            ids_str = "', '".join(writers_ids)
        else:
            ids_str = writers_data

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
    def _check_sql(sql: str) -> str:
        """Looks for modifying queries"""

        for cmd in ['ALTER', 'DELETE', 'DROP', 'INSERT', 'UPDATE']:
            if cmd in sql.upper():
                raise PermissionError('You could not modify this table: "movies"')

        return sql

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
            'director': director or None,
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
        """Prepares records to a bulk request to ElasticSearch"""

        payload = ''

        for record in records:
            head = {'index': {'_index': index_name, '_id': record['id']}}
            head = json.dumps(head)
            record = json.dumps(record)
            payload += f'{head}\n{record}\n'

        return payload

    def load_to_es(self, records: List[dict], index_name: str, bulk_len: int = 100) -> List[dict]:
        """Uploads records to ElasticSearch
        :param records: data to load
        :param index_name: name of an index where to load records
        :param bulk_len: one-time data list size for loading to ElasticSearch
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
                err = response.json().get('items', [])
                with_errors.extend(err)

        return with_errors


class ETL:
    """Extracts data from a database and loads it to ElasticSearch"""

    def __init__(self, extractor: BaseExtractor, loader: ESLoader):
        self.extractor = extractor
        self.loader = loader

    def load(self, index_name: str) -> list:
        """Loads data to ElasticSearch
        :param index_name: name of index to load data into
        :returns upload errors
        """
        if requests.get(self.loader.url).status_code != 200:
            raise ConnectionError('ElasticSearch server is not available')

        records = self.extractor.extract()
        return self.loader.load_to_es(records, index_name)


if __name__ == '__main__':

    with connect(DB_ADDRESS) as db:
        es_loader = ESLoader(ES_HOSTS[0])
        es_loader.create_index(INDEX, CR_INDEX_SCR)
        movie_extractor = MovieDataExtractor(db)

        etl = ETL(movie_extractor, es_loader)
        errors = etl.load(INDEX)
        print(errors)
