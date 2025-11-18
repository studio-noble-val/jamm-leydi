# -*- coding: utf-8 -*-
"""
Script de génération de données de démonstration pour le projet JAMM LEYDI
Basé sur les TDR officiels du projet (doc/GRDR - TDR WEBSIG JAMM LEYDI - v1.pdf)

Ce script crée un jeu de données réaliste correspondant aux indicateurs
et activités décrites dans les Termes de Référence.
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamm_leydi.settings')
django.setup()

from django.contrib.gis.geos import Point
from core.models import Projet, User, UserProjet
from referentiels.models import (
    Commune, ProjetCommune, ChefLieu, TypeIntervention, TypeActeur, EquipeGRDR
)
from geo.models import Acteur
from suivi.models import Thematique, Indicateur, CibleIndicateur, Intervention, ValeurIndicateur


def clear_existing_data():
    """Supprime les données existantes pour repartir à zéro"""
    print("🗑️  Suppression des données existantes...")

    # Supprimer dans l'ordre (contraintes de clés étrangères)
    ValeurIndicateur.objects.all().delete()
    Intervention.objects.all().delete()
    Acteur.objects.all().delete()
    CibleIndicateur.objects.all().delete()
    Indicateur.objects.all().delete()
    TypeIntervention.objects.all().delete()
    TypeActeur.objects.all().delete()
    Thematique.objects.all().delete()
    ProjetCommune.objects.all().delete()
    ChefLieu.objects.all().delete()
    Commune.objects.all().delete()
    UserProjet.objects.filter(projet__code_projet='JAMM-LEYDI-2024').delete()
    Projet.objects.filter(code_projet='JAMM-LEYDI-2024').delete()

    print("✅ Données existantes supprimées")


def create_equipe_grdr():
    """Crée l'équipe GRDR Sénégal"""
    print("\n👥 Création de l'équipe GRDR...")

    equipe, created = EquipeGRDR.objects.get_or_create(
        code='GRDR-SN-BAKEL',
        defaults={
            'nom': 'Équipe GRDR Bakel - Sénégal',
            'type_equipe': 'COORDINATION',
            'pays': 'Sénégal',
            'ville': 'Bakel',
            'email': 'bakel@grdr.org',
            'telephone': '+221 33 XXX XX XX',
            'actif': True
        }
    )

    if created:
        print(f"✅ Équipe GRDR créée : {equipe.nom}")
    else:
        print(f"ℹ️  Équipe GRDR existante : {equipe.nom}")

    return equipe


def create_projet(equipe_grdr):
    """Crée le projet JAMM LEYDI selon les TDR"""
    print("\n📋 Création du projet JAMM LEYDI...")

    projet = Projet.objects.create(
        code_projet='JAMM-LEYDI-2024',
        libelle='JAMM LEYDI - Territoire Apaisé',
        description="""
        Projet de prévention durable des conflits liés au changement climatique et à la gestion
        des ressources naturelles frontalières dans le territoire de la Falémé.

        Zone d'intervention : Arrondissement de Kéniéba (département de Bakel, région de Tambacounda).

        Objectifs :
        - R1 : Renforcement des capacités des acteurs locaux dans l'adaptation au changement climatique
        - R2 : Renforcement de la cohésion sociale et de la gouvernance locale
        - R3 : Développement de solutions locales de résilience et accès aux services sociaux de base
        """,
        pays='Sénégal',
        zone_intervention='Arrondissement de Kéniéba, Département de Bakel, Région de Tambacounda',
        equipe_grdr=equipe_grdr,
        bailleurs='Union Européenne',
        date_debut=datetime(2024, 1, 1).date(),
        date_fin=datetime(2026, 12, 31).date(),
        budget=Decimal('1500000.00'),  # Budget estimatif
        devise='EUR',
        statut='EN_COURS',
        actif=True
    )

    print(f"✅ Projet créé : {projet.code_projet}")
    return projet


