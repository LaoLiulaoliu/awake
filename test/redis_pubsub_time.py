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
redispool = RedisPool().get_redis_connection()

def send_cycle_pub(redispool):
    print('enter send_cycle_pub')
    global GAP
    i = 0
    while True:
        t = time.time()
        redispool.publish('key', f'value_new_{i}')
        GAP = time.time()
        print('pub cost: ', GAP - t) # 0.000548942 on my mac i5 2.4G
        i += 1
        time.sleep(1)

def receive_sub(redispool):
    print('enter receive_sub')
    global GAP
    pubsub = redispool.pubsub()
    pubsub.subscribe('key')
    i = 0
    while True:
        for item in pubsub.listen():
            # if item['type'] == 'message':
            #     print(i, item['channel'], item['data'])
            # else:
            #     print(item)
            print('pubsub delay: ', time.time() - GAP) # 0.000183, sometimes exceed 0.5s - 1s
            i += 1
            time.sleep(0.5)


t1 = threading.Thread(target=send_cycle_pub, args=(redispool,))
t2 = threading.Thread(target=receive_sub, args=(redispool,))
t1.start()
t2.start()
