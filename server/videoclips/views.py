from django.db import transaction
from rest_framework import filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, VCCategory, VCComment, Videoclip

from vidnet.viewsets import VidnetModelViewSet

from .permissions import AuthorPermission, CommentPermission, IsAdminOrReadOnly
from .filters import VideoclipFilter
from .serializers import CategorySerializer, VCCategorySerializer, VCCommentEditSerializer, VCCommentSerializer, VideoclipEditSerializer, VideoclipSerializer


class VideoclipView(VidnetModelViewSet):

    permission_classes = [AuthorPermission]
    queryset = Videoclip.objects.all()
    read_serializer_class = VideoclipSerializer
    edit_serializer_class = VideoclipEditSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = VideoclipFilter
    search_fields = ['title', 'description',
                     'categories__name', 'author__first_name']

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        kwargs['author'] = user
        return super().create(request, *args, **kwargs)


class CategoryView(VidnetModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    edit_serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class VCCategoriesView(VidnetModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    edit_serializer_class = VCCategorySerializer
    permission_classes = [AuthorPermission]

    def list(self, request, videoclip_pk=None):
        categories = VCCategory.objects.filter(videoclip=videoclip_pk)
        categories_id = categories.values_list('category', flat=True)
        queryset = Category.objects.filter(pk__in=categories_id)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class VCCommentView(VidnetModelViewSet):
    queryset = VCComment.objects.all()
    serializer_class = VCCommentSerializer
    edit_serializer_class = VCCommentEditSerializer
    permission_classes = [AuthorPermission | CommentPermission]

    def list(self, request, videoclip_pk=None):
        queryset = VCComment.objects.filter(videoclip=videoclip_pk)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
