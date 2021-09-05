from newsfeeds.api.serializers import NewsfeedSerializer
from newsfeeds.models import Newsfeed
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from util.paginations import EndlessPagination


class NewsfeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def get_queryset(self):
        return Newsfeed.objects.filter(user=self.request.user.id)

    def list(self, request):
        page = self.paginate_queryset(self.get_queryset())
        serializer = NewsfeedSerializer(
                        page,
                        context={'request': request},
                        many=True)
        return self.get_paginated_response(serializer.data)
