from django.db.models import Avg
from django.test import TestCase
from main.models import Groups, Rating, RatingStar
from main.serializers import *
from users.models import Users, Chat


class PublishedSerializerTestCase(TestCase):
    def test_is_valid(self):
        group_1 = Groups.objects.create(name='group_1', slug='group_1')
        pub_1 = Published.objects.create(name='pub_1', slug='pub_1', group_id=group_1.id)
        pub_2 = Published.objects.create(name='pub_2', slug='pub_2', group_id=group_1.id)
        value_1 = RatingStar.objects.create(value=3)
        value_2 = RatingStar.objects.create(value=4)
        Rating.objects.create(ip='user_1', published=pub_1, star=value_1)
        Rating.objects.create(ip='user_2', published=pub_1, star=value_1)
        Rating.objects.create(ip='user_1', published=pub_2, star=value_2)
        pub = Published.objects.all().annotate(rat=Avg('rating__star__value')).order_by('-date')
        data = PublishedSerializer(pub, many=True, context={'request': None}).data
        self.assertEquals(data[0]['url'], '/publish/2/')
        self.assertEquals(data[1]['group'], '/group/1/')
        self.assertEquals(data[0]['rat'], '4.00')


class UsersProfileSerializerTestCase(TestCase):
    def test_is_valid(self):
        for group in range(2):
            Groups.objects.create(name='group_%s' % group, slug='group_%s' % group)
        groups = Groups.objects.all()
        user = Users.objects.create(username='user', email='user@mail.ru')
        Published.objects.create(name='pub_1', slug='pub_1', group_id=groups[0].id, owner=user)

        data = UsersProfileFSerializer(user, context={'request': None}).data
        exp_data = {
            'username': 'user', 'first_name': '', 'last_name': '', 'email': 'user@mail.ru', 'num_tel': '',
            'photo': None,'friends': [], 'my_group': [], 'groups_users': [], 'ow_ip': [], 'us_ip': [],
            'my_published': [{'url': '/publish/3/', 'name': 'pub_1'}]
        }
        self.assertEquals(data, exp_data)


class HomeUpdateSerializerTestCase(TestCase):
    def test_is_valid(self):
        user = Users.objects.create(username='user', email='user@mail.ru', photo=None)
        data = UsersProfileFSerializer(user, context={'request': None}).data
        self.assertEquals(data['photo'], None)


class MessagesSerializerTestCase(TestCase):
    def test_is_valid(self):
        for user in range(2):
            Users.objects.create(username='user_%s' % user, email='user%s@mail.ru' % user)
        users = Users.objects.all()
        chat = Chat.objects.create()
        chat.members.add(users[0], users[1])
        Message.objects.create(chat_id=chat.id, author=users[0])
        Message.objects.create(chat_id=chat.id, author=users[1], is_readed=True)
        messages = Message.objects.all()
        data = MessagesSerializer(messages, many=True,  context={'request': None}).data
        self.assertEquals(data[0]['chat'], '/chat/2/')
        self.assertEquals(data[0]['is_readed'], True)
        self.assertEquals(data[1]['is_readed'], False)
        self.assertEquals(data[0]['author'], 'user_1')


class ChatMessagesSerializerTestCase(TestCase):
    def test_is_valid(self):
        for user in range(2):
            Users.objects.create(username='user_%s' % user, email='user%s@mail.ru' % user)
        users = Users.objects.all()
        chat = Chat.objects.create()
        chat.members.add(users[0], users[1])
        Message.objects.create(chat_id=chat.id, author=users[0])
        Message.objects.create(chat_id=chat.id, author=users[1], is_readed=True)
        messages = Message.objects.all()
        data = ChatMessagesSerializer(messages, many=True,  context={'request': None}).data
        self.assertEquals(data[0]['chat'], 1)
        self.assertEquals(data[0]['is_readed'], True)
        self.assertEquals(data[1]['is_readed'], False)
        self.assertEquals(data[0]['author'], 'user_1')


class RatingSerializerTestCase(TestCase):
    def test_is_valid(self):
        group_1 = Groups.objects.create(name='group_1', slug='group_1')
        pub_1 = Published.objects.create(name='pub_1', slug='pub_1', group_id=group_1.id)
        pub_2 = Published.objects.create(name='pub_2', slug='pub_2', group_id=group_1.id)
        value_1 = RatingStar.objects.create(value=3)
        value_2 = RatingStar.objects.create(value=4)
        Rating.objects.create(ip='user_1', published=pub_1, star=value_1)
        Rating.objects.create(ip='user_1', published=pub_2, star=value_2)
        rating = Rating.objects.all()
        data_1 = RatingSerializer(rating[0], context={'request': None}).data
        data_2 = RatingSerializer(rating[1], context={'request': None}).data
        self.assertEquals(data_1['star'].value, 3)
        self.assertEquals(data_2['star'].value, 4)
