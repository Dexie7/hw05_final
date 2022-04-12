from django.test import TestCase

from ..models import Group, Post, User


AUTHOR = 'user_test'
POST_TEXT = 'Тестовый тест'
GROUP_TITLE = 'Тестовый заголовок'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Описание тестовой группы'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)

        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(str(self.group), self.group.title)
        self.assertEqual(str(self.post), self.post.text[:15])

    def test_verbose_name(self):
        self.assertEquals(Post._meta.get_field("text").verbose_name,
                          "Текст поста")
        self.assertEquals(Post._meta.get_field("group").verbose_name, "Группа")

    def test_text_help_text(self):
        self.assertEquals(Post._meta.get_field("text").help_text,
                          "Введите текст поста")
        self.assertEquals(Post._meta.get_field("group").help_text,
                          "Группа, к которой будет относиться пост")
