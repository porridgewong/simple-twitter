from django.conf import settings
from django.core.cache import caches

cache = caches['testing'] if settings.TESTING else caches['default']


class MemcachedHelper:
    @classmethod
    def get_key(cls, model_class, object_id):
        return '{}:{}'.format(model_class.__name__, object_id)

    @classmethod
    def get_object_from_cache(cls, model_class, object_id):
        key = cls.get_key(model_class, object_id)
        obj = cache.get(key)

        if obj is not None:
            return obj

        obj = model_class.objects.get(id=object_id)
        cache.set(key, obj)
        return obj

    @classmethod
    def invalidate_cached_object(cls, model_class, object_id):
        key = cls.get_key(model_class, object_id)
        cache.delete(key)
        