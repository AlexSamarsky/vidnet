# from django.shortcuts import render

from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_framework import filters

from videoclips.models import Category, Videoclip
from videoclips.serializers import CategorySerializer, VideoclipSerializer


class VideoclipView(ListAPIView):

    queryset = Videoclip.objects.all()
    serializer_class = VideoclipSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description',
                     'categories__name', 'author__first_name']


class CategoryView(ReadOnlyModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
