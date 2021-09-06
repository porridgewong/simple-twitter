from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import caches
from friendships.models import Friendship
from twitter.cache import FOLLOWINGS_PATTERN


cache = caches['testing'] if settings.TESTING else caches['default']


class FriendshipService(object):
    @classmethod
    def get_followers(cls, user):
        friendships = Friendship.objects.filter(to_user=user)
        follower_ids = [friendship.from_user_id for friendship in friendships]
        followers = User.objects.filter(id__in=follower_ids)
        return followers

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        user_id_set = cache.get(key)
        if user_id_set is not None:
            return user_id_set

        friendships = Friendship.objects.filter(from_user_id=from_user_id)

        user_id_set = set([fs.to_user_id for fs in friendships])

        cache.set(key, user_id_set)
        return user_id_set

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)
        