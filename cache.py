import redis
# import os


redis_client = redis.Redis(host='localhost', port=6379, db=0)
# REDIS_HOST = os.getenv("REDIS_HOST")
# REDIS_PORT = os.getenv("REDIS_PORT")

# redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def cache_set(key, value):
    redis_client.set(key, value)

def cache_get(key):
    return redis_client.get(key)
