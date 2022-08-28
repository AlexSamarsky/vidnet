from django.db import transaction
from rest_framework import filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
# from rest_framework.parsers import FileUploadParser

from vidnet.paginator import VidnetPagination


from .models import Category, UserReaction, VCBan, VCCategory, VCComment, VCSubscription, Videoclip

from vidnet.viewsets import VidnetModelViewSet

from .permissions import AuthorPermission, CommentPermission, IsAdminOrReadOnly
from .filters import VideoclipFilter
from .serializers import (CategorySerializer, UserReactionEditSerializer, UserReactionSerializer, VCBanEditSerializer, VCBanSerializer,
                          VCCategorySerializer, VCCommentEditSerializer, VCCommentSerializer, VCSubscriptionEditSerializer,
                          VCSubscriptionSerializer, VideoclipEditSerializer, VideoclipSerializer, UploadSerializer)

from pure_pagination.mixins import PaginationMixin
# from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action


class UploadView(ViewSet):

    permission_classes = [AuthorPermission]

    @action(methods=['put'], detail=False, url_path='')
    def put(self, request, videoclip_pk):

        serializer = UploadSerializer(data=request.data)
        if serializer.is_valid():
            videoclip = get_object_or_404(Videoclip, pk=videoclip_pk)
            self.check_object_permissions(request, videoclip)
            videoclip.upload = request.FILES.get('upload')
            videoclip.save()

            serializer_read = VideoclipSerializer(
                videoclip, context={'request': request, "format": None, 'view': videoclip})
            return Response(serializer_read.data, status=status.HTTP_200_OK)


class VideoclipView(PaginationMixin, VidnetModelViewSet):

    # parser_classes = (FileUploadParser,)
    permission_classes = [AuthorPermission]
    queryset = Videoclip.objects.all()
    read_serializer_class = VideoclipSerializer
    write_serializer_class = VideoclipEditSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = VideoclipFilter
    search_fields = ['title', 'description',
                     'categories__name', 'author__first_name']

    pagination_class = VidnetPagination
    paginate_by = 1

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        kwargs['author'] = user
        return super().create(request, *args, **kwargs)


class CategoryView(VidnetModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class VCCategoriesView(VidnetModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    write_serializer_class = VCCategorySerializer
    permission_classes = [AuthorPermission]

    def list(self, request, videoclip_pk=None):
        categories = VCCategory.objects.filter(videoclip=videoclip_pk)
        categories_id = categories.values_list('category', flat=True)
        queryset = Category.objects.filter(pk__in=categories_id)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class VCNestedView(VidnetModelViewSet):
    def list(self, request, videoclip_pk=None):
        queryset = self.queryset.filter(videoclip=videoclip_pk)
        read_serializer = self.get_read_serializer_class()
        serializer = read_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, **kwargs):
        videoclip_pk = kwargs.get('videoclip_pk', None)
        view_object = get_object_or_404(
            self.queryset, pk=pk, videoclip=videoclip_pk)

        read_serializer = self.get_read_serializer_class()
        serializer = read_serializer(view_object, many=False)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        videoclip_pk = kwargs.pop('videoclip_pk')
        kwargs['videoclip'] = get_object_or_404(Videoclip, pk=videoclip_pk)
        # kwargs['user'] = request.user
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        videoclip_pk = kwargs.pop('videoclip_pk')
        videoclip = get_object_or_404(Videoclip, pk=videoclip_pk)
        self.queryset = self.queryset.filter(videoclip=videoclip)
        return super().update(request, *args, **kwargs)


class VCCommentView(VCNestedView):

    queryset = VCComment.objects.all()
    serializer_class = VCCommentSerializer
    write_serializer_class = VCCommentEditSerializer
    permission_classes = [AuthorPermission | CommentPermission]

    def create(self, request, *args, **kwargs):
        videoclip_pk = kwargs.get('videoclip_pk', None)
        ban_queryset = VCBan.objects.filter(
            videoclip=videoclip_pk, banned_user=request.user)
        if ban_queryset.count():
            ban: VCBan = ban_queryset[:1].get()
            err = {
                "message": f"Бан до {ban.term_date}"
            }
            return Response(err, status=status.HTTP_400_BAD_REQUEST)

        kwargs['user'] = request.user

        return super().create(request, *args, **kwargs)


class UserReactionView(VCNestedView):

    queryset = UserReaction.objects.all()
    write_serializer_class = UserReactionEditSerializer
    serializer_class = UserReactionSerializer
    permission_classes = [CommentPermission]
    http_method_names = ['get', 'post', 'head', 'delete']

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kwargs['user'] = request.user
        try:
            response = super().create(request, *args, **kwargs)
        except IntegrityError:
            err = {
                "message": f"Уже есть ваша реакция"
            }
            return Response(err, status=status.HTTP_400_BAD_REQUEST)
        return response

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.unregister_reaction()
        return super().perform_destroy(instance)


class VCBanView(VCNestedView):

    queryset = VCBan.objects.all()
    serializer_class = VCBanSerializer
    write_serializer_class = VCBanEditSerializer
    permission_classes = [AuthorPermission]

    def create(self, request, *args, **kwargs):
        videoclip_pk = kwargs.get('videoclip_pk', None)
        videoclip = get_object_or_404(Videoclip, pk=videoclip_pk)

        self.check_object_permissions(request, videoclip)
        try:
            response = super().create(request, *args, **kwargs)
        except IntegrityError:
            err = {
                "message": f"Бан на этого пользователя уже существует"
            }
            return Response(err, status=status.HTTP_400_BAD_REQUEST)

        return response


class VCSubscriptionView(VidnetModelViewSet):

    queryset = VCSubscription.objects.all()
    serializer_class = VCSubscriptionSerializer
    write_serializer_class = VCSubscriptionEditSerializer
    permission_classes = [CommentPermission]
    http_method_names = ['get', 'post', 'head', 'delete']

    def create(self, request, *args, **kwargs):
        kwargs['user'] = request.user

        try:
            response = super().create(request, *args, **kwargs)
        except IntegrityError:
            err = {
                "message": f"Вы уже подписаны на эту категорию"
            }
            return Response(err, status=status.HTTP_400_BAD_REQUEST)

        return response
