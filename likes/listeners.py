def incr_likes_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    model_class = instance.content_type.model_class()

    if model_class != Tweet:
        # TODO: support likes for comments.
        return

    tweet = instance.content_object
    Tweet.objects.filter(id=tweet.id).update(likes_count=F('likes_count') + 1)


def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    model_class = instance.content_type.model_class()

    if model_class != Tweet:
        # TODO: support likes for comments.
        return

    tweet = instance.content_object
    Tweet.objects.filter(id=tweet.id).update(likes_count=F('likes_count') - 1)
