from django.urls import path, include

urlpatterns = [
    path('', include('scr.main.urls')),
    path('users/', include('scr.users.urls')),
]
