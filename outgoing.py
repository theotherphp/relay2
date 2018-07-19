import multiprocessing as mp
import logging
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import Application

from ws_base import RelayWSHandler

class LeaderboardWSHandler(RelayWSHandler):

    clients = dict()
    client_key = 0
    
    def open(self, *args, **kwargs):
        self.client_key = LeaderboardWSHandler.client_key
        LeaderboardWSHandler.clients[self.client_key] = self
        LeaderboardWSHandler.client_key += 1

    def on_close(self):
        del LeaderboardWSHandler.clients[self.client_key]


def poll_queue(q):
    if not q.empty():
        notification = q.get_nowait()
        for client in LeaderboardWSHandler.clients.values():
            client.write_message(dict(
                type='leaderboard',
                change=notification
            ))


def send_outgoing_notifications(q, port):
    logging.info('starting up')
    app_settings = dict(debug=True)
    handler_args = dict(q=q)
    app = Application([
        (r'/leaderboard_ws', LeaderboardWSHandler, handler_args),        
    ], autoreload=True, **app_settings)
    HTTPServer(app).listen(port)
    PeriodicCallback(lambda: poll_queue(q), 500).start()
    IOLoop.current().start()
    logging.info('shutting down')