from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


AUTHOR = 'user_test'
POST_TEXT = 'Тестовый тест'
GROUP_TITLE = 'Тестовый заголовок'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Описание тестовой группы'
LOGIN_URL = f'{reverse("login")}?next='
FAKE_PAGE = '/fake/page'
INDEX_URL = reverse('posts:index')
NEW_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', args=[GROUP_SLUG])
PROFILE_URL = reverse('posts:profile', args=[AUTHOR])
FOLLOW_URL = reverse('posts:follow_index')
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[AUTHOR])
PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[AUTHOR])


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
        cls.COMMENT_URL = reverse(
            'posts:add_comment',
            kwargs={
                'post_id': cls.post.id}
        )
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.another = Client()
        cls.another.force_login(cls.some_user)

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
            [self.guest, FOLLOW_URL, REDIRECT],
            [self.another, FOLLOW_URL, SUCCESS],
            [self.guest, PROFILE_FOLLOW_URL, REDIRECT],
            [self.another, PROFILE_FOLLOW_URL, REDIRECT],
            [self.author, PROFILE_FOLLOW_URL, REDIRECT],
            [self.guest, PROFILE_UNFOLLOW_URL, REDIRECT],
            [self.another, PROFILE_UNFOLLOW_URL, REDIRECT],
            [self.guest, self.COMMENT_URL, REDIRECT],
            [self.another, self.COMMENT_URL, REDIRECT],
            [self.author, self.COMMENT_URL, REDIRECT],
            [self.guest, FAKE_PAGE, NOT_FOUND]
        ]
        for client, url, code in url_names:
            with self.subTest(url=url):
                self.assertEqual(code, client.get(url).status_code)

    def test_redirect(self):
        """Перенаправление пользователя."""
        templates_url_names = [
            [self.guest, NEW_URL, LOGIN_URL + NEW_URL],
            [self.guest, PROFILE_FOLLOW_URL, LOGIN_URL + PROFILE_FOLLOW_URL],
            [self.another, PROFILE_FOLLOW_URL, PROFILE_URL],
            [self.author, PROFILE_FOLLOW_URL, PROFILE_URL],
            [self.guest, PROFILE_UNFOLLOW_URL,
                LOGIN_URL + PROFILE_UNFOLLOW_URL],
            [self.another, PROFILE_UNFOLLOW_URL, PROFILE_URL],
            [self.another, self.POST_EDIT, self.VIEW_POST],
            [self.guest, self.POST_EDIT, LOGIN_URL + self.POST_EDIT],
            [self.guest, self.COMMENT_URL, LOGIN_URL + self.COMMENT_URL],
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
            FOLLOW_URL: 'posts/follow.html',
            self.VIEW_POST: 'posts/post_detail.html',
            self.POST_EDIT: 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.author.get(url),
                    template
                )
