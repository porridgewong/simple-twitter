from django.test import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from rest_framework.test import APIClient


class TwitterTestCase(TestCase):
    def create_user(self, username, password=None, email=None):
        if password is None:
            password = 'testpassword'

        if email is None:
            email = f'{username}@test.com'

        return User.objects.create_user(username=username, password=password, email=email)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'this is a test tweet.'

        return Tweet.objects.create(user=user, content=content)

    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client
