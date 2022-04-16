from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, User


class TaskURLTests(TestCase):

    def test_cache_index_page(self):
        super().setUpClass()
        no_user_name = 'noUserName'
        user = User.objects.create_user(username=no_user_name)
        post = Post.objects.create(
            author=user,
            text='Тестовый пост',
        )
        content = Client().get(reverse('posts:index')).content
        Post.objects.filter(id=post.id).delete()
        content_cache = Client().get(reverse('posts:index')).content
        self.assertEqual(content, content_cache, 'Не работает cache страницы')
