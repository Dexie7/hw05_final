from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, User


class FollowTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Mike')
        self.user_two = User.objects.create_user(username='vica')
        self.authorized_client = Client()
        self.authorized_client_two = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_two.force_login(self.user_two)

    def test_following_author(self):

        """Новая запись пользователя не появляется в ленте тех,
        кто не подписан на него."""

        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_authorized_can_unfollow(self):

        """Авторизованный пользователь может отписываться от других
         пользователей."""

        count_follow = Follow.objects.all().count()
        self.authorized_client_two.get(reverse("posts:profile_follow",
                                       kwargs={
                                               "username": self.user
                                               }))
        self.assertEqual(Follow.objects.all().count(), count_follow + 1)
        self.authorized_client_two.get(reverse("posts:profile_unfollow",
                                       kwargs={
                                               "username": self.user
                                               }))
        self.assertEqual(Follow.objects.all().count(), count_follow)

    def test_follow(self):
        '''Проверяем, что авторизованный пользователь
        может подписываться на пользователей'''
        # получаем кол-во записей в подписках
        count_follow = Follow.objects.all().count()
        # подписываемся на автора
        self.authorized_client_two.get(reverse("posts:profile_follow",
                                       kwargs={
                                               "username": self.user
                                               }))
        # проверяем кол-во записей в подписках
        self.assertEqual(Follow.objects.all().count(), count_follow + 1)
