from friendships.services import FriendshipService
from newsfeeds.models import Newsfeed


class NewsfeedService(object):
    @classmethod
    def fanout_to_followers(cls, tweet):
        user = tweet.user
        followers = FriendshipService.get_followers(user)
        newsfeeds = [Newsfeed(user=follower, tweet=tweet) for follower in followers]
        # add tweet's owner since it is visible to the owner themself
        newsfeeds.append(Newsfeed(user=tweet.user, tweet=tweet))
        Newsfeed.objects.bulk_create(newsfeeds)
