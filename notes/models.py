from django.db import models
from django.conf import settings
from django.utils import timezone

class Note(models.Model):
    class Category(models.TextChoices):
        PERSONAL = 'personal', 'Личное'
        WORK = 'work', 'Работа'
        STUDY = 'study', 'Учёба'
        OTHER = 'other', 'Другое'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активная'
        TRASH = 'trash', 'В корзине'

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes', verbose_name='Автор')
    title = models.CharField(max_length=200, verbose_name='Название')
    content = models.TextField(blank=True, verbose_name='Содержимое')
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER, verbose_name='Категория')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE, verbose_name='Статус')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменено')
    
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Удалено')

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'
        indexes = [
            models.Index(fields=['author', 'status']),
            models.Index(fields=['author', 'category']),
        ]

    def __str__(self):
        return self.title

    def to_recycle_bin(self):
        self.status = self.Status.TRASH
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def restore(self):
        self.status = self.Status.ACTIVE
        self.deleted_at = None
        self.save(update_fields=['status', 'deleted_at'])
        
#сортировка заметок по группам