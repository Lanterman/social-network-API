from django.urls import path

from main.views import *

urlpatterns = [
    path('', PublishedListView.as_view(), name='news'),
    path('home/<int:pk>/', HomeView.as_view(), name='users-detail'),
    path('messages/', MessagesView.as_view(), name='messages'),
    path('chat/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),
    path('friends/<int:pk>/', FriendsView.as_view(), name='friends'),
    path('groups/<int:pk>/', GroupsView.as_view(), name='groups'),
    path('group/group_add/', AddGroupView.as_view(), name='group_add'),
    path('group/<int:pk>/', DetailGroupView.as_view(), name='groups-detail'),
    path('group/<int:pk>/pub_add/', AddPublishedView.as_view(), name='pub_add'),
    path('publish/<int:pk>/', DetailPublishView.as_view(), name='published-detail'),
    path('publish/<int:pk>/comments_add/', AddCommentView.as_view(), name='comments_add'),
    # Logic
    path('group/<int:pk>/group_update/', UpdateGroup.as_view(), name='update_group'),
    path('publish/<int:pk>/pub_update/', UpdatePublished.as_view(), name='update_pub'),
    path('publish/<int:pk>/add_rating/', AddStarRating.as_view(), name='add_rating'),
    ]
