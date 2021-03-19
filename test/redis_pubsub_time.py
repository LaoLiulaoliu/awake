import time
import redis
import threading

REDIS_CLS = redis.StrictRedis

REDIS_PARAMS = {
    'host': '127.0.0.1',
    'port': 6379,
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': 'utf-8',
    # 'decode_responses': True
}

class RedisPool(object):

    def __init__(self, *args, **kwargs):
        kwargs.update(REDIS_PARAMS)
        self.redis_pool = redis.ConnectionPool(**kwargs)

    def get_redis_connection(self):
        return REDIS_CLS(connection_pool=self.redis_pool)

    def close_connection_pool(self):
        self.redis_pool.disconnect()

GAP = 0

def send_cycle_pub():
    print('enter send_cycle_pub')
    global GAP
    redispool = RedisPool().get_redis_connection()
    i = 0
    while True:
        t = time.time()
        redispool.publish('key', f'value_new_{i}')
        GAP = time.time()
        # print('pub cost: ', GAP - t)
        i += 1
        time.sleep(1)

def receive_sub():
    print('enter receive_sub')
    global GAP
    redispool = RedisPool().get_redis_connection()
    pubsub = redispool.pubsub()
    pubsub.subscribe('key')
    message = pubsub.get_message()
    if message['type'] == 'subscribe':
        print(message['data'])
    i = 0
    while True:
        print('enter receive_sub while')
        message = pubsub.listen()
        print(message)
        # print(GAP, message)
        # for item in message:
        #     if item['type'] == 'message':
        #         print(i, item['channel'], item['data'])
        print('pubsub delay: ', time.time() - GAP)
        i += 1


t1 = threading.Thread(target=send_cycle_pub, args=())
t2 = threading.Thread(target=receive_sub, args=())
t1.start()
print('start 2')
t2.start()
print('start 1')




