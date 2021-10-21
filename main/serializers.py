from rest_framework import serializers

from main.models import Published, Groups, Comments
from users.models import Users, PostSubscribers, Message, Chat


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Users
        fields = ('url', 'username')


class MyGroupsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Groups
        fields = ('url', 'name')


class MyPublishedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Published
        fields = ('url', 'name')


class PostSubOwnerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = PostSubscribers
        fields = ('user', 'date', 'escape')


class PostSubUserSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = PostSubscribers
        fields = ('owner', 'date', 'escape')


# Main
class PublishedSerializer(serializers.HyperlinkedModelSerializer):
    rat = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner = UserSerializer()

    class Meta:
        model = Published
        fields = ('url', 'name', 'slug', 'photo', 'group', 'rat', 'owner', 'date')


class UsersProfileSerializer(serializers.HyperlinkedModelSerializer):
    friends = UserSerializer(many=True)
    my_group = MyGroupsSerializer(many=True)
    groups_users = MyGroupsSerializer(many=True)
    my_published = MyPublishedSerializer(many=True)
    ow_ip = PostSubOwnerSerializer(many=True)
    us_ip = PostSubUserSerializer(many=True)

    class Meta:
        model = Users
        fields = ('username', 'first_name', 'last_name', 'email', 'num_tel', 'photo', 'friends', 'my_group',
                  'groups_users', 'ow_ip', 'us_ip', 'my_published')


class HomeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('photo',)


class MessagesSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.SlugField(source='author.username')

    class Meta:
        model = Message
        fields = ('chat', 'author', 'message', 'pub_date', 'is_readed')


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'





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
