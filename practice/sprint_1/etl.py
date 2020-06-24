from json import loads as json_loads
from sqlite3 import connect, Connection

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from common.config import DB_ADDRESS, ES_HOSTS


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


def get_writers_names(db: Connection, movie_data: dict) -> str:
    """Extracts the movie writers from DB

    :param db: database connection instance
    :param movie_data: data from db
    :return: a str with writers names
    """

    writers_data = movie_data.get('writers') or '[]'
    writers_ids = map(
        lambda w: str(w.get('id', '')),
        json_loads(writers_data)
    )
    ids_str = "', '".join(writers_ids)

    if ids_str:
        query = f"SELECT group_concat(name, ', ') FROM writers WHERE id IN ('{ids_str}')"
        cursor = db.execute(query)
        writers_names = cursor.fetchone()[0]
        cursor.close()
    else:
        writers_names = ''

    return writers_names


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


# Transform
def convert_movie_data(db: Connection, data: dict) -> dict:
    """Converts the movie data to be uploaded to ElasticSearch server

    :param db: database connection instance
    :param data: the movie data
    :return: prepared movie data
    """

    actors = json_loads(data.get('actors') or '[]')
    writers = json_loads(data.get('writers') or '[]')
    writers_names = get_writers_names(db, data)

    data.update({
        'actors': actors,
        'writers': writers,
        'writers_names': writers_names,
    })
    return data


# Load
def create_index(es_client: Elasticsearch):
    """Creates the movie index in ElasticSearch server"""

    with open('create_index.json', 'rb') as file:
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

