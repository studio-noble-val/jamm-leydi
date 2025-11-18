"""
Vues publiques de la plateforme JAMM LEYDI.

Ce module gère les pages accessibles sans authentification.
"""
from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from referentiels.models import Commune
from suivi.models import CibleIndicateur, Indicateur, Intervention, ValeurIndicateur


def public_home(request: HttpRequest) -> HttpResponse:
    """
    Page d'accueil publique.

    Affiche les statistiques générales du projet.

    Args:
        request: Requête HTTP

    Returns:
        Page HTML d'accueil publique
    """

    # Statistiques publiques
    stats = {
        'total_activites': Intervention.objects.filter(statut='PUBLIE').count(),
        'total_beneficiaires_cible': 14700,  # Cible du projet
        'communes_couvertes': Commune.objects.count(),
    }

    # TODO: Implémenter le modèle Evenement pour les webstories
    derniers_evenements = []

    context = {
        'stats': stats,
        'derniers_evenements': derniers_evenements,
    }

    return render(request, 'public/home.html', context)


def carte_view(request: HttpRequest) -> HttpResponse:
    """
    Vue carte interactive publique.

    Affiche les interventions publiées sur une carte.

    Args:
        request: Requête HTTP

    Returns:
        Page HTML avec la carte interactive
    """

    # Interventions publiées avec géolocalisation
    activites = Intervention.objects.filter(
        statut='PUBLIE',
        geom__isnull=False
    ).select_related('commune', 'type_intervention')

    # Grouper par type pour la légende
    types_activites = {}
    for activite in activites:
        type_nom = activite.type_intervention.libelle
        if type_nom not in types_activites:
            types_activites[type_nom] = []
        types_activites[type_nom].append(activite)

    context = {
        'activites': activites,
        'types_activites': types_activites,
    }

    return render(request, 'public/carte.html', context)


def public_indicateurs(request: HttpRequest) -> HttpResponse:
    """
    Indicateurs publics avec pourcentages d'avancement.

    Args:
        request: Requête HTTP

    Returns:
        Page HTML listant les indicateurs publics
    """
    # Tous les indicateurs avec leurs valeurs
    indicateurs = Indicateur.objects.select_related('thematique').all()

    # Enrichir avec les valeurs actuelles
    for indicateur in indicateurs:
        derniere_valeur = ValeurIndicateur.objects.filter(
            indicateur=indicateur,
            statut='PUBLIE'
        ).order_by('-date_mesure').first()

        if derniere_valeur:
            # Récupérer la cible
            cible = CibleIndicateur.objects.filter(
                indicateur=indicateur,
                commune__isnull=True
            ).order_by('-annee').first()

            indicateur.valeur_actuelle = derniere_valeur.valeur_realisee
            indicateur.pourcentage = 0
            if cible and cible.valeur_cible > 0:
                indicateur.pourcentage = round((float(derniere_valeur.valeur_realisee) / float(cible.valeur_cible)) * 100, 1)
        else:
            indicateur.valeur_actuelle = 0
            indicateur.pourcentage = 0

    context = {
        'indicateurs': indicateurs,
    }

    return render(request, 'public/indicateurs.html', context)


def evenements_view(request: HttpRequest) -> HttpResponse:
    """
    Liste des événements et webstories.

    TODO: Implémenter le modèle Evenement.

    Args:
        request: Requête HTTP

    Returns:
        Page HTML listant les événements
    """

    # TODO: Implémenter le modèle Evenement pour les webstories
    evenements = []

    context = {
        'evenements': evenements,
    }

    return render(request, 'public/evenements.html', context)
