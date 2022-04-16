from django.shortcuts import reverse
from django.test import Client, TestCase

from posts.models import Follow, Group, Post, User

SLUG = 'test-slug'
USERNAME = 'user_test'
AUTHOR_USERNAME = 'author_name'
FOLLOW_URL = reverse('posts:follow_index')
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[AUTHOR_USERNAME])
PROFILE_UNFOLLOW_URL = reverse(
    'posts:profile_unfollow',
    args=[AUTHOR_USERNAME]
)


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.user_author = User.objects.create(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user_author,
            group=cls.group,
        )
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)

    def test_post_with_group_not_appear_at_wrong_follower_page(self):
        """"Новая запись пользователя не появляется в ленте тех,
        кто не подписан на него.
        """
        self.assertFalse(
            Follow.objects.filter(
                user=self.user.id,
                author=self.post.author.id
            ).exists()
        )
        response = self.author.get(FOLLOW_URL)
        self.assertNotIn(
            self.post,
            response.context['page_obj']
        )

    def test_authorized_user_can_follow_author(self):
        """Авторизованный пользователь может подписываться
        на других пользователей.
        """
        self.assertFalse(
            Follow.objects.filter(
                user=self.user.id,
                author=self.post.author.id
            ).exists()
        )
        self.author.get(PROFILE_FOLLOW_URL)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user.id,
                author=self.post.author.id
            ).exists()
        )

    def test_authorized_user_can_unfollow_author(self):
        """Авторизованный пользователь может удалять
        из подписок других пользователей.
        """
        Follow.objects.create(
            user=self.user,
            author=self.post.author
        )
        self.author.get(PROFILE_UNFOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user.id,
                author=self.post.author.id
            ).exists()
        )
