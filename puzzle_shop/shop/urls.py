from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),           # Главная страница
    path('about/', views.about),     # Страница о магазине
    path('author/', views.author),   # Страница об авторе
]