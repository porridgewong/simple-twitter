from newsfeeds.services import NewsfeedService
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate, TweetSerializerWithComments
from tweets.models import Tweet
from util.decorators import required_params


class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate
    queryset = Tweet.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        return Response(TweetSerializerWithComments(tweet).data)

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        tweets = Tweet.objects.filter(user_id=request.query_params['user_id']).order_by('-created_at')
        serializers = TweetSerializer(tweets, many=True)
        return Response({'tweets': serializers.data})

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
        return Response(TweetSerializer(tweet).data, status=201)
