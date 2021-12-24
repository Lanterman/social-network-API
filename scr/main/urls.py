from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()
router.register(r'published', PublishViewSet, basename='published')
router.register(r'groups', GroupsViewSet, basename='groups')
router.register(r'friends', UserViewSet, basename='users')
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'comment', CommentViewSet, basename='comment')


urlpatterns = [
    path('chat/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),
    # path('comment/<int:pk>/', CommentViewSet.as_view({'get': 'retrieve'}), name='comment_detail'),
    # path('comment/<int:pk>/add_like', CommentViewSet.as_view({'get': 'add_like_comment'}), name='add_like_comment'),
    ]

urlpatterns += router.urls
