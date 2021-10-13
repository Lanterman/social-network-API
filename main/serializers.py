from rest_framework import serializers

from main.models import Published, Groups, Comments


class PublishedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Published
        fields = ('url', 'name', 'slug', 'photo', 'owner', 'group', 'date')


class GroupsSerializer(serializers.ModelSerializer):
    published = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)

    class Meta:
        model = Groups
        fields = ('name', 'slug', 'published')


class PublishedAddSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Published
        fields = ('url', 'name', 'slug', 'photo', 'group')


class CommentsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comments
        fields = ('published', 'users', 'biography', 'date', 'like')
