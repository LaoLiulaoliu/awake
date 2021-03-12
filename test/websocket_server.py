from geventwebsocket import WebSocketError
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import time
from flask import request, Flask


app = Flask(__name__)
users = set()

@app.route('/websocket')
def handle_websocket():
    web_socket = request.environ.get('wsgi.websocket')
    print('get connection: ', web_socket)
    
    users.add(web_socket)

    while True:
        try:
            # message = web_socket.receive()
            # print('get: ', message)
            web_socket.send('got your message')
            time.sleep(1)
        except WebSocketError as e:
            print(f'WebSocketError: {e}')
            users.remove(web_socket)
            return 'Error, connection closed!!'

        # if message:
        #     for user in users:
        #         user.send(message)

if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()
