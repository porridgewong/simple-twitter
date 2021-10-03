from django.conf import settings
import redis


class RedisClient(object):
    conn = None

    @classmethod
    def get_connection(cls):
        if cls.conn:
            return cls.conn

        cls.conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        return cls.conn

    @classmethod
    def clear(cls):
        if not settings.TESTING:
            raise Exception('You can flush Redis in production')

        conn = cls.get_connection()
        conn.flushdb()
        