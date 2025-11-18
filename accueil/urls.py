"""
URLs pour l'application accueil
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('projets/', views.liste_projets, name='liste_projets'),
    path('projets/creer/', views.creer_projet, name='creer_projet'),
    path('projets/<int:projet_id>/selectionner/', views.selectionner_projet, name='selectionner_projet'),
    path('projets/<int:projet_id>/supprimer/', views.supprimer_projet, name='supprimer_projet'),
]
