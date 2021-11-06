from django.utils.decorators import method_decorator
from newsfeeds.api.serializers import NewsfeedSerializer
from newsfeeds.models import Newsfeed
from newsfeeds.services import NewsfeedService
from ratelimit.decorators import ratelimit
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from util.paginations import EndlessPagination


class NewsfeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    @method_decorator(ratelimit(key='user', rate='5/s', method='GET', block=True))
    def list(self, request):
        newsfeeds = NewsfeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginator.paginate_cached_list(newsfeeds, request)

        # The data is not in the cache when the data is not recent.
        # Only cache the recent REDIS_LIST_LENGTH_LIMIT objects in cache.
        if page is None:
            queryset = Newsfeed.objects.filter(user_id=request.user.id).order_by('-created_at')
            page = self.paginate_queryset(queryset)

        serializer = NewsfeedSerializer(
                        page,
                        context={'request': request},
                        many=True)
        return self.get_paginated_response(serializer.data)
