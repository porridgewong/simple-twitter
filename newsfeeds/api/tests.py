from django.conf import settings
from friendships.models import Friendship
from newsfeeds.models import Newsfeed
from newsfeeds.services import NewsfeedService
from newsfeeds.tasks import fanout_newsfeeds_main_task
from rest_framework.test import APIClient
from testing.TwitterTestCase import TwitterTestCase
from util.paginations import EndlessPagination


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TwitterTestCase):

    def setUp(self):
        self.clear_cache()
        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)

        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        # create followings and followers for dongxie
        for i in range(2):
            follower = self.create_user('dongxie_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.dongxie)
        for i in range(3):
            following = self.create_user('dongxie_following{}'.format(i))
            Friendship.objects.create(from_user=self.dongxie, to_user=following)

    def test_list(self):
        # case 1: no login
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)

        # case 2: use post
        response = self.linghu_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)

        # case 3: success
        response = self.linghu_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
        # self-visibility
        self.linghu_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.linghu_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['results']), 1)
        # visibility after following
        self.linghu_client.post(FOLLOW_URL.format(self.dongxie.id))
        response = self.dongxie_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.linghu_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['tweet']['id'], posted_tweet_id)

    def test_pagination(self):
        page_size = EndlessPagination.page_size
        followed_user = self.create_user('followed')
        newsfeeds = []
        for i in range(page_size * 2):
            tweet = self.create_tweet(followed_user)
            newsfeed = self.create_newsfeed(user=self.linghu, tweet=tweet)
            newsfeeds.append(newsfeed)

        newsfeeds = newsfeeds[::-1]

        # pull the first page
        response = self.linghu_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[1].id)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'],
            newsfeeds[page_size - 1].id,
        )

        # pull the second page
        response = self.linghu_client.get(
            NEWSFEEDS_URL,
            {'created_at__lt': newsfeeds[page_size - 1].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        results = response.data['results']
        self.assertEqual(len(results), page_size)
        self.assertEqual(results[0]['id'], newsfeeds[page_size].id)
        self.assertEqual(results[1]['id'], newsfeeds[page_size + 1].id)
        self.assertEqual(
            results[page_size - 1]['id'],
            newsfeeds[2 * page_size - 1].id,
        )

        # pull latest newsfeeds
        response = self.linghu_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)

        tweet = self.create_tweet(followed_user)
        new_newsfeed = self.create_newsfeed(user=self.linghu, tweet=tweet)

        response = self.linghu_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeed.id)

    def test_user_cache(self):
        profile = self.dongxie.profile
        profile.nickname = 'huanglaoxie'
        profile.save()

        self.assertEqual(self.linghu.username, 'linghu')
        self.create_newsfeed(self.dongxie, self.create_tweet(self.linghu))
        self.create_newsfeed(self.dongxie, self.create_tweet(self.dongxie))

        response = self.dongxie_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'dongxie')
        self.assertEqual(results[0]['tweet']['user']['nickname'], 'huanglaoxie')
        self.assertEqual(results[1]['tweet']['user']['username'], 'linghu')

        self.linghu.username = 'linghuchong'
        self.linghu.save()
        profile.nickname = 'huangyaoshi'
        profile.save()

        response = self.dongxie_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'dongxie')
        self.assertEqual(results[0]['tweet']['user']['nickname'], 'huangyaoshi')
        self.assertEqual(results[1]['tweet']['user']['username'], 'linghuchong')

    def test_tweet_cache(self):
        tweet = self.create_tweet(self.linghu, 'content1')
        self.create_newsfeed(self.dongxie, tweet)
        response = self.dongxie_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'linghu')
        self.assertEqual(results[0]['tweet']['content'], 'content1')

        # update username
        self.linghu.username = 'linghuchong'
        self.linghu.save()
        response = self.dongxie_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'linghuchong')

        # update content
        tweet.content = 'content2'
        tweet.save()
        response = self.dongxie_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['content'], 'content2')

    def _paginate_to_get_newsfeeds(self, client):
        # paginate until the end
        response = client.get(NEWSFEEDS_URL)
        results = response.data['results']
        while response.data['has_next_page']:
            created_at__lt = response.data['results'][-1]['created_at']
            response = client.get(NEWSFEEDS_URL, {'created_at__lt': created_at__lt})
            results.extend(response.data['results'])
        return results

    def test_redis_list_limit(self):
        list_limit = settings.REDIS_LIST_LENGTH_LIMIT
        page_size = 20
        users = [self.create_user('user{}'.format(i)) for i in range(5)]
        newsfeeds = []
        for i in range(list_limit + page_size):
            tweet = self.create_tweet(user=users[i % 5], content='feed{}'.format(i))
            feed = self.create_newsfeed(self.linghu, tweet)
            newsfeeds.append(feed)
        newsfeeds = newsfeeds[::-1]

        # only cached list_limit objects
        cached_newsfeeds = NewsfeedService.get_cached_newsfeeds(self.linghu.id)
        self.assertEqual(len(cached_newsfeeds), list_limit)
        queryset = Newsfeed.objects.filter(user=self.linghu)
        self.assertEqual(queryset.count(), list_limit + page_size)

        results = self._paginate_to_get_newsfeeds(self.linghu_client)
        self.assertEqual(len(results), list_limit + page_size)
        for i in range(list_limit + page_size):
            self.assertEqual(newsfeeds[i].id, results[i]['id'])

        # a followed user create a new tweet
        self.create_friendship(self.linghu, self.dongxie)
        new_tweet = self.create_tweet(self.dongxie, 'a new tweet')
        NewsfeedService.fanout_to_followers(new_tweet)

        def _test_newsfeeds_after_new_feed_pushed():
            results = self._paginate_to_get_newsfeeds(self.linghu_client)
            self.assertEqual(len(results), list_limit + page_size + 1)
            self.assertEqual(results[0]['tweet']['id'], new_tweet.id)
            for i in range(list_limit + page_size):
                self.assertEqual(newsfeeds[i].id, results[i + 1]['id'])

        _test_newsfeeds_after_new_feed_pushed()

        # cache expired
        self.clear_cache()
        _test_newsfeeds_after_new_feed_pushed()


