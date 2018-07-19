from tornado.websocket import WebSocketHandler
import logging

"""
Base class for Websockets bookkeeping
"""
class RelayWSHandler(WebSocketHandler):

    def initialize(self, q):
        self.q = q
        self.alive = True

    
    def open(self):
        self.stream.set_nodelay(True)

    
    def on_close(self):
        logging.debug('on_close')
        self.alive = False
