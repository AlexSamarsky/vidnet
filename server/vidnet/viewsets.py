from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


class VidnetModelViewSet(ModelViewSet):
    write_serializer_class = None
    read_serializer_class = None

    permission_classes_by_action = {
        'list': [AllowAny],
        'retrieve': [AllowAny]
    }

    serializers = {
        'default': None
    }

    def get_write_serializer_class(self):
        if hasattr(self, 'write_serializer_class') and self.write_serializer_class:
            return self.write_serializer_class

        return self.serializer_class

    def get_read_serializer_class(self):
        if hasattr(self, 'read_serializer_class') and self.read_serializer_class:
            return self.read_serializer_class

        return self.serializer_class

    def get_serializer_class(self):
        serializer = self.serializers.get(self.action, None)
        if serializer:
            return serializer

        if hasattr(self, 'write_serializer_class') and self.write_serializer_class and self.action in ['create', 'update', 'partial_update']:
            return self.write_serializer_class

        if hasattr(self, 'read_serializer_class') and self.read_serializer_class and self.action in ['list', 'retrieve']:
            return self.read_serializer_class

        return self.serializer_class

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        serializer_edit_object = self.get_write_serializer_class()
        serializer_edit = serializer_edit_object(data=request.data)
        if serializer_edit.is_valid():
            obj = serializer_edit.save(**kwargs)
            serializer_read_object = self.get_read_serializer_class()
            serializer_read = serializer_read_object(
                obj, context={'request': request, "format": None, 'view': obj})
            # serializer_object = serializer
            return Response(data=serializer_read.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer_edit.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, **kwargs):
        return super().perform_create(serializer)

    def update(self, request, *args, **kwargs):
        # super().update(request, *args, **kwargs)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        obj = self.get_object()
        serializer_read_object = self.get_read_serializer_class()
        serializer_read = serializer_read_object(
            obj, context={'request': request, "format": None, 'view': obj})
        return Response(data=serializer_read.data, status=status.HTTP_201_CREATED)
