from json import loads as json_loads
from sqlite3 import connect, Connection
from typing import Iterator

from elasticsearch import Elasticsearch
from common.config import DB_ADDRESS, ES_HOSTS


es = Elasticsearch(ES_HOSTS)


# Extract
def get_movies_ids(db: Connection) -> Iterator[str]:
    """Extracts ids of all movies from DB

    :param db: database connection instance
    :return: an iterator with ids of all movies
    """

    cursor = db.execute('SELECT id FROM movies')
    records = cursor.fetchall()
    cursor.close()

    ids = map(lambda item: item[0], records)
    return ids


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
    # todo: if None
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
    """Converts the movie data to be uploaded to Elasticsearch server

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


def prepare_bulk_payload(data: list, action_str: str = None) -> str:
    """Converts items from data list to Elasticsearch bulk body"""

    payload = ''
    action_str = action_str or '{"create": {}}\n'
    
    for item in data:
        payload += action_str + str(item) + '\n'
    
    return payload.replace('\'', '"')

    es = Elasticsearch(['http://127.0.0.1:9200'])

    if es.ping():
        cache = []

    with connect('db.sqlite') as db:
        movies_ids = get_movies_ids(db)

            for movie_id in movies_ids:
                data = get_movie_data(db, movie_id)
                es_data = convert_movie_data(db, data)

                if len(cache) < 10:
                    cache.append(es_data)
                else:
                    # todo: bulk load
                    payload = create_payload()
                    result = es.bulk(body=payload)
                    if not result['Error']:
                        cache.clear()
    else:
        raise ConnectionError('Elasticsearch server is not available')


if __name__ == '__main__':
    main()

