from pytest import fixture, mark
from search_service.manage import *


@fixture
def client():
    return app.test_client()


@mark.parametrize('url', [
    '/',
    '/api/v1/movies/',
    '/api/v1/movies/tt0112270',
])
def test_service_running(client, url):
    """Checks that url returns HTTP 200"""
    with client:
        response = client.get(url)
        assert response.status_code == 200


def test_client_info(client):
    """Check that ClientInfo endpoint works correctly"""
    with client:
        response = client.get('/client/info', headers={'User-Agent': 'testagent/1.0'})
        assert response.json == {'user_agent': 'testagent/1.0'}
