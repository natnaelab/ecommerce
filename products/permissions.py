from rest_framework import permissions
from common.utils import is_user_manager


class IsManagerAndProductOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return is_user_manager(request.user) and obj.added_by == request.user


class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            is_user_manager(request.user) or request.method in permissions.SAFE_METHODS
        )
