import argparse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import logging

from .etl import ETL


log = logging.getLogger('ETL')
handler = logging.StreamHandler()
log.addHandler(handler)
log.setLevel(logging.INFO)

filmwork_etl = ETL('filmwork')
genre_etl = ETL('genre')
person_etl = ETL('person')


class SignalHandler(BaseHTTPRequestHandler):
    """HTTP request handler for signals"""

    content_type = 'application/json'
    allowed = '/filmwork', '/genre', '/person'

    def do_GET(self):
        """Handle GET request"""
        if self.path not in self.allowed:
            self.response(200, b'{"result": null, "error": true}')
        else:
            self.response(200, b'{"result": "Signal accepted", "error": false}')
            self.run_etl()

    def response(self, code: int, body: bytes):
        self.send_response(code)
        self.send_header('Content-Type', self.content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def run_etl(self):
        """Start concrete ETL process"""
        if self.path == '/filmwork':
            filmwork_etl.run()

        if self.path == '/genre':
            genre_etl.run()

        if self.path == '/person':
            person_etl.run()


class ETLServer(ThreadingHTTPServer):
    """Server to handle ETLRunner signals and to start ETL processes"""

    def __init__(self, port):
        super().__init__(('localhost', port), SignalHandler)

    def run(self):
        """Start the server"""
        try:
            log.info(f'Listening for signals on port {self.server_port}\n')
            self.serve_forever()
        except KeyboardInterrupt:
            log.info('Shutting down...')
        finally:
            self.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start an ETL server')
    parser.add_argument(
        "-p", "--port",
        type=int, default=8050,
        help="start a server on this port (default 8050)"
    )
    args = parser.parse_args()
    ETLServer(args.port).run()
