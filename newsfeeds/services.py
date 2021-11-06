from newsfeeds.models import Newsfeed
from newsfeeds.tasks import fanout_newsfeeds_main_task
from twitter.cache import USER_NEWSFEEDS_PATTERN
from util.redis_helper import RedisHelper


class NewsfeedService(object):
    @classmethod
    def fanout_to_followers(cls, tweet):
        fanout_newsfeeds_main_task.delay(tweet.id, tweet.user_id)

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = Newsfeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = Newsfeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_object(key, newsfeed, queryset)
