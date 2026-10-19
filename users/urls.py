from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('authorization/', views.login_view, name='authorization'),
]