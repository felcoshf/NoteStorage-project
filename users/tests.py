from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class CustomUserManagerTests(TestCase):#тесты для models
    def test_create_user(self):
        user = User.objects.create_user(
            login="alice",
            password="test-password",
        )

        self.assertEqual(user.login, "alice")
        self.assertTrue(user.check_password("test-password"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_login_raises_value_error(self):
        with self.assertRaisesMessage(ValueError, "The login field must be set"):
            User.objects.create_user(login="", password="test-password")

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            login="admin",
            password="test-password",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("test-password"))

    def test_create_superuser_with_is_staff_false_raises_value_error(self):
        with self.assertRaisesMessage(
            ValueError,
            "Superuser must have is_staff=True.",
        ):
            User.objects.create_superuser(
                login="admin",
                password="test-password",
                is_staff=False,
            )

    def test_create_superuser_with_is_superuser_false_raises_value_error(self):
        with self.assertRaisesMessage(
            ValueError,
            "Superuser must have is_superuser=True.",
        ):
            User.objects.create_superuser(
                login="admin",
                password="test-password",
                is_superuser=False,
            )


class CustomUserModelTests(TestCase):
    def test_str_returns_login(self):
        user = User(login="alice")
        self.assertEqual(str(user), "alice")
        
        

