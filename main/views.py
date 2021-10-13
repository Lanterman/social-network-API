from rest_framework import generics

from main.models import Published
from main.serializers import PublishedSerializers


class PublishedListView(generics.ListAPIView):
    queryset = Published.objects.all()
    serializer_class = PublishedSerializers
