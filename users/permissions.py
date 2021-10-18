from rest_framework import permissions


class Anonymous(permissions.BasePermission):
    def has_permission(self, request, view):
        return not bool(request.user.is_authenticated)


class ID(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.pk == request.user.pk
