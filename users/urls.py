from django.urls import path

from users.views import *

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/<int:pk>/', ProfileUserView.as_view(), name='profile'),
    path('password_change/', ChangePasswordView.as_view(), name='password_change'),
    path('update_user/<int:pk>/', UpdateUserView.as_view(), name='update_user')
]