def create_communes(projet):
    """Crée les 4 communes de l'arrondissement de Kéniéba"""
    print("\n🏘️  Création des communes...")

    # Coordonnées approximatives des chefs-lieux (zone Kéniéba, Sénégal)
    communes_data = [
        {
            'nom': 'Gathiary',
            'code': 'SN-KEN-GATH',
            'lat': 12.820,
            'lon': -11.450,
            'population': 8500
        },
        {
            'nom': 'Toumboura',
            'code': 'SN-KEN-TOUM',
            'lat': 12.750,
            'lon': -11.380,
            'population': 7200
        },
        {
            'nom': 'Médina Foulbé',
            'code': 'SN-KEN-MEDF',
            'lat': 12.680,
            'lon': -11.520,
            'population': 6800
        },
        {
            'nom': 'Sadatou',
            'code': 'SN-KEN-SADA',
            'lat': 12.900,
            'lon': -11.420,
            'population': 9200
        }
    ]

    communes = []
    for data in communes_data:
        commune = Commune.objects.create(
            nom=data['nom'],
            code_commune=data['code'],
            departement='Bakel',
            region='Tambacounda',
            population=data['population'],
            annee_recensement=2023
        )

        # Créer le chef-lieu avec coordonnées GPS
        ChefLieu.objects.create(
            commune=commune,
            nom=data['nom'],
            geom=Point(data['lon'], data['lat'], srid=4326)
        )

        # Associer la commune au projet
        ProjetCommune.objects.create(
            projet=projet,
            commune=commune,
            prioritaire=True
        )

        communes.append(commune)
        print(f"  ✅ Commune créée : {commune.nom} ({commune.population} habitants)")

    return communes


def create_thematiques(projet):
    """Crée les 3 thématiques principales du projet"""
    print("\n🎯 Création des thématiques...")

    thematiques_data = [
        {
            'code': 'R1',
            'libelle': 'Renforcement des capacités',
            'description': 'Renforcement des capacités des acteurs locaux dans l\'adaptation au changement climatique et la prévention des conflits.'
        },
        {
            'code': 'R2',
            'libelle': 'Cohésion sociale',
            'description': 'Renforcement de la cohésion sociale et de la gouvernance locale autour de la gestion des ressources naturelles.'
        },
        {
            'code': 'R3',
            'libelle': 'Résilience et services',
            'description': 'Développement de solutions locales de résilience et amélioration de l\'accès aux services sociaux de base.'
        }
    ]

    thematiques = []
    for i, data in enumerate(thematiques_data):
        thematique = Thematique.objects.create(
            projet=projet,
            code=data['code'],
            libelle=data['libelle'],
            description=data['description'],
            ordre=i + 1
        )
        thematiques.append(thematique)
        print(f"  ✅ Thématique créée : {thematique.code} - {thematique.libelle}")

    return thematiques


