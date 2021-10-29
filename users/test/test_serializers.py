from django.test import TestCase

from users.models import Users
from users.serializers import *


class ProfileUserSerializerTestCase(TestCase):
    def test_is_valid(self):
        user_1 = Users.objects.create(username='user_1', email='user_1@mail.ru', num_tel='3752257213',
                                      first_name='user_1', last_name='user_1')
        user_2 = Users.objects.create(username='user_2', email='user_2@mail.ru', num_tel='3752257213',
                                      first_name='user_2', last_name='user_2')
        data = ProfileSerializer([user_1, user_2], many=True).data
        exp_data = [{'first_name': 'user_1', 'last_name': 'user_1', 'email': 'user_1@mail.ru', 'num_tel': '3752257213'},
                    {'first_name': 'user_2', 'last_name': 'user_2', 'email': 'user_2@mail.ru', 'num_tel': '3752257213'}]
        self.assertEqual(data[0]['first_name'], 'user_1')
        self.assertEqual(data, exp_data)
        self.assertEqual(len(data), 2)


class UpdateUserSerializerTestCase(TestCase):
    def test_is_valid(self):
        user_1 = Users.objects.create(username='user_1', email='user_1@mail.ru', num_tel='3752257213',
                                      first_name='user_1', last_name='user_1')
        user_2 = Users.objects.create(username='user_2', email='user_2@mail.ru', num_tel='3752257213',
                                      first_name='user_2', last_name='user_2')
        data = ProfileSerializer([user_1, user_2], many=True).data
        exp_data = [{'first_name': 'user_1', 'last_name': 'user_1', 'email': 'user_1@mail.ru', 'num_tel': '3752257213'},
                    {'first_name': 'user_2', 'last_name': 'user_2', 'email': 'user_2@mail.ru', 'num_tel': '3752257213'}]
        self.assertEqual(data[0]['first_name'], 'user_1')
        self.assertEqual(data, exp_data)
