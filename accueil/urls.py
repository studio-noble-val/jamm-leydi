"""
URLs pour l'application accueil
"""
from django.urls import path
from . import views, api_views

urlpatterns = [
    # Pages principales
    path('', views.landing_page, name='landing_page'),
    path('projets/', views.liste_projets, name='liste_projets'),
    path('projets/creer/', views.creer_projet, name='creer_projet'),
    path('projets/<int:projet_id>/selectionner/', views.selectionner_projet, name='selectionner_projet'),
    path('projets/<int:projet_id>/supprimer/', views.supprimer_projet, name='supprimer_projet'),

    # API pour sélection géographique en cascade
    path('api/geo/regions/', api_views.get_regions_by_pays, name='api_get_regions'),
    path('api/geo/departements/', api_views.get_departements_by_regions, name='api_get_departements'),
    path('api/geo/arrondissements/', api_views.get_arrondissements_by_departements, name='api_get_arrondissements'),
    path('api/geo/communes/', api_views.get_communes_by_arrondissements, name='api_get_communes'),
]
