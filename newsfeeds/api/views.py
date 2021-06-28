from newsfeeds.api.serializers import NewsfeedSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from newsfeeds.models import Newsfeed
from rest_framework.response import Response
from rest_framework import status


class NewsfeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Newsfeed.objects.filter(user=self.request.user.id)

    def list(self, request):
        serializer = NewsfeedSerializer(self.get_queryset(), many=True)
        return Response({'newsfeeds': serializer.data}, status=status.HTTP_200_OK)
