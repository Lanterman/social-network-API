from django.urls import path

from main.views import *

urlpatterns = [
    path('', api_root, name='api_root'),
    path('published/list', PublishedListView.as_view(), name='pub_list'),
    path('published/<int:pk>', PublishedDetailView.as_view(), name='pub_detail'),
]
