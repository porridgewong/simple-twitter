from newsfeeds.api.serializers import NewsfeedSerializer
from newsfeeds.services import NewsfeedService
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from util.paginations import EndlessPagination


class NewsfeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def list(self, request):
        newsfeeds = NewsfeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginate_queryset(newsfeeds)
        serializer = NewsfeedSerializer(
                        page,
                        context={'request': request},
                        many=True)
        return self.get_paginated_response(serializer.data)
