from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound


class PageNumberPaginationDataOnly(PageNumberPagination):
    # Set any other options you want here like page_size
    page_size = 12
    max_page_size = 1000

    def paginate_queryset(self, queryset, request, view=None):
        """Checking NotFound exception"""
        try:
            return super(PageNumberPaginationDataOnly, self).paginate_queryset(queryset, request, view=view)
        except NotFound:  # intercept NotFound exception
            return list()

    def get_paginated_response(self, data):
        try:
            return Response({
                'count': self.page.paginator.num_pages,
                'results': data
            })
        except:
            return Response(list())
