from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.notes_list, name='list'),
    path('create/', views.note_create, name='create'),
    path('<int:pk>/move/', views.move_note, name='move'),
    path('<int:pk>/delete/', views.delete_note, name='delete'),
    path('<int:pk>/restore/', views.restore_note, name='restore'),
    path('<int:pk>/delete-forever/', views.delete_note_forever, name='delete_forever'),
    path('<int:pk>/edit/', views.redact_note, name='edit'),
]