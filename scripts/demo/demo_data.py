#!/usr/bin/env python
"""
Script pour créer des données de démonstration pour JAMM LEYDI - Architecture V2
Crée : Interventions, ValeurIndicateur, Infrastructures, Acteurs, SecurityReports
"""
import os
import django
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamm_leydi.settings')
django.setup()

from django.contrib.gis.geos import Point
from core.models import User, Projet
from referentiels.models import (
    Commune, TypeIntervention, TypeInfrastructure, TypeActeur
)
from suivi.models import (
    Thematique, Indicateur, Intervention, ValeurIndicateur, CibleIndicateur,
    InterventionActeur, InterventionInfrastructure
)
from geo.models import Infrastructure, Acteur
from securite.models import TypeInsecurite, SecurityReport


# Coordonnées GPS réalistes pour Kédougou (Sénégal)
# Format: (latitude, longitude)
COORDS_COMMUNES = {
    'SN-KD-KEN-GAT': (12.5567, -12.1833),  # Gathiary
    'SN-KD-KEN-TOU': (12.5233, -12.2167),  # Toumboura
    'SN-KD-KEN-MED': (12.4900, -12.2500),  # Médina Foulbé
    'SN-KD-KEN-SAD': (12.5667, -12.1333),  # Sadatou
}


def random_point_near(lat, lon, radius_km=5):
    """Générer un point aléatoire autour d'une coordonnée (rayon en km)"""
    # Approximation: 1 degré ≈ 111 km
    radius_deg = radius_km / 111.0
    lat_offset = random.uniform(-radius_deg, radius_deg)
    lon_offset = random.uniform(-radius_deg, radius_deg)
    return Point(lon + lon_offset, lat + lat_offset, srid=4326)


def get_or_create_data():
    """Récupérer les données de référence créées par init_data.py"""
    projet = Projet.objects.get(code_projet='JAMM-LEYDI-2024')
    admin_user = User.objects.get(username='admin')
    communes = {c.code_commune: c for c in Commune.objects.all()}
    types_intervention = {t.code: t for t in TypeIntervention.objects.all()}
    types_infra = {t.code: t for t in TypeInfrastructure.objects.all()}
    types_acteur = {t.code: t for t in TypeActeur.objects.all()}
    types_insecurite = {t.code: t for t in TypeInsecurite.objects.all()}
    indicateurs = {i.code: i for i in Indicateur.objects.all()}

    return {
        'projet': projet,
        'admin_user': admin_user,
        'communes': communes,
        'types_intervention': types_intervention,
        'types_infra': types_infra,
        'types_acteur': types_acteur,
        'types_insecurite': types_insecurite,
        'indicateurs': indicateurs,
    }


