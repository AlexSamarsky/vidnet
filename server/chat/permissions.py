from rest_framework import permissions


class RoomPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.current_users.filter(id=request.user.id).exists():
            return True

        return False
