from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


AUTHOR = 'user_test'
POST_TEXT = 'Тестовый тест'
GROUP_TITLE = 'Тестовый заголовок'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Описание тестовой группы'
AUTH = reverse('login')
FAKE_PAGE = '/fake/page'
INDEX_URL = reverse('posts:index')
NEW_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', kwargs={'slug': GROUP_SLUG})
PROFILE_URL = reverse('posts:profile', args=[AUTHOR])


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.some_user = User.objects.create_user(username='someuser')
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            description=GROUP_DESCRIPTION,
            slug=GROUP_SLUG
        )
        cls.post = Post.objects.create(
            text='a' * 20,
            author=cls.user
        )
        cls.VIEW_POST = reverse(
            'posts:post_detail',
            kwargs={
                'post_id': cls.post.id}
        )
        cls.POST_EDIT = reverse(
            'posts:post_edit',
            kwargs={
                'post_id': cls.post.id}
        )

    def setUp(self):
        self.guest = Client()
        self.author = Client()
        self.author.force_login(self.user)
        self.another = Client()
        self.another.force_login(self.some_user)

    def test_pages_codes(self):
        """Страницы доступны любому пользователю."""
        SUCCESS = 200
        REDIRECT = 302
        NOT_FOUND = 404
        url_names = [
            [self.author, NEW_URL, SUCCESS],
            [self.author, self.POST_EDIT, SUCCESS],
            [self.another, self.POST_EDIT, REDIRECT],
            [self.guest, INDEX_URL, SUCCESS],
            [self.guest, NEW_URL, REDIRECT],
            [self.guest, self.POST_EDIT, REDIRECT],
            [self.guest, GROUP_URL, SUCCESS],
            [self.guest, PROFILE_URL, SUCCESS],
            [self.guest, self.VIEW_POST, SUCCESS],
            [self.guest, FAKE_PAGE, NOT_FOUND]
        ]
        for client, url, code in url_names:
            with self.subTest(url=url):
                self.assertEqual(code, client.get(url).status_code)

    def test_redirect(self):
        """Перенаправление пользователя."""
        templates_url_names = [
            [self.another, self.POST_EDIT, self.VIEW_POST],
            [self.guest, NEW_URL, AUTH + '?next=' + NEW_URL],
            [self.guest, self.POST_EDIT, AUTH + '?next=' + self.POST_EDIT],
        ]
        for client, url, url_redirect in templates_url_names:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url, follow=True),
                                     url_redirect)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX_URL: 'posts/index.html',
            NEW_URL: 'posts/create_post.html',
            GROUP_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.VIEW_POST: 'posts/post_detail.html',
            self.POST_EDIT: 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.author.get(url),
                    template
                )