class NewsFeedTaskTests(TwitterTestCase):

    def setUp(self):
        self.clear_cache()
        self.linghu = self.create_user('linghu')
        self.dongxie = self.create_user('dongxie')

    def test_fanout_main_task(self):
        tweet = self.create_tweet(self.linghu, 'tweet 1')
        self.create_friendship(self.dongxie, self.linghu)
        msg = fanout_newsfeeds_main_task(tweet.id, self.linghu.id)
        self.assertEqual(msg, '1 newsfeeds going to fanout, 1 batches created.')
        self.assertEqual(1 + 1, Newsfeed.objects.count())
        cached_list = NewsfeedService.get_cached_newsfeeds(self.linghu.id)
        self.assertEqual(len(cached_list), 1)

        for i in range(2):
            user = self.create_user('user{}'.format(i))
            self.create_friendship(user, self.linghu)
        tweet = self.create_tweet(self.linghu, 'tweet 2')
        msg = fanout_newsfeeds_main_task(tweet.id, self.linghu.id)
        self.assertEqual(msg, '3 newsfeeds going to fanout, 1 batches created.')
        self.assertEqual(4 + 2, Newsfeed.objects.count())
        cached_list = NewsfeedService.get_cached_newsfeeds(self.linghu.id)
        self.assertEqual(len(cached_list), 2)

        user = self.create_user('another user')
        self.create_friendship(user, self.linghu)
        tweet = self.create_tweet(self.linghu, 'tweet 3')
        msg = fanout_newsfeeds_main_task(tweet.id, self.linghu.id)
        self.assertEqual(msg, '4 newsfeeds going to fanout, 2 batches created.')
        self.assertEqual(8 + 3, Newsfeed.objects.count())
        cached_list = NewsfeedService.get_cached_newsfeeds(self.linghu.id)
        self.assertEqual(len(cached_list), 3)
        cached_list = NewsfeedService.get_cached_newsfeeds(self.dongxie.id)
        self.assertEqual(len(cached_list), 3)
