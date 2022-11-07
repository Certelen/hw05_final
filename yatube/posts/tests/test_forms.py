from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User, Comment


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test',
            description='Тестовое описание',
        )
        cls.test_post = Post.objects.create(
            author=PostCreateFormTests.user,
            text='Длинный тестовый пост',
            group=None,
        )

    def setUp(self):
        self.guest_client = Client()
        self.group_id = PostCreateFormTests.group.pk
        self.post_id = PostCreateFormTests.test_post.pk
        self.post_data = PostCreateFormTests.test_post.created
        self.posts_count = Post.objects.count()

    def test_create_auth_post(self):
        """Проверка создания поста авторизированым"""

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Длинный тестовый пост',
            'group': self.group_id,
            'image': uploaded,
        }

        response = PostCreateFormTests.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': f'{PostCreateFormTests.user}'}
        ))
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateFormTests.user,
                text='Длинный тестовый пост',
                group=self.group_id,
                image__contains='gif',
            ).exists()
        )

    def test_create_guest_post(self):
        """Проверка создания поста неавторизированым"""

        posts_count = Post.objects.count()

        form_data = {
            'text': 'Длинный тестовый пост',
        }

        response = self.guest_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_author_post(self):
        """Проверка редактирования текста и группы поста автором"""

        form_data = {
            'text': 'Меняем текст и группу c None на тестовую',
            'group': self.group_id,
        }

        response = PostCreateFormTests.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post_id}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post_id}
        ))
        self.assertEqual(Post.objects.count(), self.posts_count)
        self.assertTrue(
            Post.objects.filter(
                pk=self.post_id,
                author=PostCreateFormTests.user,
                text='Меняем текст и группу c None на тестовую',
                group=self.group_id,
                created=self.post_data,
            ).exists()
        )

    def test_edit_not_author_post(self):
        """Проверка не редактирования поста не-автором"""

        user_reader = User.objects.create_user(username='Reader')
        authorized_client = Client()
        authorized_client.force_login(user_reader)

        form_data = {
            'text': 'Меняем текст',
        }

        user_tuple = (
            authorized_client.post,
            self.guest_client.post,
        )
        link_tuple = (
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post_id}
            ),
            '/auth/login/?next=/posts/1/edit/',
        )
        for n in range(len(user_tuple)):
            with self.subTest(number=n):

                response = user_tuple[n](
                    reverse('posts:post_edit', kwargs={
                        'post_id': self.post_id
                    }),
                    data=form_data,
                    follow=True
                )
                self.assertRedirects(response, link_tuple[n])
        self.assertTrue(
            Post.objects.filter(
                pk=self.post_id,
                author=PostCreateFormTests.user,
                text='Длинный тестовый пост',
                created=self.post_data,
                group=None,
            ).exists()
        )


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.test_post = Post.objects.create(
            author=CommentCreateFormTests.user,
            text='Длинный тестовый пост',
            group=None,
        )

    def setUp(self):
        self.guest_client = Client()
        self.post_id = CommentCreateFormTests.test_post.pk
        self.comments_count = Comment.objects.count()

    def test_create_auth_comment(self):
        """Проверка создания комментария авторизированым"""

        form_data = {
            'text': 'Комментарий',
        }

        response = CommentCreateFormTests.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post_id}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post_id}
        ))
        self.assertEqual(Comment.objects.count(), self.comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                author=CommentCreateFormTests.user,
                text='Комментарий',
            ).exists()
        )

    def test_create_guest_comment(self):
        """Проверка создания поста неавторизированым"""

        form_data = {
            'text': 'Комментарий',
        }

        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post_id}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')
        self.assertEqual(Comment.objects.count(), self.comments_count)
