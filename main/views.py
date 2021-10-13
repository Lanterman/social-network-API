from rest_framework import generics

from main.models import Published, Groups
from main.pagination import PaginationPublished
from main.serializers import *


class NewsView(generics.ListAPIView):
    queryset = Published.objects.all()
    serializer_class = PublishedSerializer
    pagination_class = PaginationPublished


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
    queryset = Groups.objects.all()
    serializer_class = GroupsSerializer


class AddPublished(generics.CreateAPIView):
    queryset = Published.objects.all()
    serializer_class = PublishedAddSerializer
