from django.conf import settings
from util.redis_client import RedisClient
from util.redis_serializer import DjangoModelSerializer


class RedisHelper:
    @classmethod
    def _load_objects_to_cache(cls, key, objects):
        conn = RedisClient.get_connection()

        serialized_list = list()

        # load REDIS_LIST_LENGTH_LIMIT objects
        for obj in objects[:settings.REDIS_LIST_LENGTH_LIMIT]:
            serialized_list.append(DjangoModelSerializer.serialize(obj))

        if serialized_list:
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def load_objects(cls, key, queryset):
        conn = RedisClient.get_connection()
        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1)
            objects = list()
            for serialized_data in serialized_list:
                objects.append(DjangoModelSerializer.deserialize(serialized_data))

            return objects

        cls._load_objects_to_cache(key, queryset)

        return list(queryset)

    '''
    Used by post commit. When the key is not existed, it means all the tweets don't exist, so load all the tweets
    directly from DB, instead of push a single tweet to the list in the Redis.
    '''
    @classmethod
    def push_object(cls, key, obj, queryset):
        conn = RedisClient.get_connection()
        if not conn.exists(key):
            cls._load_objects_to_cache(key, queryset)
            return

        serialized_data = DjangoModelSerializer.serialize(obj)
        conn.lpush(key, serialized_data)

        # keep REDIS_LIST_LENGTH_LIMIT objects in cache
        conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1)