def create_indicateurs(thematiques, communes):
    """Crée les indicateurs du cadre logique selon les TDR"""
    print("\n📊 Création des indicateurs...")

    # Trouver les thématiques par code
    r1 = next(t for t in thematiques if t.code == 'R1')
    r2 = next(t for t in thematiques if t.code == 'R2')
    r3 = next(t for t in thematiques if t.code == 'R3')

    indicateurs_data = [
        # Indicateurs R1
        {
            'thematique': r1,
            'code': 'R1.1',
            'libelle': 'Nombre de participants à la co-actualisation des plans d\'actions locales',
            'unite_mesure': 'Personnes',
            'type_calcul': 'SOMME',
            'cible_globale': 60
        },
        {
            'thematique': r1,
            'code': 'R1.2',
            'libelle': 'Nombre d\'entités formées ou soutenues pour la prévention',
            'unite_mesure': 'Personnes',
            'type_calcul': 'SOMME',
            'cible_globale': 80
        },

        # Indicateurs R2
        {
            'thematique': r2,
            'code': 'R2.1',
            'libelle': 'Nombre d\'entités/réseaux soutenus ou formés',
            'unite_mesure': 'Organisations',
            'type_calcul': 'DENOMBREMENT',
            'cible_globale': 10
        },
        {
            'thematique': r2,
            'code': 'R2.2',
            'libelle': 'Nombre de personnes formées ayant amélioré leurs compétences',
            'unite_mesure': 'Personnes',
            'type_calcul': 'SOMME',
            'cible_globale': 250
        },

        # Indicateurs R3
        {
            'thematique': r3,
            'code': 'R3.1',
            'libelle': 'Nombre de communes avec PDC intégrant la prévention des conflits',
            'unite_mesure': 'Communes',
            'type_calcul': 'DENOMBREMENT',
            'cible_globale': 4
        },
        {
            'thematique': r3,
            'code': 'R3.2',
            'libelle': 'Nombre d\'initiatives économiques mises en œuvre',
            'unite_mesure': 'Initiatives',
            'type_calcul': 'DENOMBREMENT',
            'cible_globale': 20
        },
        {
            'thematique': r3,
            'code': 'R3.3',
            'libelle': 'Nombre de réseaux AEP réhabilités/construits',
            'unite_mesure': 'Réseaux',
            'type_calcul': 'DENOMBREMENT',
            'cible_globale': 8
        },
        {
            'thematique': r3,
            'code': 'R3.4',
            'libelle': 'Nombre d\'élèves ayant accès à des repas scolaires',
            'unite_mesure': 'Élèves',
            'type_calcul': 'SOMME',
            'cible_globale': 1200
        },
        {
            'thematique': r3,
            'code': 'R3.5',
            'libelle': 'Nombre de postes de santé réhabilités',
            'unite_mesure': 'Postes',
            'type_calcul': 'DENOMBREMENT',
            'cible_globale': 5
        },

        # Indicateurs de Réalisations
        {
            'thematique': r1,
            'code': 'REAL.1',
            'libelle': 'Nombre de structures bénéficiaires agissant pour la prévention des conflits',
            'unite_mesure': 'Structures',
            'type_calcul': 'DENOMBREMENT',
            'cible_globale': 15  # 4 conseils + 10 OSC + 1 cadre
        },
        {
            'thematique': r3,
            'code': 'REAL.2',
            'libelle': 'Nombre de personnes bénéficiant directement des interventions',
            'unite_mesure': 'Personnes',
            'type_calcul': 'SOMME',
            'cible_globale': 14700
        },

        # Indicateur d'Impact
        {
            'thematique': r1,
            'code': 'IMP.1',
            'libelle': 'Perception du niveau de sécurité par les habitants',
            'unite_mesure': 'Pourcentage',
            'type_calcul': 'MOYENNE',
            'cible_globale': 33  # Au moins 1/3 des habitants
        }
    ]

    indicateurs = []
    for i, data in enumerate(indicateurs_data):
        indicateur = Indicateur.objects.create(
            projet=data['thematique'].projet,
            thematique=data['thematique'],
            code=data['code'],
            libelle=data['libelle'],
            unite_mesure=data['unite_mesure'],
            type_calcul=data.get('type_calcul', 'SOMME'),
            ordre=i + 1
        )

        # Créer les cibles par commune et par année
        for commune in communes:
            # Répartir la cible globale entre les communes proportionnellement à la population
            total_pop = sum(c.population for c in communes)
            ratio = commune.population / total_pop
            cible_commune = int(data['cible_globale'] * ratio)

            for annee in [2024, 2025, 2026]:
                CibleIndicateur.objects.create(
                    indicateur=indicateur,
                    commune=commune,
                    annee=annee,
                    valeur_cible=cible_commune
                )

        indicateurs.append(indicateur)
        print(f"  ✅ Indicateur créé : {indicateur.code} - {indicateur.libelle}")

    return indicateurs