def create_interventions(data):
    """Créer des interventions de démonstration"""
    print("Création des interventions...")

    interventions_demo = [
        # R1 - Rencontres et formations
        {
            'indicateur': data['indicateurs']['R1.1'],  # Participants aux PAL
            'commune': data['communes']['SN-KD-KEN-GAT'],
            'type_intervention': data['types_intervention']['RENCONTRES'],
            'libelle': 'Atelier de lancement du projet JAMM LEYDI',
            'description': 'Atelier de présentation du projet aux autorités locales et représentants communautaires',
            'nature': 'ACTIVITE',
            'date_intervention': date(2024, 6, 15),
            'valeur_quantitative': 85,
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-GAT'], radius_km=2),
            'statut': 'PUBLIE',
            'cree_par': data['admin_user'],
            'valide_par': data['admin_user'],
        },
        {
            'indicateur': data['indicateurs']['R1.2'],  # Entités formées/soutenues
            'commune': data['communes']['SN-KD-KEN-TOU'],
            'type_intervention': data['types_intervention']['RENCONTRES'],
            'libelle': 'Formation sur la gestion des conflits fonciers',
            'description': 'Formation des leaders communautaires sur les techniques de médiation',
            'nature': 'ACTIVITE',
            'date_intervention': date(2024, 10, 15),
            'valeur_quantitative': 35,
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-TOU'], radius_km=1),
            'statut': 'PUBLIE',
            'cree_par': data['admin_user'],
            'valide_par': data['admin_user'],
        },

        # R2 - Rencontres intercommunautaires
        {
            'indicateur': data['indicateurs']['R2.2'],  # Personnes formées
            'commune': data['communes']['SN-KD-KEN-MED'],
            'type_intervention': data['types_intervention']['RENCONTRES'],
            'libelle': 'Rencontre intercommunautaire sur la gestion de l\'eau',
            'description': 'Dialogue entre communautés sur la gestion partagée des ressources en eau',
            'nature': 'ACTIVITE',
            'date_intervention': date(2024, 9, 10),
            'valeur_quantitative': 120,
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-MED'], radius_km=1.5),
            'statut': 'PUBLIE',
            'cree_par': data['admin_user'],
            'valide_par': data['admin_user'],
        },

        # R3 - Réalisations matérielles
        {
            'indicateur': data['indicateurs']['R3.2'],  # Initiatives économiques
            'commune': data['communes']['SN-KD-KEN-GAT'],
            'type_intervention': data['types_intervention']['AGRO'],
            'libelle': 'Périmètre maraîcher de Gathiary',
            'description': 'Aménagement d\'un périmètre maraîcher de 2 hectares pour 30 femmes',
            'nature': 'REALISATION',
            'date_intervention': date(2024, 9, 1),
            'valeur_quantitative': 2,
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-GAT'], radius_km=3),
            'statut': 'VALIDE',
            'cree_par': data['admin_user'],
            'valide_par': data['admin_user'],
        },
        {
            'indicateur': data['indicateurs']['R3.3'],  # Réseaux AEP
            'commune': data['communes']['SN-KD-KEN-TOU'],
            'type_intervention': data['types_intervention']['HYDRO'],
            'libelle': 'Réhabilitation forage de Toumboura',
            'description': 'Réhabilitation du forage principal et installation château d\'eau',
            'nature': 'REALISATION',
            'date_intervention': date(2024, 8, 15),
            'valeur_quantitative': 1,
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-TOU'], radius_km=1),
            'statut': 'PUBLIE',
            'cree_par': data['admin_user'],
            'valide_par': data['admin_user'],
        },
        {
            'indicateur': data['indicateurs']['R3.4'],  # Élèves cantines
            'commune': data['communes']['SN-KD-KEN-MED'],
            'type_intervention': data['types_intervention']['CANTINES'],
            'libelle': 'Cantine scolaire de Médina Foulbé',
            'description': 'Construction et équipement cantine scolaire pour 150 élèves',
            'nature': 'REALISATION',
            'date_intervention': date(2024, 9, 1),
            'valeur_quantitative': 150,
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-MED'], radius_km=0.5),
            'statut': 'EN_REVISION',
            'cree_par': data['admin_user'],
        },
        {
            'indicateur': data['indicateurs']['R3.2'],  # Initiatives économiques
            'commune': data['communes']['SN-KD-KEN-SAD'],
            'type_intervention': data['types_intervention']['ECO'],
            'libelle': 'Initiative apicole de Sadatou',
            'description': 'Formation et équipement de 15 jeunes pour l\'apiculture moderne',
            'nature': 'REALISATION',
            'date_intervention': date(2024, 7, 1),
            'valeur_quantitative': 15,
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-SAD'], radius_km=2),
            'statut': 'PUBLIE',
            'cree_par': data['admin_user'],
            'valide_par': data['admin_user'],
        },
        {
            'indicateur': data['indicateurs']['R3.2'],  # Initiatives économiques
            'commune': data['communes']['SN-KD-KEN-SAD'],
            'type_intervention': data['types_intervention']['AGRO'],
            'libelle': 'Mare pastorale de Sadatou',
            'description': 'Aménagement d\'une mare pastorale pour 200 têtes de bétail',
            'nature': 'REALISATION',
            'date_intervention': date(2024, 8, 10),
            'valeur_quantitative': 200,
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-SAD'], radius_km=4),
            'statut': 'VALIDE',
            'cree_par': data['admin_user'],
            'valide_par': data['admin_user'],
        },
    ]

    interventions_creees = []
    for int_data in interventions_demo:
        indicateur = int_data['indicateur']
        intervention, created = Intervention.objects.get_or_create(
            projet=indicateur.projet,
            indicateur=indicateur,
            libelle=int_data['libelle'],
            defaults=int_data
        )

        if created:
            print(f"  OK Intervention creee : {intervention.libelle}")
        else:
            print(f"  OK Intervention existe : {intervention.libelle}")

        interventions_creees.append(intervention)

    return interventions_creees


