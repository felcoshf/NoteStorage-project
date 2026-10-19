from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note


User = get_user_model()


class DraftsPageTests(TestCase):#тесты для views
    def setUp(self):
        self.user = User.objects.create_user(
            login="testuser",
            password="test-password",
        )
        self.other_user = User.objects.create_user(
            login="otheruser",
            password="test-password",
        )

    def test_drafts_page_requires_login(self):#проверка того что неавторизованого пользователя кинуло на страницу входа
        response = self.client.get(reverse("drafts:list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_shows_only_current_users_trashed_notes(self):#проверка заметок: активная, в корзине, заметка другого пользователя в корзине
        trashed_note = Note.objects.create(
            author=self.user,
            title="Моя заметка в корзине",
            status=Note.Status.TRASH,
        )
        active_note = Note.objects.create(
            author=self.user,
            title="Моя активная заметка",
            status=Note.Status.ACTIVE,
        )
        other_users_note = Note.objects.create(
            author=self.other_user,
            title="Чужая заметка в корзине",
            status=Note.Status.TRASH,
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("drafts:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "drafts/drafts.html")
        self.assertContains(response, "Моя заметка в")
        self.assertNotContains(response, active_note.title)
        self.assertNotContains(response, other_users_note.title)
        notes = list(response.context["notes"])
        self.assertEqual(notes, [trashed_note])

    def test_orders_notes_by_deleted_at_descending(self):#проверка дат в удаленых заметках
        older_note = Note.objects.create(
            author=self.user,
            title="Удалена раньше",
            status=Note.Status.TRASH,
        )
        newer_note = Note.objects.create(
            author=self.user,
            title="Удалена позже",
            status=Note.Status.TRASH,
        )

        Note.objects.filter(pk=older_note.pk).update(
            deleted_at="2025-01-01T12:00:00Z"
        )
        Note.objects.filter(pk=newer_note.pk).update(
            deleted_at="2025-01-02T12:00:00Z"
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("drafts:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["notes"]),
            [newer_note, older_note],
        )

    def test_empty_trash_returns_empty_queryset(self):#проверка корзины
        self.client.force_login(self.user)
        response = self.client.get(reverse("drafts:list"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["notes"], [])
