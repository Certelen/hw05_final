from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User, Comment, Follow


class PaginatorTests(TestCase):
    """Проверка паджинатора"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_1 = User.objects.create_user(username='auth_1')
        cls.user_2 = User.objects.create_user(username='auth_2')
        cls.LEN_POSTS = 13

        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='Test_1',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='Test_2',
            description='Тестовое описание',
        )

        for n in range(0, PaginatorTests.LEN_POSTS):
            cls.posts = []
            cls.posts.append(Post.objects.create(
                author=cls.user_1,
                text='Длинный тестовый пост первой группы и пользователя',
                group=cls.group_1,
            ))
            cls.posts.append(Post.objects.create(
                author=cls.user_2,
                text='Длинный тестовый пост второй группы и пользователя',
                group=cls.group_2,
            ))

    def setUp(self):
        self.MAX_POSTS_ON_PAGE = settings.MAX_COUNT_POST
        self.guest_client = Client()
        self.page_2 = '?page=2'
        self.page_3 = '?page=3'

    def test_index_paginator(self):
        """Проверка количества постов на страницу index"""
        response_1_page = self.guest_client.get(
            reverse('posts:index')
        )
        response_2_page = self.guest_client.get(
            reverse('posts:index') + f'{self.page_2}'
        )
        response_3_page = self.guest_client.get(
            reverse('posts:index') + f'{self.page_3}'
        )
        self.assertEqual(
            len(response_1_page.context['page_obj']),
            settings.MAX_COUNT_POST
        )
        self.assertEqual(
            len(response_2_page.context['page_obj']),
            settings.MAX_COUNT_POST
        )
        self.assertEqual(
            len(response_3_page.context['page_obj']),
            (
                (PaginatorTests.LEN_POSTS + PaginatorTests.LEN_POSTS)
                % settings.MAX_COUNT_POST
            )
        )

    def test_group_page_paginator(self):
        """Проверка количества постов на странице группы"""

        group_link_tuple = (
            PaginatorTests.group_1.slug,
            PaginatorTests.group_2.slug,
        )

        for group_link in group_link_tuple:
            with self.subTest(group_link=group_link):
                response_1_page_group = self.guest_client.get(reverse(
                    'posts:group',
                    kwargs={'slug': f'{group_link}'}
                ))
                response_2_page_group = self.guest_client.get(reverse(
                    'posts:group',
                    kwargs={'slug': f'{group_link}'}) + f'{self.page_2}'
                )

                self.assertEqual(
                    len(response_1_page_group.context['page_obj']),
                    settings.MAX_COUNT_POST
                )
                self.assertEqual(
                    len(response_2_page_group.context['page_obj']),
                    PaginatorTests.LEN_POSTS % settings.MAX_COUNT_POST
                )

    def test_profile_page_paginator(self):
        """Проверка количества постов на странице профиля"""

        user_link_tuple = (
            PaginatorTests.user_1,
            PaginatorTests.user_2,
        )

        for user_link in user_link_tuple:
            with self.subTest(group_link=user_link):
                response_1_page_profile = self.guest_client.get(reverse(
                    'posts:profile',
                    kwargs={'username': f'{user_link}'}
                ))
                response_2_page_profile = self.guest_client.get(reverse(
                    'posts:profile',
                    kwargs={'username': f'{user_link}'}) + f'{self.page_2}'
                )

                self.assertEqual(
                    len(response_1_page_profile.context['page_obj']),
                    settings.MAX_COUNT_POST
                )
                self.assertEqual(
                    len(response_2_page_profile.context['page_obj']),
                    PaginatorTests.LEN_POSTS % settings.MAX_COUNT_POST
                )


class PostViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='auth1')
        cls.user_2 = User.objects.create_user(username='auth2')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_1)
        cls.LEN_POSTS = 13

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small_1.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='Test_1',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='Test_2',
            description='Тестовое описание',
        )

        for n in range(0, PostViewsTests.LEN_POSTS):
            Post.objects.create(
                author=cls.user_1,
                text='Пост для проверки паджинатора 1',
                group=cls.group_1,
            )
            Post.objects.create(
                author=cls.user_2,
                text='Пост для проверки паджинатора 2',
                group=cls.group_2,
            )
        cls.post_1 = (Post.objects.create(
            author=cls.user_1,
            text='Длинный тестовый пост первой группы и пользователя',
            group=cls.group_1,
            image=cls.uploaded,
        ))
        cls.post_2 = (Post.objects.create(
            author=cls.user_2,
            text='Длинный тестовый пост второй группы и пользователя',
            group=cls.group_2,
        ))

    def setUp(self):
        self.guest_client = Client()
        self.post_id = PostViewsTests.post_1.pk
        self.username = PostViewsTests.post_1.author
        self.slug = PostViewsTests.group_1.slug

    def test_views_post(self):
        """Проверка соответствия шаблона с namespace"""

        templates_url_names = [
            {'posts/index.html': reverse('posts:index')},
            {'posts/follow.html': reverse('posts:follow_index')},
            {'core/404.html': '404'},
            {'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': f'{self.username}'}
            )},
            {'posts/group_list.html': reverse(
                'posts:group', kwargs={'slug': f'{self.slug}'}
            )},
            {'posts/create_post.html': reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post_id}'}
            )},
            {'posts/create_post.html': reverse('posts:create')},
        ]

        for dict in templates_url_names:
            with self.subTest(dict=dict):
                for template, reverse_name in dict.items():

                    response = PostViewsTests.authorized_client.get(
                        reverse_name
                    )
                    self.assertTemplateUsed(response, template)

    def test_index_page(self):
        """Проверка соответствия передаваемых постов в index"""

        posts = Post.objects.all()[:settings.MAX_COUNT_POST]

        response = self.authorized_client.get(
            reverse('posts:index')
        )
        posts_object = response.context.get('page_obj')

        for number_post in range(len(posts)):
            with self.subTest(number_post=number_post):
                if posts[number_post].author == PostViewsTests.user_1:
                    self.assertTrue(
                        Post.objects.filter(
                            group=PostViewsTests.group_1,
                            image='posts/small_1.gif',
                        ).exists()
                    )

                self.assertIn(posts[number_post], posts_object)

    def test_follow_index_page(self):
        """Проверка соответствия передаваемых постов в follow_index"""

        Follow.objects.create(
            user=PostViewsTests.user_1,
            author=PostViewsTests.user_2
        )

        posts = Post.objects.filter(
            author=PostViewsTests.user_2
        )[:settings.MAX_COUNT_POST]

        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        posts_object = response.context.get('page_obj')

        for number_post in range(len(posts)):
            with self.subTest(number_post=number_post):
                self.assertIn(posts[number_post], posts_object)

    def test_follow(self):
        """Проверка подписки"""

        self.assertFalse(Follow.objects.filter(user=PostViewsTests.user_1))

        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={
                'username': PostViewsTests.user_2
            }))

        self.assertTrue(Follow.objects.filter(user=PostViewsTests.user_1))

    def test_unfollow(self):
        """Проверка отписки"""

        Follow.objects.create(
            user=PostViewsTests.user_1,
            author=PostViewsTests.user_2
        )

        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={
                'username': PostViewsTests.user_2
            }))

        self.assertFalse(Follow.objects.filter(user=PostViewsTests.user_1))

    def test_group_page(self):
        """
        Проверка соответствия передаваемых постов в group и
        проверка соответствия групп и их полей
        """

        group = PostViewsTests.group_1
        groups_posts = Post.objects.filter(
            group=group)[:settings.MAX_COUNT_POST]

        response = self.authorized_client.get(reverse(
            'posts:group', kwargs={'slug': f'{group.slug}'}
        ))
        group_posts_object = response.context.get('page_obj')

        for number_post in range(len(groups_posts)):
            with self.subTest(number_post=number_post):
                if groups_posts[number_post].author == PostViewsTests.user_1:
                    self.assertTrue(
                        Post.objects.filter(
                            group=PostViewsTests.group_1,
                            image='posts/small_1.gif',
                        ).exists()
                    )

                self.assertIn(groups_posts[number_post], group_posts_object)

        group_object = response.context['group']
        group_title = group_object.title
        group_description = group_object.description
        group_slug = group_object.slug
        self.assertEqual(group_title, group.title)
        self.assertEqual(group_description, group.description)
        self.assertEqual(group_slug, group.slug)

    def test_profile_page(self):
        """Проверка соответствия передаваемых постов и author в profile"""

        expected_author = PostViewsTests.user_1
        author_posts = Post.objects.filter(
            author=expected_author)[:settings.MAX_COUNT_POST]
        test_post = Post.objects.get(pk=1)
        test_author = test_post.author

        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': f'{test_author}'}
        ))
        group_posts_object = response.context.get('page_obj')

        for number_post in range(len(author_posts)):
            with self.subTest(number_post=number_post):
                if author_posts[number_post].author == PostViewsTests.user_1:
                    self.assertTrue(
                        Post.objects.filter(
                            group=PostViewsTests.group_1,
                            image='posts/small_1.gif',
                        ).exists()
                    )

                self.assertIn(author_posts[number_post], group_posts_object)

        author = response.context['author']
        self.assertEqual(author, expected_author)

    def test_post_detail_page(self):
        """Проверка соответствия передаваемого поста в post_detail"""

        Comment.objects.create(
            post=Post.objects.get(pk=self.post_id),
            author=PostViewsTests.user_1,
            text='Комментарий',
        )

        exepted_post = Post.objects.get(pk=self.post_id)
        exepted_comment = Comment.objects.filter(post=exepted_post)

        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': f'{self.post_id}'}
        ))

        post_object = response.context.get('post')
        comments_object = response.context.get('comments')
        if exepted_post.author == PostViewsTests.user_1:
            self.assertTrue(
                Post.objects.filter(
                    group=PostViewsTests.group_1,
                    image='posts/small_1.gif',
                ).exists()
            )
        for number_comment in range(len(exepted_comment)):
            with self.subTest(number_comment=number_comment):
                self.assertIn(comments_object[number_comment], exepted_comment)
        self.assertEqual(exepted_post, post_object)

    def test_edit_page(self):
        """
        Проверка соответствия передаваемых полей формы и
        IS_EDIT в post_edit
        """

        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.post_id}'}
        ))
        value_is_edit = response.context.get('IS_EDIT')
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertTrue(value_is_edit)

    def test_create_page(self):
        """Проверка соответствия передаваемых полей формы в post_create и
        IS_EDIT в post_edit
        """

        response = self.authorized_client.get(reverse(
            'posts:create'
        ))
        value_is_edit = response.context.get('IS_EDIT')
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertFalse(value_is_edit)


class ShowPostAfterCreate(TestCase):
    """Проверка отображения поста после создания"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_1 = User.objects.create_user(username='auth1')
        cls.user_2 = User.objects.create_user(username='auth2')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_1)
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='Test_1',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='Test_2',
            description='Тестовое описание',
        )
        cls.test_post = Post.objects.create(
            author=ShowPostAfterCreate.user_1,
            text='Проверка отображения',
            group=ShowPostAfterCreate.group_1,
        )

    def test_show_post_in_index_after_create(self):
        """Проверка отображения поста в index после создания"""

        response = self.authorized_client.get(reverse('posts:index'))
        posts_object = response.context['page_obj'][0]
        self.assertEqual(posts_object, ShowPostAfterCreate.test_post)

    def test_show_post_in_group_after_create(self):
        """
        Проверка отображения поста в group_1 после создания
        """

        response = self.authorized_client.get(reverse(
            'posts:group', kwargs={'slug': ShowPostAfterCreate.group_1.slug}
        ))
        posts_object = response.context['page_obj']

        self.assertIn(
            ShowPostAfterCreate.test_post, posts_object
        )

    def test_show_post_in_group_after_create(self):
        """
        Проверка того, что поста нет в group_2
        """

        response = self.authorized_client.get(reverse(
            'posts:group', kwargs={'slug': ShowPostAfterCreate.group_2.slug}
        ))
        posts_object = response.context['page_obj']

        self.assertNotIn(
            ShowPostAfterCreate.test_post, posts_object
        )

    def test_show_post_in_profile_1_after_create(self):
        """
        Проверка отображения поста в профиле user_1 после создания
        """

        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': ShowPostAfterCreate.user_1}
        ))
        posts_object = response.context['page_obj']

        self.assertIn(
            ShowPostAfterCreate.test_post, posts_object
        )

    def test_show_post_in_profile_2_after_create(self):
        """
        Проверка того, что поста нет в профиле user__2
        """

        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': ShowPostAfterCreate.user_2}
        ))
        posts_object = response.context['page_obj']

        self.assertNotIn(
            ShowPostAfterCreate.test_post, posts_object
        )

    def test_show_post_in_index_after_create_and_delete(self):
        """Проверка кэширования поста - до удаления и после"""

        test_post2 = Post.objects.create(
            author=ShowPostAfterCreate.user_1,
            text='Проверка кэширования',
            group=ShowPostAfterCreate.group_1,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        posts_object = response.context['page_obj'][0]
        self.assertEqual(test_post2, posts_object)
        test_post2.delete()
        after_del_response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response.content, after_del_response.content
        )
        cache.clear()
        update_response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(
            after_del_response.content, update_response.content
        )
