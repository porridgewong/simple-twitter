from tweets.constants import TweetPhotoStatus
from datetime import timedelta
from testing.TwitterTestCase import TwitterTestCase
from tweets.models import TweetPhoto
from util.time_helper import utc_now


class TweetsModelTest(TwitterTestCase):
    def setUp(self):
        self.user1 = self.create_user('user1')
        self.tweet = self.create_tweet(self.user1, content='Jiuzhang Dafa Hao')
        
    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        user2 = self.create_user('user2')
        self.create_like(user2, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_create_photo(self):
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.user1,
        )
        self.assertEqual(photo.user, self.user1)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)
