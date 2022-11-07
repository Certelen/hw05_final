from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus


class AboutTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_about(self):
        """Проверка шаблона по адресу"""

        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):

                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_templates_about(self):
        """Проверка шаблона по namespace:name"""

        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):

                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
