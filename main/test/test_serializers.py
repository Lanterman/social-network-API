from django.db.models import Avg
from django.test import TestCase
from main.models import Groups, Rating, RatingStar
from main.serializers import *
from users.models import Users


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
        pub = Published.objects.all().annotate(rat=Avg('rating__star_id')).order_by('-date')
        data = PublishedSerializer(pub, many=True, context={'request': None}).data
        print(data)
        self.assertEquals(data[0]['url'], '/publish/2/')
        self.assertEquals(data[1]['group'], '/group/1/')
        # self.assertEquals(data[0]['rat'], '4.00')
