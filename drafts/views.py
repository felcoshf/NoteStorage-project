from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from notes.models import Note

@login_required
def drafts_page(request):
    notes = Note.objects.filter(
        author=request.user,
        status=Note.Status.TRASH,
    ).order_by('-deleted_at')
    return render(request, 'drafts/drafts.html', {'notes': notes})


#проверяет на вход и уже по этому сортирует его заметки и показывает их