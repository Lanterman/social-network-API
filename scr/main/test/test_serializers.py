from django.db.models import Avg
from django.test import TestCase
from scr.main.models import Groups, Rating, RatingStar
from scr.main.serializers import *
from scr.users.models import Users, Chat


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
        self.assertEquals(data[0]['url'], '/published/2/')
        self.assertEquals(data[1]['group'], '/groups/1/')
        self.assertEquals(data[0]['rat'], '4.00')


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
        rat_1 = Rating.objects.create(ip='user_1', published=pub_1, star_id=value_1.id)
        rat_2 = Rating.objects.create(ip='user_2', published=pub_2, star_id=value_2.id)
        data_1 = RatingSerializer(rat_1, context={'request': None}).data
        data_2 = RatingSerializer(rat_2, context={'request': None}).data
        self.assertEquals(data_1['star'], 3)
        self.assertEquals(data_2['star'], 4)
