from comments.models import Comment
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from likes.models import Like
from rest_framework.test import APIClient
from tweets.models import Tweet


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

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'this is a test comment.'

        return Comment.objects.create(user=user, tweet=tweet, content=content)

    def create_like(self, user, target):
        instance, _ = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        )
        return instance

    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client
