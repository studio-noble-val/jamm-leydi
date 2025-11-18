from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('indicateurs/', views.indicateurs_view, name='indicateurs'),
    path('activites/', views.activites_view, name='activites'),

    # Thématiques
    path('thematique/<int:thematique_id>/', views.thematique_detail_view, name='thematique_detail'),

    # Interventions
    path('interventions/', views.liste_interventions_view, name='liste_interventions'),
    path('interventions/creer/', views.creer_intervention_view, name='creer_intervention'),
    path('interventions/<int:intervention_id>/changer-statut/', views.changer_statut_intervention_view, name='changer_statut_intervention'),

    # Cartographie SIG
    path('carte/', views.carte_sig_view, name='carte_sig'),

    # API GeoJSON pour MapLibre
    path('api/geojson/communes/', views.api_communes_geojson, name='api_communes_geojson'),
    path('api/geojson/interventions/', views.api_interventions_geojson, name='api_interventions_geojson'),
    path('api/geojson/infrastructures/', views.api_infrastructures_geojson, name='api_infrastructures_geojson'),
    path('api/geojson/acteurs/', views.api_acteurs_geojson, name='api_acteurs_geojson'),

    # Configuration du projet (wizard en 3 étapes)
    path('configuration/thematiques/', views.creer_thematiques_view, name='creer_thematiques'),
    path('configuration/indicateurs/', views.configurer_indicateurs_view, name='configurer_indicateurs'),
    path('configuration/parametres/', views.configurer_parametres_view, name='configurer_parametres'),

    # Menu de configuration
    path('configuration/', views.menu_configuration_view, name='menu_configuration'),

    path('logout/', views.logout_view, name='dashboard_logout'),
]