from django.contrib.auth import login, logout
from django.shortcuts import redirect
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from users.permissions import Anonymous
from users.serializers import *


class UserRegisterView(generics.CreateAPIView):
    """Регистрация пользователей"""

    serializer_class = UserSerializer
    permission_classes = [Anonymous]

    def perform_create(self, serializer):
        user = serializer.save()
        login(self.request, user)
        user.set_password(str(self.request.data.get('password')))
        user.slug = user.username
        user.save()


# class ProfileUser(DataMixin, DetailView):
#     model = Users
#     template_name = 'users/profile.html'
#     pk_url_kwarg = 'user_pk'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context | self.get_context(title='Мой профиль')


def logout_view(request):
    logout(request)
    return redirect('news')


class ChangePasswordView(generics.UpdateAPIView):  # Доработать(валидация паролей на сложность и т. д.)
    serializer_class = UserChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        password = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not password.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Неверный пароль!"]}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.data.get("new_password1") != serializer.data.get("new_password2"):
                return Response({"new_password": ["Пароли не совпадают!."]}, status=status.HTTP_400_BAD_REQUEST)
            password.set_password(serializer.data.get("new_password1"))
            password.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserView(generics.UpdateAPIView):  # Доработать
    serializer_class = UpdateUserSerializer
    queryset = Users.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

