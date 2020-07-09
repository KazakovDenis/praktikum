from pytest import fixture, mark
from search_service.manage import *


@fixture
def client():
    return app.test_client()


@mark.parametrize('url,status', [
    ('/', 200),
    ('/api/v1/movies/', 200),
    ('/api/v1/movies/?page=2', 200),
    ('/api/v1/movies/?limit=10', 200),
    ('/api/v1/movies/?search=star', 200),
    ('/api/v1/movies/?sort=id', 200),
    ('/api/v1/movies/?sort=title', 200),
    ('/api/v1/movies/?sort=imdb_rating', 200),
    ('/api/v1/movies/?sort_order=asc', 200),
    ('/api/v1/movies/?sort_order=desc', 200),
    ('/api/v1/movies/?search=star&limit=2&page=2&sort=title&sort_order=desc', 200),
    ('/api/v1/movies/?page=aaa', 422),
    ('/api/v1/movies/?page=-1', 422),
    ('/api/v1/movies/?limit=aaa', 422),
    ('/api/v1/movies/?limit=-1', 422),
    ('/api/v1/movies/?sort=actors', 422),
    ('/api/v1/movies/?sort_order=ascending', 422),
    ('/api/v1/movies/?wrong=argument', 400),
    ('/api/v1/movies/?search=zzzzzzz', 404),

    ('/api/v1/movies/tt0112270', 200),
    ('/api/v1/movies/tt0000000', 404),
    ('/api/v1/movies/tt0112270?page=1', 400),
    ('/api/v1/movies/tt0112270?wrong=argument', 400),
])
def test_service_running(client, url, status):
    """Checks that url returns HTTP 200"""
    with client:
        response = client.get(url)
        assert response.status_code == status


def test_client_info(client):
    """Check that ClientInfo endpoint works correctly"""
    with client:
        response = client.get('/client/info', headers={'User-Agent': 'testagent/1.0'})
        assert response.json == {'user_agent': 'testagent/1.0'}