def create_types_intervention():
    """Crée les types d'intervention selon les TDR"""
    print("\n🔧 Création des types d'intervention...")

    types_data = [
        # R1 & R2 - Rencontres et Événements
        {
            'code': 'RENCONTRE',
            'libelle': 'Rencontre/Atelier',
            'description': 'Rencontres, ateliers, formations pour le renforcement des capacités'
        },

        # R3.1 - Activités Agro-sylvo-pastorales
        {
            'code': 'PERIMETRE',
            'libelle': 'Périmètre maraîcher',
            'description': 'Aménagement de périmètres maraîchers pour groupements féminins'
        },
        {
            'code': 'MARE',
            'libelle': 'Aménagement de mare',
            'description': 'Aménagement de mares pour activités agro-pastorales'
        },

        # R3.2 - Initiatives Économiques
        {
            'code': 'ECONOMIE',
            'libelle': 'Initiative économique',
            'description': 'Appui aux initiatives économiques (AGR, entreprises)'
        },

        # R3.3 - Infrastructures Hydrauliques
        {
            'code': 'HYDRAULIQUE',
            'libelle': 'Infrastructure hydraulique',
            'description': 'Réhabilitation/construction de réseaux AEP'
        },

        # R3.4 - Cantines Scolaires
        {
            'code': 'CANTINE',
            'libelle': 'Cantine scolaire',
            'description': 'Appui aux cantines scolaires'
        },

        # R3.5 - Postes de Santé
        {
            'code': 'SANTE',
            'libelle': 'Poste de santé',
            'description': 'Réhabilitation/équipement de postes de santé'
        }
    ]

    types = []
    for data in types_data:
        type_intervention = TypeIntervention.objects.create(
            code=data['code'],
            libelle=data['libelle'],
            description=data['description']
        )
        types.append(type_intervention)
        print(f"  ✅ Type créé : {type_intervention.code} - {type_intervention.libelle}")

    return types


def create_types_acteur():
    """Crée les types d'acteurs"""
    print("\n👤 Création des types d'acteur...")

    types_data = [
        {'code': 'OSC', 'libelle': 'Organisation de la Société Civile'},
        {'code': 'COLLECTIVITE', 'libelle': 'Collectivité Locale'},
        {'code': 'GROUPEMENT', 'libelle': 'Groupement (femmes/jeunes)'},
        {'code': 'COMITE', 'libelle': 'Comité de Gestion'},
        {'code': 'PARTENAIRE', 'libelle': 'Partenaire Technique'}
    ]

    types = []
    for data in types_data:
        type_acteur = TypeActeur.objects.create(
            code=data['code'],
            libelle=data['libelle']
        )
        types.append(type_acteur)
        print(f"  ✅ Type acteur créé : {type_acteur.code}")

    return types


def create_acteurs(types_acteur, communes, projet):
    """Crée des acteurs réalistes"""
    print("\n👥 Création des acteurs...")

    type_osc = next(t for t in types_acteur if t.code == 'OSC')
    type_collectivite = next(t for t in types_acteur if t.code == 'COLLECTIVITE')
    type_groupement = next(t for t in types_acteur if t.code == 'GROUPEMENT')

    acteurs = []

    # Fonction pour générer une position aléatoire près d'une commune
    def get_commune_point(commune):
        chef_lieu = commune.chef_lieu
        return chef_lieu.geom

    # Créer les conseils municipaux
    for commune in communes:
        acteur = Acteur.objects.create(
            projet=projet,
            denomination=f"Conseil Municipal de {commune.nom}",
            type_acteur=type_collectivite,
            commune=commune,
            telephone=f"+221 33 XXX XX XX",
            geom=get_commune_point(commune),
            statut='ACTIF'
        )
        acteurs.append(acteur)
        print(f"  ✅ Acteur créé : {acteur.denomination}")

    # Créer quelques OSC
    osc_names = [
        'Association des Jeunes de Kéniéba',
        'Collectif des Femmes de la Falémé',
        'Union des Éleveurs de Bakel',
        'Réseau des Producteurs Locaux'
    ]

    for name in osc_names:
        commune = random.choice(communes)
        acteur = Acteur.objects.create(
            projet=projet,
            denomination=name,
            type_acteur=type_osc,
            commune=commune,
            geom=get_commune_point(commune),
            statut='ACTIF'
        )
        acteurs.append(acteur)
        print(f"  ✅ Acteur créé : {acteur.denomination}")

    # Créer quelques groupements féminins
    for i, commune in enumerate(communes):
        acteur = Acteur.objects.create(
            projet=projet,
            denomination=f"Groupement de Femmes de {commune.nom}",
            type_acteur=type_groupement,
            commune=commune,
            nb_adherents=random.randint(15, 35),
            nb_femmes=random.randint(15, 35),
            geom=get_commune_point(commune),
            statut='ACTIF'
        )
        acteurs.append(acteur)
        print(f"  ✅ Acteur créé : {acteur.denomination}")

    return acteurs


