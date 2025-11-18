from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_home, name='public_home'),
    path('carte/', views.carte_view, name='carte'),
    path('indicateurs/', views.public_indicateurs, name='public_indicateurs'),
    path('evenements/', views.evenements_view, name='evenements'),
]