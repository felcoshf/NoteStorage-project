from django.test import TestCase

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class MainPageTests(TestCase):#тесты для views
    def test_first_page_is_available_without_login(self):#основная страница для неавторизованого пользователя
        response = self.client.get(reverse("main:first_page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index/home.html")

    def test_home_page_requires_login(self):#перенапровление пользователя на вход
        response = self.client.get(reverse("main:home_registrated"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_home_page_is_available_for_authenticated_user(self):#вход авторизованому пользователю на home
        user = User.objects.create_user(
            login="testuser",
            password="test-password",
            )
        self.client.force_login(user)
        response = self.client.get(reverse("main:home_registrated"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index/home-registrated.html")