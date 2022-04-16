import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import Client, TestCase, override_settings

from posts.models import Comment, Group, Post, User
from yatube.settings import MAX_PAGE_COUNT

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SLUG = 'test-slug'
USERNAME = 'test_name'
AUTHOR_USERNAME = 'author_name'
INDEX_URL = reverse('posts:index')
POST_GROUP_URL = reverse('posts:group_list', args=[SLUG])
FOLLOW_URL = reverse('posts:follow_index')
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[AUTHOR_USERNAME])
PROFILE_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])
TEST_IMAGE = (b'\x47\x49\x46\x38\x39\x61\x01\x00'
              b'\x01\x00\x00\x00\x00\x21\xf9\x04'
              b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
              b'\x00\x00\x01\x00\x01\x00\x00\x02'
              b'\x02\x4c\x01\x00\x3b')
IMAGE_NAME = 'test_image.gif'
IMAGE_TYPE = 'image/gif'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.image = SimpleUploadedFile(
            name=IMAGE_NAME,
            content=TEST_IMAGE,
            content_type=IMAGE_TYPE
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user_author,
            group=cls.group,
            image=cls.image
        )
        cls.comment = Comment.objects.create(
            text='Текст комментария',
            post=cls.post,
            author=cls.user
        )
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_on_pages_show_correct_context(self):
        """Страницы с постами сформированы с правильным контекстом."""
        self.author.get(PROFILE_FOLLOW_URL)
        urls = [INDEX_URL, POST_GROUP_URL, PROFILE_URL,
                self.POST_URL, FOLLOW_URL]
        for url in urls:
            with self.subTest(url=url):
                response = self.author.get(url)
                if 'post' in response.context:
                    post = response.context['post']
                else:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    post = response.context['page_obj'][0]
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.image.name, self.post.image.name)

    def test_context_comment(self):
        """Проверка комментария"""
        response = self.author.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id})
        )
        comment = response.context['comments'].first()
        self.assertIsNotNone(comment, 'Нет комментария')
        self.assertEqual(comment, self.comment)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        for post in range(MAX_PAGE_COUNT + 3):
            Post.objects.create(
                text='Тестовый текст поста',
                author=cls.user)

    def setUp(self):
        self.client = Client()

    def test_first_page_contains_expected_number_of_records(self):
        """Количество постов на первой странице index
        соотвествует ожидаемому.
        """
        self.assertEqual(
            len(self.client.get(INDEX_URL).context['page_obj']),
            MAX_PAGE_COUNT
        )

    def test_second_page_contains_three_records(self):
        """Количество постов на второй странице index
        соотвествует ожидаемому.
        """
        self.assertEqual(
            len(self.client.get(INDEX_URL + '?page=2').context['page_obj']), 3
        )