def create_interventions(types_intervention, indicateurs, communes, acteurs):
    """Crée des interventions réalistes géolocalisées"""
    print("\n🗺️  Création des interventions...")

    # Récupérer les types
    type_rencontre = next(t for t in types_intervention if t.code == 'RENCONTRE')
    type_perimetre = next(t for t in types_intervention if t.code == 'PERIMETRE')
    type_mare = next(t for t in types_intervention if t.code == 'MARE')
    type_economie = next(t for t in types_intervention if t.code == 'ECONOMIE')
    type_hydraulique = next(t for t in types_intervention if t.code == 'HYDRAULIQUE')
    type_cantine = next(t for t in types_intervention if t.code == 'CANTINE')
    type_sante = next(t for t in types_intervention if t.code == 'SANTE')

    interventions = []

    # Fonction pour générer une position aléatoire autour d'une commune
    def random_point_near(commune, radius_km=5):
        # 1 degré ≈ 111 km
        radius_deg = radius_km / 111.0
        chef_lieu = commune.chef_lieu
        lat = chef_lieu.geom.y + random.uniform(-radius_deg, radius_deg)
        lon = chef_lieu.geom.x + random.uniform(-radius_deg, radius_deg)
        return Point(lon, lat, srid=4326)

    # Date de début du projet
    start_date = datetime(2024, 1, 1)

    # 1. Créer des rencontres/ateliers (R1 & R2)
    indicateur_r1_1 = next(i for i in indicateurs if i.code == 'R1.1')

    rencontres_data = [
        {'titre': 'Atelier de lancement du projet', 'participants': 80},
        {'titre': 'Formation sur l\'adaptation au changement climatique', 'participants': 45},
        {'titre': 'Atelier de co-actualisation des plans d\'actions', 'participants': 35},
        {'titre': 'Rencontre de concertation intercommunale', 'participants': 50},
        {'titre': 'Formation des relais communautaires', 'participants': 60},
        {'titre': 'Atelier de prévention des conflits', 'participants': 40},
    ]

    for i, data in enumerate(rencontres_data):
        commune = communes[i % len(communes)]
        date_intervention = start_date + timedelta(days=30 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r1_1.projet,
            indicateur=indicateur_r1_1,
            commune=commune,
            type_intervention=type_rencontre,
            libelle=data['titre'],
            description=f"Rencontre organisée dans le cadre du renforcement des capacités à {commune.nom}.",
            nature='ACTIVITE',
            statut='TERMINE',
            date_intervention=date_intervention.date(),
            valeur_quantitative=data['participants'],
            geom=random_point_near(commune, radius_km=2)
        )
        interventions.append(intervention)
        print(f"  ✅ Rencontre créée : {intervention.libelle}")

    # 2. Créer des périmètres maraîchers (R3.1)
    indicateur_r3_2 = next(i for i in indicateurs if i.code == 'R3.2')

    for i, commune in enumerate(communes):
        date_intervention = start_date + timedelta(days=60 + 30 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r3_2.projet,
            indicateur=indicateur_r3_2,
            commune=commune,
            type_intervention=type_perimetre,
            libelle=f"Aménagement périmètre maraîcher - {commune.nom}",
            description=f"Périmètre maraîcher de 2 hectares pour le groupement de femmes. Convention d'exploitation signée.",
            nature='REALISATION',
            statut='TERMINE' if i < 2 else 'PROGRAMME',
            date_intervention=date_intervention.date(),
            valeur_quantitative=30,  # Nombre de femmes bénéficiaires
            geom=random_point_near(commune, radius_km=3)
        )
        interventions.append(intervention)
        print(f"  ✅ Périmètre maraîcher créé : {intervention.libelle}")

    # 3. Créer des initiatives économiques (R3.2)
    initiatives_data = [
        {'titre': 'AGR transformation produits locaux', 'beneficiaires': 15},
        {'titre': 'Appui à l\'élevage de petits ruminants', 'beneficiaires': 20},
        {'titre': 'Commerce de produits maraîchers', 'beneficiaires': 12},
        {'titre': 'Atelier de couture et teinture', 'beneficiaires': 18},
        {'titre': 'Unité de transformation lait local', 'beneficiaires': 25},
    ]

    for i, data in enumerate(initiatives_data):
        commune = communes[i % len(communes)]
        date_intervention = start_date + timedelta(days=90 + 45 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r3_2.projet,
            indicateur=indicateur_r3_2,
            commune=commune,
            type_intervention=type_economie,
            libelle=data['titre'],
            description=f"Initiative économique portée par des femmes et jeunes de {commune.nom}.",
            nature='REALISATION',
            statut='TERMINE' if i < 3 else 'PROGRAMME',
            date_intervention=date_intervention.date(),
            valeur_quantitative=data['beneficiaires'],
            geom=random_point_near(commune)
        )
        interventions.append(intervention)
        print(f"  ✅ Initiative économique créée : {intervention.libelle}")

    # 4. Créer des réseaux hydrauliques (R3.3)
    indicateur_r3_3 = next(i for i in indicateurs if i.code == 'R3.3')

    for i in range(3):
        commune = communes[i]
        date_intervention = start_date + timedelta(days=120 + 60 * i)

        pop_desservie = random.randint(800, 1500)
        intervention = Intervention.objects.create(
            projet=indicateur_r3_3.projet,
            indicateur=indicateur_r3_3,
            commune=commune,
            type_intervention=type_hydraulique,
            libelle=f"Réhabilitation réseau AEP - {commune.nom}",
            description=f"Réhabilitation du réseau d'adduction d'eau potable. Population desservie estimée à {pop_desservie} personnes.",
            nature='REALISATION',
            statut='TERMINE' if i < 2 else 'PROGRAMME',
            date_intervention=date_intervention.date(),
            valeur_quantitative=pop_desservie,
            geom=random_point_near(commune, radius_km=1)
        )
        interventions.append(intervention)
        print(f"  ✅ Infrastructure hydraulique créée : {intervention.libelle}")

    # 5. Créer des cantines scolaires (R3.4)
    indicateur_r3_4 = next(i for i in indicateurs if i.code == 'R3.4')

    ecoles_data = [
        {'nom': 'École élémentaire de Gathiary', 'eleves': 320},
        {'nom': 'École de Toumboura Centre', 'eleves': 280},
        {'nom': 'École de Médina Foulbé', 'eleves': 250},
        {'nom': 'École de Sadatou Village', 'eleves': 350},
    ]

    for i, data in enumerate(ecoles_data):
        commune = communes[i]
        date_intervention = start_date + timedelta(days=150 + 30 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r3_4.projet,
            indicateur=indicateur_r3_4,
            commune=commune,
            type_intervention=type_cantine,
            libelle=f"Appui cantine - {data['nom']}",
            description=f"Appui à la cantine scolaire : fourniture vivres, équipements. Comité de gestion formé.",
            nature='REALISATION',
            statut='TERMINE' if i < 3 else 'PROGRAMME',
            date_intervention=date_intervention.date(),
            valeur_quantitative=data['eleves'],
            geom=random_point_near(commune, radius_km=1.5)
        )
        interventions.append(intervention)
        print(f"  ✅ Cantine scolaire créée : {intervention.libelle}")

    # 6. Créer des postes de santé (R3.5)
    indicateur_r3_5 = next(i for i in indicateurs if i.code == 'R3.5')

    for i in range(2):
        commune = communes[i]
        date_intervention = start_date + timedelta(days=180 + 60 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r3_5.projet,
            indicateur=indicateur_r3_5,
            commune=commune,
            type_intervention=type_sante,
            libelle=f"Réhabilitation poste de santé - {commune.nom}",
            description=f"Réhabilitation infrastructure + équipement médical de base.",
            nature='REALISATION',
            statut='TERMINE' if i < 1 else 'PROGRAMME',
            date_intervention=date_intervention.date(),
            valeur_quantitative=1,
            geom=random_point_near(commune, radius_km=0.5)
        )
        interventions.append(intervention)
        print(f"  ✅ Poste de santé créé : {intervention.libelle}")

    print(f"\n✅ Total : {len(interventions)} interventions créées")
    return interventions


