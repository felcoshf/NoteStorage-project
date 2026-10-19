from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.unathorize_page, name='first_page'),
]
#задает url адресс 