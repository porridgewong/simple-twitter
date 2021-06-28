from rest_framework import serializers
from tweets.api.serializers import TweetSerializer
from newsfeeds.models import Newsfeed


class NewsfeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer()

    class Meta:
        model = Newsfeed
        fields = ('id', 'user', 'tweet', 'created_at')
