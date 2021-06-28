from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet
from newsfeeds.services import NewsfeedService


class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response('missing user_id.', 400)
        tweets = Tweet.objects.filter(user_id=request.query_params['user_id']).order_by('-created_at')
        serializers = TweetSerializer(tweets, many=True)
        return Response({'tweets': serializers.data})

    def create(self, request):
        serializer = TweetSerializerForCreate(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({
                    'success': False,
                    'message': 'Please check input',
                    'errors': serializer.errors
                },
                status=400)

        tweet = serializer.save()
        NewsfeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)