def create_suivi_indicateurs(indicateurs):
    """Crée des données de suivi trimestriel pour les indicateurs"""
    print("\n📈 Création des suivis d'indicateurs...")

    trimestres = [
        ('2024-Q1', datetime(2024, 3, 31).date()),
        ('2024-Q2', datetime(2024, 6, 30).date()),
        ('2024-Q3', datetime(2024, 9, 30).date()),
        ('2024-Q4', datetime(2024, 12, 31).date()),
        ('2025-Q1', datetime(2025, 3, 31).date()),
    ]

    suivis = []
    for indicateur in indicateurs[:5]:  # Seulement les premiers indicateurs pour démo
        valeur_cumulative = 0

        for i, (code_trimestre, date_observation) in enumerate(trimestres):
            # Progression réaliste : augmentation progressive
            progression = random.randint(10, 30)
            valeur_cumulative += progression

            suivi = ValeurIndicateur.objects.create(
                indicateur=indicateur,
                date_mesure=date_observation,
                valeur_realisee=valeur_cumulative,
                source='SAISIE_MANUELLE',
                statut='VALIDE',
                commentaire=f"Avancement du trimestre {code_trimestre}. Progression conforme aux objectifs."
            )
            suivis.append(suivi)

    print(f"✅ {len(suivis)} suivis d'indicateurs créés")
    return suivis


