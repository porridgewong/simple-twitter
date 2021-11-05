from celery import shared_task
from newsfeeds.models import Newsfeed
from tweets.models import Tweet
from util.time_constants import ONE_HOUR


@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeeds_task(tweet_id):
    from friendships.services import FriendshipService
    from newsfeeds.services import NewsfeedService

    tweet = Tweet.objects.filter(id=tweet_id)
    user = tweet.user
    followers = FriendshipService.get_followers(user)
    newsfeeds = [Newsfeed(user=follower, tweet=tweet) for follower in followers]
    # add tweet's owner since it is visible to the owner themself
    newsfeeds.append(Newsfeed(user=tweet.user, tweet=tweet))
    Newsfeed.objects.bulk_create(newsfeeds)

    # bulk create doesn't trigger post_save, so load to cache manually
    for newsfeed in newsfeeds:
        NewsfeedService.push_newsfeed_to_cache(newsfeed)
