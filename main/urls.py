from django.urls import path

from main.views import *

urlpatterns = [
    path('', PublishedListView.as_view(), name='news'),
    path('home/<int:pk>/', HomeView.as_view(), name='users-detail'),
    path('messages/', MessagesView.as_view(), name='messages'),
    path('chat/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),
    path('friends/<int:pk>/', FriendsView.as_view(), name='friends'),
    path('groups/<int:pk>/', GroupsView.as_view(), name='groups'),
    path('groups/group_add/', AddGroupView.as_view(), name='group_add'),
    path('group/<int:pk>/', DetailGroupView.as_view(), name='groups-detail'),

    path('published/pub_add/', AddPublished.as_view(), name='pub_add'),
    path('publish/<int:pk>/', PublishedDetailView.as_view(), name='published-detail'),
]
