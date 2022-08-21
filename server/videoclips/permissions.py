from rest_framework import permissions

from videoclips.models import VCBan, VCCategory, Videoclip


class AuthorPermission (permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_staff:
            return True

        if isinstance(obj, (Videoclip)):
            return obj.author == request.user

        if isinstance(obj, (VCCategory, VCBan)) and view.action == 'destroy':
            return obj.videoclip.author == request.user

        return False


class CommentPermission (permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and
            request.user.is_staff
        )
