from django.urls import path

from main.views import *

urlpatterns = [
    path('', PublishedListView.as_view(), name='news'),
    path('home/<int:pk>/', HomeView.as_view(), name='users-detail'),
    path('home/<int:pk>/update/', HomeUpdateView.as_view(), name='update'),
    path('messages/', MessagesView.as_view(), name='messages'),
    path('chat/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),
    path('publish/<int:pk>/', PublishedDetailView.as_view(), name='published-detail'),
    path('groups/', GroupsView.as_view(), name='groups'),
    path('group/<int:pk>/', GroupDetailView.as_view(), name='groups-detail'),
    path('groups/group_add/', AddGroupView.as_view(), name='group_add'),
    path('published/pub_add/', AddPublished.as_view(), name='pub_add'),
]
