from rest_framework import permissions

from users.models import Users


class Anonymous(permissions.BasePermission):
    def has_permission(self, request, view):
        return not bool(request.user.is_authenticated)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.pk == request.user.pk


class IsOwnerOrClose(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.pk == request.user.pk


class CheckMembers(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = Users.objects.get(pk=request.user.pk)
        return user in obj.members.all()


class IsOwnerGroup(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner.pk == request.user.pk


class IsOwnerPublished(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner.pk == request.user.pk or obj.group.owner == request.user.pk


# class ReadOnlyIfAnonymous(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         if not request.user.is_authenticated:
#             return False
#         return True
