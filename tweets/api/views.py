from newsfeeds.services import NewsfeedService
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate, TweetSerializerForDetail
from tweets.models import Tweet
from tweets.services import TweetService
from util.decorators import required_params
from util.paginations import EndlessPagination


class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    serializer_class = TweetSerializerForCreate
    pagination_class = EndlessPagination
    queryset = Tweet.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        serializer = TweetSerializerForDetail(self.get_object(), context={'request': request})
        return Response(serializer.data)

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        tweets = TweetService.get_cached_tweets(user_id=request.query_params['user_id'])
        tweets = self.paginate_queryset(tweets)
        serializer = TweetSerializer(
            tweets,
            context={'request': request},
            many=True,)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
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
        serializer = TweetSerializer(tweet, context={'request': request},)
        return Response(serializer.data, status=201)
