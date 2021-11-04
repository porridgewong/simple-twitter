def incr_likes_count(sender, instance, created, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet
    from util.redis_helper import RedisHelper

    if not created:
        return

    model_class = instance.content_type.model_class()

    if model_class != Tweet:
        # TODO: support likes for comments.
        return

    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') + 1)
    tweet = instance.content_object
    RedisHelper.incr_count(tweet, 'likes_count')


def decr_likes_count(sender, instance, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet
    from util.redis_helper import RedisHelper

    model_class = instance.content_type.model_class()

    if model_class != Tweet:
        # TODO: support likes for comments.
        return

    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') - 1)
    tweet = instance.content_object
    RedisHelper.decr_count(tweet, 'likes_count')
