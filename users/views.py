from rest_framework import generics, status, permissions
from rest_framework.response import Response

from users.permissions import *
from users.serializers import *


class UserRegisterView(generics.CreateAPIView):
    """Регистрация пользователей"""

    serializer_class = UserSerializer
    permission_classes = [Anonymous]

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(str(self.request.data.get('password')))
        user.slug = user.username
        user.save()


class UpdateUserView(generics.UpdateAPIView):  # Соединить с ProfileUserView
    queryset = Users.objects.all()
    serializer_class = UpdateUserSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrClose)


class ProfileUserView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = ProfileUserSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrClose)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = UserChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not obj.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Неверный пароль!"]}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.data.get("new_password1") != serializer.data.get('new_password2'):
                return Response({"new_password": ["Пароли не совпадают!"]}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.data.get("new_password1") == serializer.data.get("old_password"):
                return Response('Новый пароль не может быть похож на старый!')
            obj.set_password(serializer.data.get("new_password1"))
            obj.save()
            return Response('Пароль успешно изменен!', status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
