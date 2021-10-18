from rest_framework import generics

from main.models import Published, Groups
from main.pagination import PaginationPublished
from main.serializers import *


class PublishedListView(generics.ListAPIView):
    """Вывод списка публикаций в зависимости от авторизации"""
    queryset = Published.objects.all()
    serializer_class = PublishedSerializer
    pagination_class = PaginationPublished

    def get_queryset(self):
        if self.request.user.is_authenticated:
            groups = Groups.objects.filter(users__username=self.request.user.username)
            if groups:
                published = Published.objects.filter(group_id__in=[group.id for group in groups])
            else:
                published = ''
        else:
            published = Published.objects.all()
        return published


class PublishedDetailView(generics.RetrieveAPIView):
    queryset = Published.objects.all()
    serializer_class = PublishedSerializer


class GroupsView(generics.ListAPIView):
    queryset = Groups.objects.all()
    serializer_class = GroupsSerializer


class GroupDetailView(generics.RetrieveAPIView):
    queryset = Groups.objects.all()
    serializer_class = GroupsSerializer


class AddGroupView(generics.CreateAPIView):
    serializer_class = GroupsSerializer


class AddPublished(generics.CreateAPIView):
    serializer_class = PublishedAddSerializer
