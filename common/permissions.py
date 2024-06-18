from .utils import is_user_manager
from rest_framework import permissions


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_user_manager(request.user)
