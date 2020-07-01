from json import loads as json_loads
from os.path import join
from re import search as re_search
from sqlite3 import connect, Connection
from typing import List

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from common.config import DB_ADDRESS, ES_HOSTS, JSON_DIR


# Extract
def get_movies_ids(db: Connection) -> str:
    """Extracts ids of all movies from DB

    :param db: database connection instance
    :return: ids of a movies
    """

    cursor = db.execute('SELECT id FROM movies')

    while record := cursor.fetchone():
        yield record[0]

    cursor.close()


def get_movie_data(db: Connection, movie_id: str) -> dict:
    """Extracts all information about the movie from DB

    :param db: database connection instance
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

    cursor = db.execute(query, [movie_id])
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


def get_writers(db: Connection, movie_data: dict) -> List[dict]:
    """Extracts the movie writers from DB

    :param db: database connection instance
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
        query = f"SELECT * FROM writers WHERE id IN ('{ids_str}')"
        cursor = db.execute(query)
        writers = [
            {'id': record[0], 'name': record[1]} for record in cursor.fetchall()
        ]
        cursor.close()

    return writers


def get_names(data: List[dict]) -> str:
    """Extracts names from actors / writers data"""
    name_iter = map(lambda r: r.get('name', ''), data)
    return ', '.join(name_iter)


def get_list_from_str(value: str) -> list:
    """Returns a list of clean values from str"""
    if value == 'N/A':
        return []

    return value.split(', ')


# Transform
def convert_movie_data(db: Connection, data: dict) -> dict:
    """Converts the movie data to be uploaded to ElasticSearch server

    :param db: database connection instance
    :param data: the movie data
    :return: prepared movie data
    """

    tmp = re_search(r'\d+.\d+', str(data.get('imdb_rating')))
    rating = float(tmp.group()) if tmp else 0.0

    actors = json_loads(data.get('actors') or '[]')
    actors_names = data.get('actors') if data.get('actors') != 'N/A' else ''
    director = get_list_from_str(data.get('director', ''))
    genre = get_list_from_str(data.get('genre', ''))
    writers = get_writers(db, data)
    writers_names = get_names(writers)

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


# Load
def create_index(es_client: Elasticsearch):
    """Creates the movie index in ElasticSearch server"""

    script = join(JSON_DIR, 'create_index.json')

    with open(script, 'rb') as file:
        body = json_loads(file.read())

    return es_client.indices.create('movies', body, ignore=400)


def upload_movies_to_es(es_client: Elasticsearch) -> list:
    """Uploads movies data from the database to an ElasticSearch server

    :param es_client: ElasticSearch client instance
    :return: items with errors
    """

    cache, with_errors = [], []

    with connect(DB_ADDRESS) as db:
        movies_ids = get_movies_ids(db)

        for movie_id in movies_ids:
            data = get_movie_data(db, movie_id)
            es_data = convert_movie_data(db, data)
            cache.append(es_data)

            if len(cache) > 50:
                _, failed = bulk(es_client, cache, index='movies')
                cache.clear()
                with_errors.extend(failed)

    # cache remains
    _, failed = bulk(es_client, cache, index='movies')
    with_errors.extend(failed)

    return with_errors


def main():
    es = Elasticsearch(ES_HOSTS)
    if not es.ping():
        raise ConnectionError('ElasticSearch server is not available')

    create_index(es)
    not_uploaded = upload_movies_to_es(es)
    return not_uploaded


if __name__ == '__main__':
    main()

