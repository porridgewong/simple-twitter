from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FriendshipPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 20
    page_size_query_param = 'size'

    def get_paginated_response(self, data):
        return Response({
                'total_results': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'page_number': self.page.number,
                'has_next_page': self.page.has_next(),
                'results': data,
            })
