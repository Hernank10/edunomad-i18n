from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('practica/', views.random_exercise, name='random_exercise'),
]
