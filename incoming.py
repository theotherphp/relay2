import logging
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application

from ws_base import RelayWSHandler


class LapsWSHandler(RelayWSHandler):
    
    def on_message(self, message):
        tags = [int(t) for t in message.split(',')]
        for t in tags:
            self.q.put_nowait(int(t))


def read_incoming_tags(q, port):
    logging.info('starting up')
    app_settings = dict(debug=True)
    handler_args = dict(q=q)
    app = Application([
        (r'/laps_ws', LapsWSHandler, handler_args),        
    ], autoreload=True, **app_settings)
    HTTPServer(app).listen(port)
    IOLoop.current().start()
    logging.info('shutting down')