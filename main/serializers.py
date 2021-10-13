from rest_framework import serializers

from main.models import Published, Groups


class GroupsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = ('id', 'name', 'slug')


class PublishedSerializers(serializers.HyperlinkedModelSerializer):
    group = GroupsSerializers()
    url = serializers.HyperlinkedIdentityField(view_name='pub_detail')

    class Meta:
        model = Published
        fields = ('url', 'id', 'name', 'slug', 'photo', 'date', 'owner', 'group')


class PublishedDetailSerializers(serializers.HyperlinkedModelSerializer):
    group = GroupsSerializers()

    class Meta:
        model = Published
        fields = ('id', 'name', 'slug', 'photo', 'date', 'owner', 'group')
