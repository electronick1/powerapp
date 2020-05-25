import redis


class BaseKeyValueStore:
    def get(self, app_id, store_id, key):
        raise NotImplementedError()

    def set(self, app_id, store_id, key, value):
        raise NotImplementedError()


class RedisStore(BaseKeyValueStore):
    def __init__(self, redis_kwargs, max_value_len=255):
        self.redis = redis.Redis(**redis_kwargs)
        self.max_value_len = max_value_len

    def get(self, app_id, store_id, key):
        return self.redis.hget("%s:%s" % (app_id, store_id), key)

    def set(self, app_id, store_id, key, value):
        self.redis.hset("%s:%s" % (app_id, store_id), key, value)
        return value