def main():
    """Fonction principale"""
    print("="*80)
    print("🚀 GÉNÉRATION DES DONNÉES DE DÉMONSTRATION - PROJET JAMM LEYDI")
    print("="*80)

    # Demander confirmation
    response = input("\n⚠️  Cette opération va supprimer toutes les données existantes. Continuer ? (oui/non) : ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        return

    # Supprimer les données existantes
    clear_existing_data()

    # Créer les données dans l'ordre
    equipe_grdr = create_equipe_grdr()
    projet = create_projet(equipe_grdr)
    communes = create_communes(projet)
    thematiques = create_thematiques(projet)
    indicateurs = create_indicateurs(thematiques, communes)
    types_intervention = create_types_intervention()
    types_acteur = create_types_acteur()
    acteurs = create_acteurs(types_acteur, communes, projet)
    interventions = create_interventions(types_intervention, indicateurs, communes, acteurs)
    suivis = create_suivi_indicateurs(indicateurs)

    # Résumé
    print("\n" + "="*80)
    print("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS !")
    print("="*80)
    print(f"""
    📊 Résumé des données créées :

    - 1 projet : {projet.code_projet}
    - {len(communes)} communes
    - {len(thematiques)} thématiques
    - {len(indicateurs)} indicateurs
    - {len(types_intervention)} types d'intervention
    - {len(acteurs)} acteurs
    - {len(interventions)} interventions
    - {len(suivis)} suivis d'indicateurs

    🌐 Vous pouvez maintenant :
    - Accéder au dashboard : http://localhost:8000/dashboard/
    - Consulter l'interface publique : http://localhost:8000/public/
    - Gérer les données : http://localhost:8000/admin/

    Compte admin : admin / admin123
    """)
    print("="*80)


if __name__ == '__main__':
    main()
