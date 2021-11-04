def incr_comments_count(sender, instance, created, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet
    from util.redis_helper import RedisHelper

    if not created:
        return

    Tweet.objects.filter(id=instance.tweet_id).update(comments_count=F('comments_count') + 1)
    RedisHelper.incr_count(instance.tweet, 'comments_count')


def decr_comments_count(sender, instance, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet
    from util.redis_helper import RedisHelper

    Tweet.objects.filter(id=instance.tweet_id).update(comments_count=F('comments_count') - 1)
    RedisHelper.decr_count(instance.tweet, 'comments_count')

