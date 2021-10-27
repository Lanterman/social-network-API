from django.urls import path, include
from rest_framework.routers import SimpleRouter

from users.views import *


router = SimpleRouter()
router.register(r'', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('password_change/', ChangePasswordView.as_view(), name='password_change'),
]
