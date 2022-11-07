from django.test import TestCase, Client

from http import HTTPStatus

from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.user_reader = User.objects.create_user(username='reader')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Длинный тестовый пост',
        )

    def setUp(self):
        self.post_id = PostURLTests.post.pk

    def test_urls_author_post(self):
        """Проверка доступности страниц авторизированым автором"""

        templates_url_names = {
            '': 'posts/index.html',
            '/follow/': 'posts/follow.html',
            f'/posts/{self.post_id}/': 'posts/post_detail.html',
            f'/profile/{PostURLTests.post.author}/': 'posts/profile.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            '/create/': 'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):

                response = PostURLTests.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_guest_post(self):
        """Проверка доступности страниц неавторизированым"""

        templates_url_names = {
            '': 'posts/index.html',
            f'/posts/{self.post_id}/': 'posts/post_detail.html',
            f'/profile/{PostURLTests.post.author}/': 'posts/profile.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):

                response = PostURLTests.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_author_create_post(self):
        """Проверка доступности редактирования своего поста автором"""
        templates_url_names = {
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            '/create/': 'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                PostURLTests.authorized_client.force_login(
                    PostURLTests.user
                )
                response = PostURLTests.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_reader_create_post(self):
        """Проверка недоступности редактирования чужого поста пользователем"""

        PostURLTests.authorized_client.force_login(
            PostURLTests.user_reader
        )
        response = PostURLTests.authorized_client.get(
            f'/posts/{self.post_id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_guest_create_post(self):
        """Проверка недоступности страниц гостем"""

        templates_url_names = [
            f'/posts/{self.post_id}/edit/',
            '/create/',
            '/follow/',
        ]

        for address in templates_url_names:
            with self.subTest(address=address):

                response = PostURLTests.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_404_post(self):
        """Проверка недоступности постов нужных аргументов в ссылке"""

        templates_url_names = [
            '/posts/<int:post_id>/',
            '/profile/<str:username>/',
            '/group/<slug:slug>/',
            '/posts/<int:post_id>/edit/',
        ]

        for address in templates_url_names:
            with self.subTest(address=address):

                response = PostURLTests.authorized_client.get(address)
                self.assertEqual(
                    response.status_code, HTTPStatus.NOT_FOUND
                )
