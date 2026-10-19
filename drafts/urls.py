from django.urls import path
from . import views

app_name = 'drafts'

urlpatterns = [
    path('', views.drafts_page, name='list'),
]

#когда открывается адрес приложения вызывается drafts_page