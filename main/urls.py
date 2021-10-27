from django.urls import path
from rest_framework.routers import SimpleRouter

from main.views import *


router = SimpleRouter()
router.register(r'published', PublishViewSet, basename='published')
router.register(r'group', GroupsViewSet, basename='groups')
router.register(r'friends', UserViewSet, basename='users')


urlpatterns = [
    # path('home/<int:pk>/', HomeView.as_view(), name='users-detail'),
    path('messages/', MessagesView.as_view(), name='messages'),
    path('chat/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),
    # path('friends/<int:pk>/', FriendsView.as_view(), name='friends'),

    path('group/group_add/', AddGroupView.as_view(), name='group_add'),
    path('group/<int:pk>/pub_add/', AddPublishedView.as_view(), name='pub_add'),
    path('publish/<int:pk>/comments_add/', AddCommentView.as_view(), name='comments_add'),
    # Logic
    path('publish/<int:pk>/add_rating/', AddStarRating.as_view(), name='add_rating'),
    ]

urlpatterns += router.urls