def create_infrastructures(data):
    """Créer des infrastructures géolocalisées"""
    print("Creation des infrastructures...")

    infrastructures_demo = [
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-TOU'],
            'type_infrastructure': data['types_infra']['FORAGE'],
            'nom': 'Forage principal de Toumboura',
            'description': 'Forage équipé d\'une pompe solaire',
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-TOU'], radius_km=1),
            'statut': 'FONCTIONNEL',
            'nb_beneficiaires': 1200,
            'cout_construction': Decimal('25000'),
            'date_construction': date(2024, 10, 30),
            'caracteristiques': {
                'profondeur': '65 metres',
                'debit': '5 m3/h',
                'type_pompe': 'Solaire',
            }
        },
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-GAT'],
            'type_infrastructure': data['types_infra']['MARAICHAGE'],
            'nom': 'Perimetre maraicher Natangue',
            'description': 'Perimetre de 2 ha avec systeme d\'irrigation goutte-a-goutte',
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-GAT'], radius_km=3),
            'statut': 'EN_CONSTRUCTION',
            'nb_beneficiaires': 30,
            'cout_construction': Decimal('15000'),
            'date_construction': date(2024, 9, 1),
            'caracteristiques': {
                'surface': '2 hectares',
                'irrigation': 'Goutte-a-goutte',
                'cloture': 'Oui',
            }
        },
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-MED'],
            'type_infrastructure': data['types_infra']['CANTINE'],
            'nom': 'Cantine scolaire de Medina Foulbe',
            'description': 'Cantine equipee pour 150 eleves',
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-MED'], radius_km=0.5),
            'statut': 'EN_CONSTRUCTION',
            'nb_beneficiaires': 150,
            'cout_construction': Decimal('35000'),
            'date_construction': date(2024, 9, 1),
            'caracteristiques': {
                'capacite': '150 repas/jour',
                'equipements': 'Cuisiniere gaz, marmites, vaisselle',
                'stockage': 'Magasin attenant',
            }
        },
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-SAD'],
            'type_infrastructure': data['types_infra']['MARE'],
            'nom': 'Mare pastorale de Sadatou',
            'description': 'Mare amenagee pour abreuvement du betail',
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-SAD'], radius_km=4),
            'statut': 'EN_CONSTRUCTION',
            'nb_beneficiaires': 80,  # éleveurs
            'cout_construction': Decimal('18000'),
            'date_construction': date(2024, 8, 10),
            'caracteristiques': {
                'capacite': '200 tetes de betail',
                'amenagements': 'Bac de decantation, abreuvoir',
                'superficie': '0.5 hectare',
            }
        },
    ]

    infrastructures_creees = []
    for infra_data in infrastructures_demo:
        infrastructure, created = Infrastructure.objects.get_or_create(
            projet=infra_data['projet'],
            nom=infra_data['nom'],
            defaults=infra_data
        )

        if created:
            print(f"  OK Infrastructure creee : {infrastructure.nom}")
        else:
            print(f"  OK Infrastructure existe : {infrastructure.nom}")

        infrastructures_creees.append(infrastructure)

    return infrastructures_creees


