from rest_framework import serializers
from tweets.api.serializers import TweetSerializer
from newsfeeds.models import Newsfeed


class NewsfeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer(source='cached_tweet')

    class Meta:
        model = Newsfeed
        fields = ('id', 'tweet', 'created_at')
