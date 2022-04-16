from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
import tempfile

from ..models import Post, Group, User


AUTHOR = 'user_test'
POST_TEXT = 'Тестовый тест'
GROUP_TITLE = 'Тестовый заголовок'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Описание тестовой группы'
NEW_URL = reverse('posts:post_create')
LOGIN_URL = f'{reverse("login")}?next='
REDIRECT_ADDRESS = reverse('users:login')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR])
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED_GIF = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)
NEW_UPLOADED_GIF = SimpleUploadedFile(
    name='new_small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.new_group = Group.objects.create(
            title='Заголовок_новый',
            slug='test_slug_new',
            description='текстовое поле'
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=NEW_UPLOADED_GIF
        )
        cls.EDIT_URL = reverse('posts:post_edit',
                               kwargs={'post_id': cls.post.id})
        cls.POST_URL = reverse('posts:post_detail',
                               kwargs={'post_id': cls.post.id})
        cls.COMMENT_URL = reverse('posts:add_comment',
                                  kwargs={'post_id': cls.post.id})
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.unauthor = Client()

    def test_creat_new_post(self):
        """Валидная форма создает запись в Post."""
        posts = set(Post.objects.all())
        form_data = {
            'text': 'test_text',
            'group': self.group.id,
            'image': UPLOADED_GIF
        }
        response_post = self.author.post(
            NEW_URL,
            data=form_data,
            follow=True
        )
        posts = set(Post.objects.all()) - posts
        self.assertRedirects(response_post, PROFILE_URL)
        self.assertEqual(len(posts), 1)
        post = posts.pop()
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(
            post.image.name, 'posts/' + form_data['image'].name)

    def test_change_post(self):
        """Валидная форма создает запись в Post."""
        new_group = Group.objects.create()
        form_data = {
            'text': 'new_text',
            'group': new_group.id,
        }
        response = self.author.post(
            self.EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_URL)
        post = response.context['post']
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)

    def test_anonymous_can_not_create_post(self):
        """Аноним не может создавать посты."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Пост, который не создастся',
        }
        response = self.unauthor.post(
            NEW_URL,
            data=form_data,
            follow=True
        )
        self.assertFalse(
            Post.objects.filter(
                text=form_data['text']
            ).exists()
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count
        )
        self.assertRedirects(response, LOGIN_URL + NEW_URL)

    def test_form_add_comment(self):
        """Авторизированный пользователь может
        комментировать посты."""
        form_data = {
            'text': 'Добавленный тестовый коммент'
        }
        response = self.author.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_URL)
        comment = response.context['comments'].first()
        self.assertEqual(
            comment.text, form_data['text'])
        self.assertEqual(
            comment.author,
            self.user)

    def test_unauthorized_client_create_comment(self):
        """Аноним не может комментировать посты."""
        form_data = {
            'text': 'Добавленный тестовый коммент',
        }
        response = self.unauthor.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, f'{REDIRECT_ADDRESS}?next={self.COMMENT_URL}')
