def invalidate_object_cache(sender, instance, **kwargs):
    from util.memcached_helper import MemcachedHelper
    MemcachedHelper.invalidate_cached_object(sender, instance.id)


def push_tweet_to_cache(sender, instance, created, **kwargs):
    if not created:
        return

    from tweets.services import TweetService
    TweetService.push_tweet_to_cache(instance)
