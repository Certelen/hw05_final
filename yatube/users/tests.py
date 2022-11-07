from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus

User = get_user_model()


class UsersTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()

    def test_urls_users(self):
        """Проверка шаблона по адресу"""

        templates_url_names = [
            {'/auth/signup/': 'users/signup.html'},
            {'/auth/logout/': 'users/logged_out.html'},
            {'/auth/login/': 'users/login.html'},
            {'/auth/password_reset/':
                'users/password_reset_form.html'},
            {'/auth/password_reset/done/':
                'users/password_reset_done.html'},
            {'/auth/reset/done/':
                'users/password_reset_complete.html'},
            {'/auth/password_change/':
                'users/password_change_form.html'},
            {'/auth/password_change/done/':
                'users/password_change_done.html'},
            {'/auth/password_change/': 1},
            {'/auth/password_change/done/': 1},
        ]

        for dict in templates_url_names:
            with self.subTest(dict=dict):

                for address, template in dict.items():

                    if template == 1:

                        response = self.guest_client.get(address)
                        self.assertEqual(
                            response.status_code, HTTPStatus.FOUND
                        )

                    else:
                        self.authorized_client.force_login(self.user)
                        response = self.authorized_client.get(address)
                        self.assertTemplateUsed(response, template)

    def test_templates_users(self):
        """Проверка шаблона по namespace:name"""

        templates_url_names = [
            {reverse('users:signup'): 'users/signup.html'},
            {reverse('users:logout'): 'users/logged_out.html'},
            {reverse('users:login'): 'users/login.html'},
            {reverse('users:password_reset_form'):
                'users/password_reset_form.html'},
            {reverse('users:password_reset_done'):
                'users/password_reset_done.html'},
            {reverse('users:password_reset_complete'):
                'users/password_reset_complete.html'},
            {reverse('users:password_change_form'):
                'users/password_change_form.html'},
            {reverse('users:password_change_done'):
                'users/password_change_done.html'},
        ]

        for dict in templates_url_names:
            with self.subTest(dict=dict):

                for address, template in dict.items():

                    self.authorized_client.force_login(self.user)
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)

    def test_signup_page_form(self):
        """Проверка правильности полей в форме"""

        response = self.authorized_client.get(reverse(
            'users:signup'
        ))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_user(self):
        """Проверка создания нового пользователя"""

        user_count = User.objects.count()

        form_data = {
            'first_name': 'test_first_name',
            'last_name': 'test_second_name',
            'username': 'test_username',
            'email': 'test_mail@mail.ru',
            'password1': 'Testtest12345',
            'password2': 'Testtest12345',
        }

        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:index'
        ))
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='test_first_name',
                last_name='test_second_name',
                username='test_username',
                email='test_mail@mail.ru',
            ).exists()
        )
