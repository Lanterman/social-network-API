from rest_framework import serializers

from main.models import Published


class PublishedSerializers(serializers.ModelSerializer):
    class Meta:
        model = Published
        fields = ('id', 'name', 'slug', 'photo', 'date', 'owner', 'group')
