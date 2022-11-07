from django.conf import settings
from django.test import TestCase

from ..models import Group, Post, User, Comment, Follow


class PostModelTest(TestCase):
    """Проверка модели Post"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Длинный тестовый пост',
        )

    def test_post_verbose_name(self):
        """Проверка наименования полей формы модели Post"""

        field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата публикации',
            'group': 'Группа',
            'author': 'Автор',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_post_help_text(self):
        """Проверка help_text полей формы модели Post"""

        field_help_texts = {
            'text': 'Содержимое поста',
            'group': 'Группа, к которой относится пост',
            'image': 'Загрузка картинки',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).help_text,
                    expected_value
                )

    def test_post_name_is_text_fild(self):
        """Проверка заголовка в названии вкладки"""

        expected_object_name = (
            PostModelTest.post.text[:settings.MAX_SYMBOLS_IN_TAB]
        )
        self.assertEqual(expected_object_name, str(PostModelTest.post))


class GroupModelTest(TestCase):
    """Проверка модели Group"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Длинный тестовый пост',
        )

    def test_group_verbose_name(self):
        """Проверка наименования полей формы модели Group"""

        field_verboses = {
            'title': 'Название',
            'slug': 'Ссылка',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    GroupModelTest.group._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_group_name_is_text_fild(self):
        """Проверка заголовка в названии вкладки"""
        expected_object_name = GroupModelTest.group.title
        self.assertEqual(expected_object_name, str(GroupModelTest.group))


class CommentModelTest(TestCase):
    """Проверка модели Comment"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Длинный тестовый пост',
        )
        cls.comm = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Комментарий',
        )

    def test_comment_verbose_name(self):
        """Проверка наименования полей формы модели Comment"""

        field_verboses = {
            'post': 'Пост',
            'created': 'Дата публикации',
            'text': 'Текст комментария',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    CommentModelTest.comm._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_comment_help_text(self):
        """Проверка help_text полей формы модели Comment"""

        field_help_texts = {
            'text': 'Содержимое комментария',
            'post': 'Пост, к которому относится комментарий',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    CommentModelTest.comm._meta.get_field(field).help_text,
                    expected_value
                )


class FollowModelTest(TestCase):
    """Проверка модели Follow"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='auth1')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.follow = Follow.objects.create(user=cls.user1, author=cls.user2)

    def test_follow_verbose_name(self):
        """Проверка наименования полей формы модели Follow"""

        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    FollowModelTest.follow._meta.get_field(field).verbose_name,
                    expected_value
                )