def create_acteurs(data):
    """Créer des acteurs géolocalisés"""
    print("Creation des acteurs...")

    acteurs_demo = [
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-GAT'],
            'type_acteur': data['types_acteur']['GF'],
            'denomination': 'Groupement feminin Natangue',
            'sigle': 'GFN',
            'description': 'Groupement de femmes pour le maraichage',
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-GAT'], radius_km=3),
            'nb_adherents': 30,
            'nb_femmes': 30,
            'nb_hommes': 0,
            'nb_jeunes': 8,
            'responsable': 'Mariama Diallo',
            'telephone': '+221 77 234 56 78',
            'domaines_activite': ['Maraichage', 'Transformation produits agricoles'],
        },
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-SAD'],
            'type_acteur': data['types_acteur']['ELEVEURS'],
            'denomination': 'Association des eleveurs de Sadatou',
            'sigle': 'AES',
            'description': 'Association pour la gestion du betail et des paturages',
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-SAD'], radius_km=2),
            'nb_adherents': 85,
            'nb_femmes': 15,
            'nb_hommes': 70,
            'nb_jeunes': 25,
            'responsable': 'Ousmane Ba',
            'telephone': '+221 77 345 67 89',
            'domaines_activite': ['Elevage bovin', 'Gestion paturages', 'Sante animale'],
        },
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-TOU'],
            'type_acteur': data['types_acteur']['COMITE'],
            'denomination': 'Comite de gestion du forage de Toumboura',
            'sigle': 'CGFT',
            'description': 'Comite pour la gestion et maintenance du forage',
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-TOU'], radius_km=1),
            'nb_adherents': 12,
            'nb_femmes': 5,
            'nb_hommes': 7,
            'nb_jeunes': 2,
            'responsable': 'Abdoulaye Keita',
            'telephone': '+221 77 456 78 90',
            'domaines_activite': ['Gestion eau', 'Maintenance infrastructure'],
        },
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-GAT'],
            'type_acteur': data['types_acteur']['CM'],
            'denomination': 'Conseil Municipal de Gathiary',
            'sigle': 'CM-GAT',
            'description': 'Autorite locale de la commune',
            'geom': Point(*reversed(COORDS_COMMUNES['SN-KD-KEN-GAT']), srid=4326),
            'nb_adherents': 25,
            'nb_femmes': 8,
            'nb_hommes': 17,
            'nb_jeunes': 5,
            'responsable': 'Mamadou Sow (Maire)',
            'telephone': '+221 77 567 89 01',
            'email': 'mairie.gathiary@gouv.sn',
            'domaines_activite': ['Gouvernance locale', 'Developpement communal'],
        },
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-MED'],
            'type_acteur': data['types_acteur']['OSC'],
            'denomination': 'OSC pour le Developpement de Medina Foulbe',
            'sigle': 'OSC-MF',
            'description': 'Association locale de developpement',
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-MED'], radius_km=0.5),
            'nb_adherents': 45,
            'nb_femmes': 20,
            'nb_hommes': 25,
            'nb_jeunes': 18,
            'responsable': 'Fatou Sall',
            'telephone': '+221 77 678 90 12',
            'domaines_activite': ['Education', 'Sante', 'Environnement'],
        },
    ]

    acteurs_crees = []
    for acteur_data in acteurs_demo:
        acteur, created = Acteur.objects.get_or_create(
            projet=acteur_data['projet'],
            denomination=acteur_data['denomination'],
            defaults=acteur_data
        )

        if created:
            print(f"  OK Acteur cree : {acteur.denomination}")
        else:
            print(f"  OK Acteur existe : {acteur.denomination}")

        acteurs_crees.append(acteur)

    return acteurs_crees


def link_interventions_acteurs_infrastructures(interventions, acteurs, infrastructures):
    """Créer les relations Many-to-Many"""
    print("Creation des relations interventions <-> acteurs/infrastructures...")

    # Lier périmètre maraîcher avec groupement féminin
    perimetre = next((i for i in interventions if 'maraicher' in i.libelle.lower()), None)
    groupement_feminin = next((a for a in acteurs if 'feminin' in a.denomination.lower()), None)
    infra_maraichage = next((i for i in infrastructures if 'maraicher' in i.nom.lower()), None)

    if perimetre and groupement_feminin:
        InterventionActeur.objects.get_or_create(
            intervention=perimetre,
            acteur=groupement_feminin,
            defaults={'role': 'Beneficiaire principal'}
        )
        print("  OK Lien: Perimetre maraicher <-> Groupement feminin")

    if perimetre and infra_maraichage:
        InterventionInfrastructure.objects.get_or_create(
            intervention=perimetre,
            infrastructure=infra_maraichage,
            defaults={'commentaire': 'Construction du périmètre maraîcher'}
        )
        print("  OK Lien: Intervention <-> Infrastructure maraichage")

    # Lier forage avec comité de gestion
    forage_intervention = next((i for i in interventions if 'forage' in i.libelle.lower()), None)
    comite_gestion = next((a for a in acteurs if 'comite' in a.denomination.lower()), None)
    infra_forage = next((i for i in infrastructures if 'forage' in i.nom.lower()), None)

    if forage_intervention and comite_gestion:
        InterventionActeur.objects.get_or_create(
            intervention=forage_intervention,
            acteur=comite_gestion,
            defaults={'role': 'Gestionnaire'}
        )
        print("  OK Lien: Forage <-> Comite de gestion")

    if forage_intervention and infra_forage:
        InterventionInfrastructure.objects.get_or_create(
            intervention=forage_intervention,
            infrastructure=infra_forage,
            defaults={'commentaire': 'Réhabilitation du forage'}
        )
        print("  OK Lien: Intervention <-> Forage")


