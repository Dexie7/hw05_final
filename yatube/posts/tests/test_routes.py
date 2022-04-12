from django.test import TestCase
from django.urls import reverse


AUTHOR = 'user_test'
POST_ID = 1
GROUP_SLUG = 'test-slug'


class RoutesTest(TestCase):
    def test_routes(self):
        urls_routes_names = [
            [reverse('posts:index'), '/'],
            [reverse('posts:post_create'), '/create/'],
            [reverse(
                'posts:group_list',
                args=[GROUP_SLUG]),
             f'/group/{GROUP_SLUG}/'],
            [reverse(
                'posts:profile',
                args=[AUTHOR]),
             f'/profile/{AUTHOR}/'],
            [reverse(
                'posts:post_detail',
                args=[POST_ID]),
             f'/posts/{POST_ID}/'],
            [reverse(
                'posts:post_edit',
                args=[POST_ID]),
             f'/posts/{POST_ID}/edit/']
        ]
        for url, route in urls_routes_names:
            self.assertEqual(url, route)
