from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from scr.main.serializers import *
from scr.users.models import Users, Chat


class PublishViewSetAPITest(APITestCase):
    def setUp(self):
        self.user = Users.objects.create_user(username='user1', password='12345', email='user@mail.ru')
        group = Groups.objects.create(name='group', slug='group', owner_id=self.user.id)
        group.users.add(self.user)
        Published.objects.create(name='pub_1', slug='pub_1', owner_id=self.user.id, group_id=group.id)
        Published.objects.create(name='pub_2', slug='pub_2', owner_id=self.user.id, group_id=group.id)
        self.pub = Published.objects.all()
        self.pub_1 = self.pub[1]

    def test_list(self):
        url = reverse('published-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_search(self):
        url = reverse('published-list')
        response = self.client.get(url, data={'search': 'pub_1'})
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_retrieve(self):
        url = reverse('published-detail', kwargs={'pk': self.pub_1.pk})
        response = self.client.get(url)
        data = {'url': f'http://testserver/friends/{self.pub_1.owner.pk}/', 'username': 'user1'}
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(response.data), 8)
        self.assertEqual(response.data['owner'], data)

    def test_add_rating(self):
        url = f'http://127.0.0.1:8000/published/{self.pub_1.pk}/add_rating/'
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class GroupViewSetAPITest(APITestCase):
    def setUp(self):
        self.user = Users.objects.create_user(username='user1', password='12345', email='user@mail.ru')
        self.group = Groups.objects.create(name='group', slug='group', owner_id=self.user.id)
        self.group.users.add(self.user)

    def test_list(self):
        self.client.force_login(self.user)
        url = reverse('groups-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_search(self):
        self.client.force_login(self.user)
        url = reverse('groups-list')
        response = self.client.get(url, data={'search': 'group'})
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_retrieve(self):
        self.client.force_login(self.user)
        url = reverse('groups-detail', kwargs={'pk': self.group.pk})
        response = self.client.get(url)
        data = {'url': f'http://testserver/friends/{self.group.owner.pk}/', 'username': 'user1'}
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data['owner'], data)


class UserViewSetAPITest(APITestCase):
    def setUp(self):
        for user_num in range(3):
            Users.objects.create_user(username='user_%s' % user_num, password='12345', num_tel=12345678910,
                                      email='user_%s@mail.ru' % user_num)
        self.users = Users.objects.all()
        self.users[0].friends.add(self.users[1])

    def test_list(self):
        self.client.force_login(self.users[0])
        url = reverse('users-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_search(self):
        self.client.force_login(self.users[0])
        url = reverse('users-list')
        response = self.client.get(url, data={'search': 'user_0'})
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_retrieve(self):
        self.client.force_login(self.users[0])
        url = reverse('users-detail', kwargs={'pk': self.users[0].pk})
        response = self.client.get(url)
        data = [{'url': f'http://testserver/friends/{self.users[1].pk}/', 'username': 'user_1'}]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(response.data), 12)
        self.assertEqual(response.data['friends'], data)

    def test_chat(self):
        Chat.objects.create()
        chat = Chat.objects.all()
        chat[0].members.add(self.users[0], self.users[1])
        users = len(chat[0].members.all())
        self.assertEqual(len(chat), 1)
        self.assertFalse(self.users[2] in chat[0].members.all())
        self.assertEqual(self.users[1] in chat[0].members.all(), self.users[0] in chat[0].members.all())
        self.assertTrue(users == 2)


class CommentViewSetAPITest(APITestCase):
    def setUp(self):
        self.user = Users.objects.create_user(username='user1', password='12345', email='user@mail.ru')
        group = Groups.objects.create(name='group', slug='group', owner_id=self.user.id)
        self.pub = Published.objects.create(name='pub_1', slug='pub_1', owner_id=self.user.id, group_id=group.id)
        self.comment = Comments.objects.create(published_id=self.pub.id, users_id=self.user.id)

    def test_retrieve(self):
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        response = self.client.get(url)
        data = {'url': f'http://testserver/friends/{self.comment.users.pk}/', 'username': 'user1'}
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data['users'], data)
