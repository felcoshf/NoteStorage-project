from django.shortcuts import render, get_object_or_404, redirect
from .models import Note
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from django.http import JsonResponse
from .forms import NoteEditForm
from django.urls import reverse

@login_required
def note_create(request):
    if request.method == "POST":
        form = NoteEditForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.save()
            return redirect("notes:list")
    else:
        form = NoteEditForm()

    return render(request, "notes/note-redact.html", {
        "form": form,
        "form_action": reverse("notes:create"),
        "page_title": "Создание заметки",
        "submit_label": "Создать",
        "initial_content": "",
        "initial_title": "",
    })

@login_required
def notes_list(request):
    category = request.GET.get('category', 'all')
    notes = Note.objects.filter(author=request.user, status=Note.Status.ACTIVE,)
    if category != 'all':
        notes = notes.filter(category=category)
    return render(request, 'notes/notes.html', {'notes': notes, 'categories': Note.Category.choices, 'current_category': category,})

@login_required
@require_POST
def move_note(request, pk):
    note = get_object_or_404(Note, pk=pk, author=request.user)
    data = json.loads(request.body)
    new_category = data.get('category')
    valid_categories = {category[0] for category in Note.Category.choices}
    if new_category not in valid_categories:
        return JsonResponse(
            {'ok': False, 'error': 'Invalid category'},
            status=400,
        )
    note.category = new_category
    note.save(update_fields=['category'])
    return JsonResponse({'ok': True, 'category': new_category})


@login_required
@require_POST
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk, author=request.user)
    note.to_recycle_bin()
    return redirect('notes:list')

@login_required
@require_POST
def restore_note(request, pk):
    note = get_object_or_404(Note, pk=pk, author=request.user,status=Note.Status.TRASH,)
    note.restore()
    return redirect('drafts:list')


@login_required
@require_POST
def delete_note_forever(request, pk):
    note = get_object_or_404(Note, pk=pk, author=request.user, status=Note.Status.TRASH,)
    note.delete()
    return redirect('drafts:list')

@login_required
def redact_note(request, pk):
    note = get_object_or_404(Note, pk=pk, author=request.user)

    if request.method == "POST":
        form = NoteEditForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect("notes:list")
    else:
        form = NoteEditForm(instance=note)

    return render(request, "notes/note-redact.html", {
        "form": form,
        "note": note,
        "form_action": reverse("notes:edit", args=[note.pk]),
        "page_title": "Редактирование заметки",
        "submit_label": "Сохранить",
        "initial_content": note.content or "",
        "initial_title": note.title or "",
    })