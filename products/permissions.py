from rest_framework import permissions


class IsManagerAndProductOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.groups.filter(name="Manager").exists()
            and obj.added_by == request.user
        )
