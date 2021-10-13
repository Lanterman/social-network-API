from django.urls import path

from main.views import *

urlpatterns = [
    path('', NewsView.as_view(), name='news'),
    path('publish/<int:pk>/', PublishedDetailView.as_view(), name='published-detail'),
    path('groups/', GroupsView.as_view(), name='groups'),
    path('group/<int:pk>/', GroupDetailView.as_view(), name='groups-detail'),
    path('groups/group_add/', AddGroupView.as_view(), name='group_add'),
    path('published/pub_add/', AddPublished.as_view(), name='pub_add'),
]
