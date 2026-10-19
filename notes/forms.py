import re
from django import forms
from .models import Note


class NoteEditForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "content"]
        labels = {
            "title": "Название",
            "content": "Текст заметки",
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "title-input",
                "placeholder": "Название заметки",
            }),
        }
        
    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise forms.ValidationError("Название не может быть пустым.")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"] or ""
        content = re.sub(r"<p>(&nbsp;|\s)*</p>", "", content)
        content = content.replace("&nbsp;", " ")
        content = content.replace("&#160;", " ")
        content = content.replace("\u00a0", " ")

        if not content.strip():
            raise forms.ValidationError("Текст заметки не может быть пустым.")
        return content
    
#редактирование заметки и проверка на то что она не пустая