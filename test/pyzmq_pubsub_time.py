import zmq
import time
import threading

GAP = 0

def pub():
    global GAP
    i = 0
    socket = zmq.Context().socket(zmq.PUB)
    socket.bind('tcp://*:5555')
    while True:
        msg = f'key: who are {i}'
        t = time.time()
        socket.send(msg.encode('utf-8'))
        GAP = time.time()
        print('pub cost: ', GAP - t) # 0.0002679824829 on my mac i5 2.4G
        time.sleep(1)
        i += 1

def sub():
    global GAP
    i = 0
    socket = zmq.Context().socket(zmq.SUB)
    socket.connect('tcp://localhost:5555')
    socket.setsockopt(zmq.SUBSCRIBE, 'key'.encode('utf-8'))
    while True:
        response = socket.recv().decode('utf-8')
        print('response: %s' % response)
        print('pubsub delay: ', time.time() - GAP) # 0.0007688999
        time.sleep(0.5)
        i += 1

t1 = threading.Thread(target=pub, args=())
t2 = threading.Thread(target=sub, args=())
t1.start()
t2.start()