from datetime import timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from util.time_helper import utc_now


class TweetsModelTest(TestCase):
    def test_create_data(self):
        user = User.objects.create_user('test user')
        tweet = Tweet.objects.create(user=user, content='This is a test tweet.')
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)
