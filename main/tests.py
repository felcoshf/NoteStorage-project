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