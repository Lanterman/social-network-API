from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from main.models import Published, Groups
from main.serializers import *


@api_view(['GET'])
def api_root(request):
    return Response({
        'published', reverse('pub_list', request=request)
    })


class PublishedListView(generics.ListAPIView):
    queryset = Published.objects.all()
    serializer_class = PublishedSerializers


class PublishedDetailView(generics.RetrieveAPIView):
    queryset = Published.objects.all()
    serializer_class = PublishedDetailSerializers