def create_valeurs_indicateurs(data):
    """Créer des valeurs d'indicateurs pour T3 et T4 2024"""
    print("Creation des valeurs d'indicateurs...")

    valeurs_demo = [
        # R1
        {'code': 'R1.1', 'valeur': 48, 'trimestre': 'T3', 'source': 'SAISIE_MANUELLE'},
        {'code': 'R1.1', 'valeur': 60, 'trimestre': 'T4', 'source': 'SAISIE_MANUELLE'},
        {'code': 'R1.2', 'valeur': 52, 'trimestre': 'T3', 'source': 'SAISIE_MANUELLE'},
        {'code': 'R1.2', 'valeur': 68, 'trimestre': 'T4', 'source': 'SAISIE_MANUELLE'},
        {'code': 'R1.3', 'valeur': 10, 'trimestre': 'T3', 'source': 'DENOMBREMENT'},
        {'code': 'R1.3', 'valeur': 13, 'trimestre': 'T4', 'source': 'DENOMBREMENT'},

        # R2
        {'code': 'R2.1', 'valeur': 7, 'trimestre': 'T3', 'source': 'DENOMBREMENT'},
        {'code': 'R2.1', 'valeur': 9, 'trimestre': 'T4', 'source': 'DENOMBREMENT'},
        {'code': 'R2.2', 'valeur': 135, 'trimestre': 'T3', 'source': 'SOMME'},
        {'code': 'R2.2', 'valeur': 180, 'trimestre': 'T4', 'source': 'SOMME'},
        {'code': 'R2.3', 'valeur': 3850, 'trimestre': 'T3', 'source': 'SOMME'},
        {'code': 'R2.3', 'valeur': 5200, 'trimestre': 'T4', 'source': 'SOMME'},

        # R3
        {'code': 'R3.1', 'valeur': 2, 'trimestre': 'T3', 'source': 'DENOMBREMENT'},
        {'code': 'R3.1', 'valeur': 3, 'trimestre': 'T4', 'source': 'DENOMBREMENT'},
        {'code': 'R3.2', 'valeur': 9, 'trimestre': 'T3', 'source': 'DENOMBREMENT'},
        {'code': 'R3.2', 'valeur': 12, 'trimestre': 'T4', 'source': 'DENOMBREMENT'},
        {'code': 'R3.3', 'valeur': 2, 'trimestre': 'T3', 'source': 'DENOMBREMENT'},
        {'code': 'R3.3', 'valeur': 3, 'trimestre': 'T4', 'source': 'DENOMBREMENT'},
        {'code': 'R3.4', 'valeur': 450, 'trimestre': 'T3', 'source': 'SOMME'},
        {'code': 'R3.4', 'valeur': 620, 'trimestre': 'T4', 'source': 'SOMME'},
        {'code': 'R3.5', 'valeur': 1, 'trimestre': 'T3', 'source': 'DENOMBREMENT'},
        {'code': 'R3.5', 'valeur': 2, 'trimestre': 'T4', 'source': 'DENOMBREMENT'},
        {'code': 'R3.6', 'valeur': 18, 'trimestre': 'T3', 'source': 'MANUEL'},
        {'code': 'R3.6', 'valeur': 25, 'trimestre': 'T4', 'source': 'MANUEL'},
    ]

    base_date_t3 = date(2024, 9, 30)
    base_date_t4 = date(2024, 12, 31)

    for val_data in valeurs_demo:
        try:
            indicateur = data['indicateurs'][val_data['code']]
            date_mesure = base_date_t3 if val_data['trimestre'] == 'T3' else base_date_t4

            valeur, created = ValeurIndicateur.objects.get_or_create(
                indicateur=indicateur,
                date_mesure=date_mesure,
                commune=None,  # Valeur globale
                defaults={
                    'valeur_realisee': val_data['valeur'],
                    'source': val_data['source'],
                    'statut': 'PUBLIE',
                    'saisi_par': data['admin_user'],
                    'commentaire': f"Donnees de demonstration {val_data['trimestre']} 2024",
                }
            )

            if created:
                print(f"  OK Valeur creee : {indicateur.code} - {val_data['trimestre']} = {val_data['valeur']}")
            else:
                print(f"  OK Valeur existe : {indicateur.code} - {val_data['trimestre']}")

        except KeyError:
            print(f"  ERREUR: Indicateur {val_data['code']} non trouve")


