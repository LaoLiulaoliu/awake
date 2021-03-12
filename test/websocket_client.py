import json
import gevent
from websocket import WebSocketApp

WS_URL = 'ws://localhost:8000/websocket'

class Cli(object):
    def __init__(self):
        self.__connection = None

    def create(self):
        self.__connection = WebSocketApp(WS_URL,
                                        on_message=self.on_message,
                                        on_close=self.on_close,
                                        on_error=self.on_error)
        self.__connection.on_open = self.on_open
        print('before run forever')
        self.__connection.run_forever(ping_interval=20)
        print('after run forever')
    
    def send(self):
        print('send msg')
        if self.__connection is None:
            self.create()
            self.__connection.send('Jameson')

    def on_open(self):
        print('open')
        self.__connection.send('Jameson')

    def on_close(self):
        print('close')

    def on_error(self, error):
        print('error: ', error)

    def on_message(self, msg):
        print('message: ', msg)

c = Cli()
g = gevent.spawn(c.create)
print('created')
# gevent.sleep(1) # if sleep, it will run_forever, not execute rest code
c.send()
g.join()