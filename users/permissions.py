from rest_framework import permissions


class Anonymous(permissions.BasePermission):
    def has_permission(self, request, view):
        return not bool(request.user.is_authenticated)