def create_security_reports(data):
    """Créer des rapports de sécurité de démonstration"""
    print("Creation des rapports de securite...")

    rapports_demo = [
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-GAT'],
            'type_insecurite': data['types_insecurite']['FONCIER'],
            'libelle': 'Conflit foncier entre agriculteurs et eleveurs',
            'description': 'Tension autour d\'un terrain conteste entre un groupement d\'agriculteurs et des eleveurs',
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-GAT'], radius_km=5),
            'date_incident': date(2024, 7, 12),
            'gravite': 'MOYENNE',
            'nb_personnes_affectees': 45,
            'statut': 'CONFIRME',
            'actions_entreprises': 'Mediation par le conseil municipal en cours',
            'confidentiel': False,
            'cree_par': data['admin_user'],
        },
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-TOU'],
            'type_insecurite': data['types_insecurite']['EAU'],
            'libelle': 'Conflit autour du point d\'eau de Toumboura',
            'description': 'Tensions entre villages pour l\'acces au forage',
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-TOU'], radius_km=2),
            'date_incident': date(2024, 8, 5),
            'gravite': 'ELEVEE',
            'nb_personnes_affectees': 120,
            'statut': 'RESOLU',
            'actions_entreprises': 'Rehabilitation du forage et mise en place comite de gestion paritaire',
            'date_resolution': date(2024, 10, 30),
            'confidentiel': False,
            'cree_par': data['admin_user'],
        },
        {
            'projet': data['projet'],
            'commune': data['communes']['SN-KD-KEN-SAD'],
            'type_insecurite': data['types_insecurite']['VOL_BETAIL'],
            'libelle': 'Vol de betail signale',
            'description': 'Plusieurs tetes de betail disparues',
            'geom': random_point_near(*COORDS_COMMUNES['SN-KD-KEN-SAD'], radius_km=6),
            'date_incident': date(2024, 9, 18),
            'gravite': 'FAIBLE',
            'nb_personnes_affectees': 8,
            'statut': 'RESOLU',
            'actions_entreprises': 'Renforcement surveillance par l\'association d\'eleveurs',
            'date_resolution': date(2024, 9, 25),
            'confidentiel': False,
            'cree_par': data['admin_user'],
        },
    ]

    for rapport_data in rapports_demo:
        rapport, created = SecurityReport.objects.get_or_create(
            projet=rapport_data['projet'],
            libelle=rapport_data['libelle'],
            defaults=rapport_data
        )

        if created:
            print(f"  OK Rapport securite cree : {rapport.libelle}")
        else:
            print(f"  OK Rapport securite existe : {rapport.libelle}")


def main():
    """Fonction principale"""
    print("=" * 70)
    print("CREATION DES DONNEES DE DEMONSTRATION - ARCHITECTURE V2")
    print("=" * 70)
    print()

    # Récupérer les données de référence
    data = get_or_create_data()

    # Créer les données de test
    interventions = create_interventions(data)
    print()

    infrastructures = create_infrastructures(data)
    print()

    acteurs = create_acteurs(data)
    print()

    link_interventions_acteurs_infrastructures(interventions, acteurs, infrastructures)
    print()

    create_valeurs_indicateurs(data)
    print()

    create_security_reports(data)
    print()

    print("=" * 70)
    print("DONNEES DE DEMONSTRATION CREEES AVEC SUCCES")
    print("=" * 70)
    print()
    print("Statistiques :")
    print(f"  - {Intervention.objects.count()} Interventions")
    print(f"  - {Infrastructure.objects.count()} Infrastructures")
    print(f"  - {Acteur.objects.count()} Acteurs")
    print(f"  - {ValeurIndicateur.objects.count()} Valeurs d'indicateurs")
    print(f"  - {SecurityReport.objects.count()} Rapports de securite")
    print()
    print("Vous pouvez maintenant tester la plateforme :")
    print("  - Admin Django : http://localhost:8000/admin/")
    print("  - Dashboard : http://localhost:8000/dashboard/")
    print("  - Interface publique : http://localhost:8000/public/")
    print()


if __name__ == '__main__':
    main()
