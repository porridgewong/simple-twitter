from testing.TwitterTestCase import TwitterTestCase


class CommentModelTest(TwitterTestCase):

    def test_comment(self):
        user = self.create_user('lord')
        tweet = self.create_tweet(user, 'test tweet')
        comment = self.create_comment(user, tweet, 'test comment')
        self.assertNotEqual(comment.__str__(), None)
