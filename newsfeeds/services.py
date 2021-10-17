from friendships.services import FriendshipService
from newsfeeds.models import Newsfeed
from twitter.cache import USER_NEWSFEEDS_PATTERN
from util.redis_helper import RedisHelper


class NewsfeedService(object):
    @classmethod
    def fanout_to_followers(cls, tweet):
        user = tweet.user
        followers = FriendshipService.get_followers(user)
        newsfeeds = [Newsfeed(user=follower, tweet=tweet) for follower in followers]
        # add tweet's owner since it is visible to the owner themself
        newsfeeds.append(Newsfeed(user=tweet.user, tweet=tweet))
        Newsfeed.objects.bulk_create(newsfeeds)

        # bulk create doesn't trigger post_save, so load to cache manually
        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)

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
