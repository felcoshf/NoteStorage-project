import json
from django.test import TestCase
from .forms import NoteEditForm
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Note
from django.urls import reverse


#python manage.py test-запуск тестов
class NoteEditFormTests(TestCase):# тест к forms
    def test_valid_data(self):
        form = NoteEditForm(data={
            "title": "Моя заметка",
            "content": "<p>Текст заметки</p>",
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["title"], "Моя заметка")

    def test_title_is_trimmed(self):
        form = NoteEditForm(data={
            "title": "  Моя заметка  ",
            "content": "Текст",
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["title"], "Моя заметка")

    def test_empty_title_is_invalid(self):
        form = NoteEditForm(data={
            "title": "   ",
            "content": "Текст",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_empty_content_is_invalid(self):
        form = NoteEditForm(data={
            "title": "Моя заметка",
            "content": "<p>&nbsp;</p>",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_content_entities_are_replaced(self):
        form = NoteEditForm(data={
            "title": "Моя заметка",
            "content": "Первый&nbsp;текст&#160;и\u00a0ещё",
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data["content"],
            "Первый текст и ещё",
        )




User = get_user_model()# тесты для models


class NoteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            login="testuser",
            password="test-password",
        )

        self.note = Note.objects.create(
            author=self.user,
            title="Тестовая заметка",
            content="Текст заметки",
        )

    def test_default_values(self):
        self.assertEqual(self.note.category, Note.Category.OTHER)
        self.assertEqual(self.note.status, Note.Status.ACTIVE)
        self.assertIsNone(self.note.deleted_at)

    def test_str_returns_title(self):
        self.assertEqual(str(self.note), "Тестовая заметка")

    def test_note_is_related_to_author(self):
        self.assertEqual(self.note.author, self.user)
        self.assertIn(self.note, self.user.notes.all())

    def test_to_recycle_bin(self):
        self.note.to_recycle_bin()
        self.assertEqual(self.note.status, Note.Status.TRASH)
        self.assertIsNotNone(self.note.deleted_at)
        self.note.refresh_from_db()
        self.assertEqual(self.note.status, Note.Status.TRASH)
        self.assertIsNotNone(self.note.deleted_at)

    def test_restore(self):
        self.note.to_recycle_bin()
        self.note.restore()
        self.assertEqual(self.note.status, Note.Status.ACTIVE)
        self.assertIsNone(self.note.deleted_at)
        self.note.refresh_from_db()
        self.assertEqual(self.note.status, Note.Status.ACTIVE)
        self.assertIsNone(self.note.deleted_at)

    def test_restore_clears_deleted_at(self):
        old_deleted_at = timezone.now() - timedelta(days=1)
        self.note.status = Note.Status.TRASH
        self.note.deleted_at = old_deleted_at
        self.note.save()
        self.note.restore()
        self.assertEqual(self.note.status, Note.Status.ACTIVE)
        self.assertIsNone(self.note.deleted_at)
        
class NoteViewsTests(TestCase):#тесты для views
    def setUp(self):
        self.user = User.objects.create_user(
            login="testuser",
            password="test-password",
        )       
        self.other_user = User.objects.create_user(
            login="otheruser",
            password="test-password",
        )

        self.note = Note.objects.create(
            author=self.user,
            title="Моя заметка",
            content="Текст заметки",
            category=Note.Category.PERSONAL,
        )

    def test_notes_list_requires_login(self):
        response = self.client.get(reverse("notes:list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_notes_list_shows_only_active_notes_of_current_user(self):
        other_note = Note.objects.create(
            author=self.other_user,
            title="Чужая заметка",
            content="Не должна отображаться",
        )
        trashed_note = Note.objects.create(
            author=self.user,
            title="Заметка в корзине",
            content="Не должна отображаться",
            status=Note.Status.TRASH,
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("notes:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.note.title)
        self.assertNotContains(response, other_note.title)
        self.assertNotContains(response, trashed_note.title)

    def test_notes_list_filters_by_category(self):
        work_note = Note.objects.create(
            author=self.user,
            title="Рабочая заметка",
            content="Работа",
            category=Note.Category.WORK,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("notes:list"),
            {"category": Note.Category.WORK},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, work_note.title)
        self.assertNotContains(response, self.note.title)
        self.assertEqual(
            response.context["current_category"],
            Note.Category.WORK,
        )

    def test_create_note_get_displays_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("notes:create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note-redact.html")
        self.assertEqual(response.context["page_title"], "Создание заметки")

    
    def test_create_note_post_invalid_data_shows_errors(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notes:create"),
            {
                "title": "   ",
                "content": "Текст",
                "category": Note.Category.PERSONAL,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(Note.objects.filter(title="   ").exists())

    def test_move_note_changes_category(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notes:move", args=[self.note.pk]),
            data=json.dumps({"category": Note.Category.WORK}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"ok": True, "category": Note.Category.WORK},
        )

        self.note.refresh_from_db()
        self.assertEqual(self.note.category, Note.Category.WORK)

    def test_move_note_rejects_invalid_category(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notes:move", args=[self.note.pk]),
            data=json.dumps({"category": "invalid"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"ok": False, "error": "Invalid category"},
        )

    def test_move_note_does_not_allow_changing_another_users_note(self):
        other_note = Note.objects.create(
            author=self.other_user,
            title="Чужая заметка",
            content="Текст",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notes:move", args=[other_note.pk]),
            data=json.dumps({"category": Note.Category.WORK}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    def test_move_note_requires_post(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("notes:move", args=[self.note.pk])
        )

        self.assertEqual(response.status_code, 405)

    def test_delete_note_moves_note_to_trash(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notes:delete", args=[self.note.pk])
        )

        self.assertRedirects(response, reverse("notes:list"))

        self.note.refresh_from_db()
        self.assertEqual(self.note.status, Note.Status.TRASH)
        self.assertIsNotNone(self.note.deleted_at)

    def test_delete_note_requires_post(self):
        """Удалить заметку GET-запросом нельзя."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("notes:delete", args=[self.note.pk])
        )

        self.assertEqual(response.status_code, 405)

    def test_delete_note_does_not_allow_deleting_another_users_note(self):
        other_note = Note.objects.create(
            author=self.other_user,
            title="Чужая заметка",
            content="Текст",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notes:delete", args=[other_note.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_restore_note_restores_trashed_note(self):
        self.note.to_recycle_bin()
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notes:restore", args=[self.note.pk])
        )

        self.note.refresh_from_db()
        self.assertEqual(self.note.status, Note.Status.ACTIVE)
        self.assertIsNone(self.note.deleted_at)
        self.assertEqual(response.status_code, 302)

    def test_restore_note_requires_post(self):
        self.note.to_recycle_bin()
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("notes:restore", args=[self.note.pk])
        )

        self.assertEqual(response.status_code, 405)

    def test_restore_active_note_returns_404(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notes:restore", args=[self.note.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_note_forever_removes_trashed_note(self):
        self.note.to_recycle_bin()
        note_pk = self.note.pk
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notes:delete_forever", args=[note_pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=note_pk).exists())

    def test_delete_note_forever_requires_post(self):
        self.note.to_recycle_bin()
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("notes:delete_forever", args=[self.note.pk])
        )

        self.assertEqual(response.status_code, 405)

    def test_edit_note_get_displays_existing_data(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("notes:edit", args=[self.note.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note-redact.html")
        self.assertEqual(response.context["note"], self.note)
        self.assertEqual(response.context["initial_title"], self.note.title)
        self.assertEqual(
            response.context["initial_content"],
            self.note.content,
        )


    def test_edit_note_does_not_allow_editing_another_users_note(self):
        other_note = Note.objects.create(
            author=self.other_user,
            title="Чужая заметка",
            content="Текст",
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("notes:edit", args=[other_note.pk])
        )

        self.assertEqual(response.status_code, 404)
            
            
            
