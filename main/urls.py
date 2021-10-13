from django.urls import path

from main.views import *

urlpatterns = [
    path('', PublishedListView.as_view(), name='pub_list'),
]
