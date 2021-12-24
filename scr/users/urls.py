from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import *


router = SimpleRouter()
router.register(r'profile', UserProfileViewSet, basename='profile')


urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('password_change/', ChangePasswordView.as_view(), name='password_change'),
    path('', include(router.urls)),
]
