from friendships.models import Friendship
from friendships.services import FriendshipService
from testing.TwitterTestCase import TwitterTestCase


class FriendshipServiceTests(TwitterTestCase):
    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')

    def test_get_followings(self):
        user1 = self.create_user('user11')
        user2 = self.create_user('user22')
        for to_user in [user1, user2, self.user2]:
            Friendship.objects.create(from_user=self.user1, to_user=to_user)

        user_id_set = FriendshipService.get_following_user_id_set(self.user1.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id, self.user2.id})

        Friendship.objects.filter(from_user=self.user1, to_user=self.user2).delete()
        user_id_set = FriendshipService.get_following_user_id_set(self.user1.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id})
