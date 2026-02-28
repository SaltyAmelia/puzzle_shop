from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('about/', views.about),
    path('author/', views.author),
    path('products/', views.products_list),  # Новый маршрут!
]