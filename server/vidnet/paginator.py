from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from rest_framework.utils.urls import replace_query_param

# def get_url(number):


class VidnetPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):

        pages = list(self.page.paginator.get_elided_page_range(
            self.page.number, on_each_side=3, on_ends=2))

        pages_urls = map(lambda page_number: page_number if page_number == self.page.paginator.ELLIPSIS else replace_query_param(
            self.request.build_absolute_uri(), self.page_query_param, page_number), pages)

        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'elided_pages': pages_urls,
            'num_pages': self.page.paginator.num_pages,
            'results': data
        })
