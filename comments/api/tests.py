from comments.models import Comment
from django.utils import timezone
from rest_framework.test import APIClient
from testing.TwitterTestCase import TwitterTestCase


COMMENT_URL = '/api/comments/'
TWEET_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'


class CommentApiTests(TwitterTestCase):

    def setUp(self):
        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)
        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        self.tweet = self.create_tweet(self.linghu)

    def test_create(self):
        # case 1: anonymous client
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # case 2: no params in request body
        response = self.linghu_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # case 3: tweet id only
        response = self.linghu_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        # case 4: content only
        response = self.linghu_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # case 5: content too long
        response = self.linghu_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # case 6: success
        response = self.linghu_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.linghu.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

    def test_destroy(self):
        comment = self.create_comment(self.linghu, self.tweet)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # case 1: anonymous client doesn't have permission to delete
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # case 2: non-owner is not allowed to delete
        response = self.dongxie_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # case 3: valid case
        count = Comment.objects.count()
        response = self.linghu_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.linghu, self.tweet, 'original')
        another_tweet = self.create_tweet(self.dongxie)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # case 1: anonymous client doesn't have permission to delete
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)

        # case 2: non-owner is not allowed to delete
        response = self.dongxie_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')

        # case 3: only content can be updated
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.linghu_client.put(url, {
            'content': 'new',
            'user_id': self.dongxie.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.linghu)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)

    def test_list(self):
        # case 1: no tweet_id param
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # case 2: list empty
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        # case 3: list newly created comments
        self.create_comment(self.linghu, self.tweet, '1')
        self.create_comment(self.dongxie, self.tweet, '2')
        self.create_comment(self.dongxie, self.create_tweet(self.dongxie), '3')
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], '1')
        self.assertEqual(response.data['comments'][1]['content'], '2')

        # case 4: more filters ignored
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.linghu.id,
        })
        self.assertEqual(len(response.data['comments']), 2)

    def test_comments_count(self):
        # case 1: test tweet detail api
        tweet = self.create_tweet(self.linghu)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.dongxie_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 0)

        # case 2: test tweet list api
        self.create_comment(self.linghu, tweet)
        response = self.dongxie_client.get(TWEET_LIST_API, {'user_id': self.linghu.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['comments_count'], 1)

        # case 3: test newsfeeds list api
        self.create_comment(self.dongxie, tweet)
        self.create_newsfeed(self.dongxie, tweet)
        response = self.dongxie_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['comments_count'], 2)

