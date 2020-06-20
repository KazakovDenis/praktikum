from json import loads as json_loads
from multiprocessing import Process
from requests import get as http_get
from time import sleep

from search_service.manage import *


HOST, PORT = '127.0.0.1', 7999
BASE_URL = f'http://{HOST}:{PORT}'
server = Process(target=lambda: app.run(host=HOST, port=PORT))


def setup_module():
    server.start()
    sleep(5)        # while the server is not running


def teardown_module():
    server.kill()
    server.join()


def test_service_running():
    """Checks that index page returns HTTP 200"""
    response = http_get(BASE_URL)
    assert response.status_code == 200


def test_client_info():
    """Check that ClientInfo endpoint works correctly"""
    response = http_get(BASE_URL + '/client/info')
    payload = json_loads(response.content)
    assert 'python-requests' in payload.get('user_agent', '')
