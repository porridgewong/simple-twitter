from testing.TwitterTestCase import TwitterTestCase
from rest_framework.test import APIClient
from tweets.models import Tweet

TWEET_LIST_ENDPOINT = '/api/tweets/'
TWEET_CREATE_ENDPOINT = '/api/tweets/'
TWEET_RETRIEVE_API = '/api/tweets/{}/'


class TweetAPITest(TwitterTestCase):

    def setUp(self):
        self.user1 = self.create_user('user1', 'user1@test.com')
        self.tweets1 = [
            self.create_tweet(self.user1)
            for i in range(3)
        ]
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@test.com')
        self.tweets2 = [
            self.create_tweet(self.user2)
            for i in range(2)
        ]

    def test_list_api(self):
        # case 1: no user_id parameter
        response = self.anonymous_client.get(TWEET_LIST_ENDPOINT)
        self.assertEqual(response.status_code, 400)

        # case 2: success
        response = self.anonymous_client.get(TWEET_LIST_ENDPOINT, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 3)
        response = self.anonymous_client.get(TWEET_LIST_ENDPOINT, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['tweets']), 2)
        # check tweets are in the descending order of created_at
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)

    def test_create_api(self):
        # case 1: not login
        response = self.anonymous_client.post(TWEET_CREATE_ENDPOINT)
        self.assertEqual(response.status_code, 403)

        # case 2: no content
        response = self.user1_client.post(TWEET_CREATE_ENDPOINT)
        self.assertEqual(response.status_code, 400)

        # case 3: content too short
        response = self.user1_client.post(TWEET_CREATE_ENDPOINT, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # case 4: content too long
        response = self.user1_client.post(TWEET_CREATE_ENDPOINT, {
            'content': '0' * 141
        })
        self.assertEqual(response.status_code, 400)

        # case 5: success
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_ENDPOINT, {
            'content': 'Hello World, this is my first tweet!'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_retrieve(self):
        # case 1: tweet with id=-1 does not exist
        url = TWEET_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        # case 2: get tweets with comments
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        self.create_comment(self.user2, tweet, 'holly s***')
        self.create_comment(self.user1, tweet, 'hmm...')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 2)
