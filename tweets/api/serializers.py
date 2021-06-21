from rest_framework import serializers
from accounts.api.serializers import UserSerializerForTweet
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        content = validated_data['content']
        user = self.context['request'].user
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet
