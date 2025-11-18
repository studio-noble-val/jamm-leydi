# -*- coding: utf-8 -*-
"""
Script de génération de données de démonstration V2 pour le projet JAMM LEYDI
Données plus réalistes avec environ 2/3 des objectifs atteints

Version améliorée avec :
- Cohérence entre unités de mesure et valeurs
- Cibles réalistes par rapport aux réalisations
- Environ 66% d'avancement global
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
    """Supprime les données du projet JAMM LEYDI V2"""
    print("🗑️  Suppression des données existantes...")

    ValeurIndicateur.objects.filter(indicateur__projet__code_projet='JAMM-LEYDI-V2').delete()
    Intervention.objects.filter(projet__code_projet='JAMM-LEYDI-V2').delete()
    Acteur.objects.filter(projet__code_projet='JAMM-LEYDI-V2').delete()
    CibleIndicateur.objects.filter(indicateur__projet__code_projet='JAMM-LEYDI-V2').delete()
    Indicateur.objects.filter(projet__code_projet='JAMM-LEYDI-V2').delete()
    Thematique.objects.filter(projet__code_projet='JAMM-LEYDI-V2').delete()
    Projet.objects.filter(code_projet='JAMM-LEYDI-V2').delete()

    print("✅ Données existantes supprimées")


def create_projet(equipe_grdr, communes):
    """Crée le projet JAMM LEYDI V2"""
    print("\n📋 Création du projet JAMM LEYDI V2...")

    projet = Projet.objects.create(
        code_projet='JAMM-LEYDI-V2',
        libelle='JAMM LEYDI V2 - Territoire Apaisé (Démo)',
        description="""
        Projet de démonstration avec données réalistes.
        Avancement global : environ 66% des objectifs atteints.
        """,
        pays='Sénégal',
        zone_intervention='Arrondissement de Kéniéba, Département de Bakel, Région de Tambacounda',
        equipe_grdr=equipe_grdr,
        bailleurs='Union Européenne',
        date_debut=datetime(2024, 1, 1).date(),
        date_fin=datetime(2026, 12, 31).date(),
        budget=Decimal('1500000.00'),
        devise='EUR',
        statut='EN_COURS',
        actif=True
    )

    # Associer les communes existantes au projet
    for commune in communes:
        ProjetCommune.objects.create(
            projet=projet,
            commune=commune,
            prioritaire=True
        )

    print(f"✅ Projet créé : {projet.code_projet}")
    return projet


def create_thematiques(projet):
    """Crée les 3 thématiques"""
    print("\n🎯 Création des thématiques...")

    thematiques_data = [
        {'code': 'R1', 'libelle': 'Renforcement des capacités'},
        {'code': 'R2', 'libelle': 'Cohésion sociale'},
        {'code': 'R3', 'libelle': 'Résilience et services'}
    ]

    thematiques = []
    for i, data in enumerate(thematiques_data):
        thematique = Thematique.objects.create(
            projet=projet,
            code=data['code'],
            libelle=data['libelle'],
            ordre=i + 1
        )
        thematiques.append(thematique)
        print(f"  ✅ Thématique créée : {thematique.code} - {thematique.libelle}")

    return thematiques


def create_indicateurs_realistes(thematiques, communes):
    """Crée des indicateurs avec des cibles réalistes"""
    print("\n📊 Création des indicateurs avec cibles réalistes...")

    r1 = next(t for t in thematiques if t.code == 'R1')
    r2 = next(t for t in thematiques if t.code == 'R2')
    r3 = next(t for t in thematiques if t.code == 'R3')

    # Indicateurs avec cibles RÉALISTES
    indicateurs_data = [
        # R1 - Renforcement capacités
        {
            'thematique': r1,
            'code': 'R1.1',
            'libelle': 'Nombre de participants aux formations',
            'unite_mesure': 'Personnes',
            'cible_globale': 300,  # Cible réaliste pour 300 personnes formées
        },
        {
            'thematique': r1,
            'code': 'R1.2',
            'libelle': 'Nombre d\'organisations renforcées',
            'unite_mesure': 'Organisations',
            'cible_globale': 15,  # 15 organisations
        },

        # R2 - Cohésion sociale
        {
            'thematique': r2,
            'code': 'R2.1',
            'libelle': 'Nombre de rencontres intercommunales',
            'unite_mesure': 'Rencontres',
            'cible_globale': 12,  # 12 rencontres sur 3 ans
        },
        {
            'thematique': r2,
            'code': 'R2.2',
            'libelle': 'Nombre de participants aux rencontres',
            'unite_mesure': 'Personnes',
            'cible_globale': 240,  # 240 personnes
        },

        # R3 - Résilience
        {
            'thematique': r3,
            'code': 'R3.1',
            'libelle': 'Nombre de périmètres maraîchers aménagés',
            'unite_mesure': 'Périmètres',
            'cible_globale': 8,  # 8 périmètres (2 par commune)
        },
        {
            'thematique': r3,
            'code': 'R3.2',
            'libelle': 'Nombre de femmes bénéficiaires (maraîchage)',
            'unite_mesure': 'Femmes',
            'cible_globale': 240,  # 30 femmes x 8 périmètres
        },
        {
            'thematique': r3,
            'code': 'R3.3',
            'libelle': 'Nombre de réseaux AEP réhabilités',
            'unite_mesure': 'Réseaux',
            'cible_globale': 8,  # 8 réseaux (2 par commune)
        },
        {
            'thematique': r3,
            'code': 'R3.4',
            'libelle': 'Nombre d\'élèves bénéficiant de cantines',
            'unite_mesure': 'Élèves',
            'cible_globale': 1200,  # 1200 élèves
        },
        {
            'thematique': r3,
            'code': 'R3.5',
            'libelle': 'Nombre de postes de santé équipés',
            'unite_mesure': 'Postes',
            'cible_globale': 4,  # 4 postes (1 par commune)
        },
    ]

    indicateurs = []
    for i, data in enumerate(indicateurs_data):
        indicateur = Indicateur.objects.create(
            projet=data['thematique'].projet,
            thematique=data['thematique'],
            code=data['code'],
            libelle=data['libelle'],
            unite_mesure=data['unite_mesure'],
            type_calcul='SOMME',
            ordre=i + 1
        )

        # Créer les cibles par commune
        for commune in communes:
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
        print(f"  ✅ Indicateur créé : {indicateur.code} - Cible: {data['cible_globale']} {indicateur.unite_mesure}")

    return indicateurs


def create_interventions_realistes(types_intervention, indicateurs, communes):
    """Crée des interventions réalistes pour atteindre environ 66% des cibles"""
    print("\n🗺️  Création des interventions (objectif: ~66% d'avancement)...")

    interventions = []
    start_date = datetime(2024, 1, 1)

    def random_point_near(commune, radius_km=5):
        radius_deg = radius_km / 111.0
        chef_lieu = commune.chef_lieu
        lat = chef_lieu.geom.y + random.uniform(-radius_deg, radius_deg)
        lon = chef_lieu.geom.x + random.uniform(-radius_deg, radius_deg)
        return Point(lon, lat, srid=4326)

    # Types
    type_rencontre = next(t for t in types_intervention if t.code == 'RENCONTRE')
    type_perimetre = next(t for t in types_intervention if t.code == 'PERIMETRE')
    type_hydraulique = next(t for t in types_intervention if t.code == 'HYDRAULIQUE')
    type_cantine = next(t for t in types_intervention if t.code == 'CANTINE')
    type_sante = next(t for t in types_intervention if t.code == 'SANTE')

    # R1.1 - Formations (cible: 300, réaliser: 200 = 66%)
    indicateur_r1_1 = next(i for i in indicateurs if i.code == 'R1.1')
    formations = [
        {'titre': 'Formation adaptation changement climatique', 'participants': 45},
        {'titre': 'Atelier prévention des conflits', 'participants': 40},
        {'titre': 'Formation gestion ressources naturelles', 'participants': 38},
        {'titre': 'Atelier de co-actualisation des plans', 'participants': 42},
        {'titre': 'Formation des relais communautaires', 'participants': 35},
    ]

    for i, data in enumerate(formations):
        commune = communes[i % len(communes)]
        intervention = Intervention.objects.create(
            projet=indicateur_r1_1.projet,
            indicateur=indicateur_r1_1,
            commune=commune,
            type_intervention=type_rencontre,
            libelle=data['titre'],
            nature='ACTIVITE',
            statut='TERMINE',
            date_intervention=(start_date + timedelta(days=30 * i)).date(),
            valeur_quantitative=data['participants'],
            geom=random_point_near(commune)
        )
        interventions.append(intervention)

    print(f"  ✅ {len(formations)} formations créées (R1.1): {sum([f['participants'] for f in formations])}/300 participants")

    # R1.2 - Organisations renforcées (cible: 15, réaliser: 10 = 66%)
    indicateur_r1_2 = next(i for i in indicateurs if i.code == 'R1.2')
    for i in range(10):
        commune = communes[i % len(communes)]
        intervention = Intervention.objects.create(
            projet=indicateur_r1_2.projet,
            indicateur=indicateur_r1_2,
            commune=commune,
            type_intervention=type_rencontre,
            libelle=f"Appui organisation - {commune.nom} #{(i % 3) + 1}",
            nature='ACTIVITE',
            statut='TERMINE',
            date_intervention=(start_date + timedelta(days=45 * i)).date(),
            valeur_quantitative=1,
            geom=random_point_near(commune)
        )
        interventions.append(intervention)

    print(f"  ✅ 10 organisations renforcées (R1.2): 10/15")

    # R2.1 - Rencontres intercommunales (cible: 12, réaliser: 8 = 66%)
    indicateur_r2_1 = next(i for i in indicateurs if i.code == 'R2.1')
    for i in range(8):
        commune = communes[i % len(communes)]
        intervention = Intervention.objects.create(
            projet=indicateur_r2_1.projet,
            indicateur=indicateur_r2_1,
            commune=commune,
            type_intervention=type_rencontre,
            libelle=f"Rencontre intercommunale #{i+1}",
            nature='ACTIVITE',
            statut='TERMINE',
            date_intervention=(start_date + timedelta(days=40 * i)).date(),
            valeur_quantitative=1,
            geom=random_point_near(commune)
        )
        interventions.append(intervention)

    print(f"  ✅ 8 rencontres créées (R2.1): 8/12")

    # R2.2 - Participants rencontres (cible: 240, réaliser: 160 = 66%)
    indicateur_r2_2 = next(i for i in indicateurs if i.code == 'R2.2')
    participants_rencontres = [22, 18, 25, 19, 21, 20, 17, 18]  # Total: 160
    for i, nb_participants in enumerate(participants_rencontres):
        commune = communes[i % len(communes)]
        intervention = Intervention.objects.create(
            projet=indicateur_r2_2.projet,
            indicateur=indicateur_r2_2,
            commune=commune,
            type_intervention=type_rencontre,
            libelle=f"Concertation gestion ressources - {commune.nom}",
            nature='ACTIVITE',
            statut='TERMINE',
            date_intervention=(start_date + timedelta(days=40 * i)).date(),
            valeur_quantitative=nb_participants,
            geom=random_point_near(commune)
        )
        interventions.append(intervention)

    print(f"  ✅ 8 concertations créées (R2.2): {sum(participants_rencontres)}/240 participants")

    # R3.1 - Périmètres maraîchers (cible: 8, réaliser: 5 = 62.5%)
    indicateur_r3_1 = next(i for i in indicateurs if i.code == 'R3.1')
    for i in range(5):
        commune = communes[i % len(communes)]
        intervention = Intervention.objects.create(
            projet=indicateur_r3_1.projet,
            indicateur=indicateur_r3_1,
            commune=commune,
            type_intervention=type_perimetre,
            libelle=f"Périmètre maraîcher - {commune.nom} #{(i % 2) + 1}",
            nature='REALISATION',
            statut='TERMINE',
            date_intervention=(start_date + timedelta(days=60 + 45 * i)).date(),
            valeur_quantitative=1,
            geom=random_point_near(commune, radius_km=3)
        )
        interventions.append(intervention)

    print(f"  ✅ 5 périmètres maraîchers créés (R3.1): 5/8")

    # R3.2 - Femmes bénéficiaires maraîchage (cible: 240, réaliser: 150 = 62.5%)
    indicateur_r3_2 = next(i for i in indicateurs if i.code == 'R3.2')
    for i in range(5):
        commune = communes[i % len(communes)]
        intervention = Intervention.objects.create(
            projet=indicateur_r3_2.projet,
            indicateur=indicateur_r3_2,
            commune=commune,
            type_intervention=type_perimetre,
            libelle=f"Groupement femmes - Périmètre {commune.nom}",
            nature='REALISATION',
            statut='TERMINE',
            date_intervention=(start_date + timedelta(days=60 + 45 * i)).date(),
            valeur_quantitative=30,  # 30 femmes par périmètre
            geom=random_point_near(commune, radius_km=3)
        )
        interventions.append(intervention)

    print(f"  ✅ 150 femmes bénéficiaires (R3.2): 150/240")

    # R3.3 - Réseaux AEP (cible: 8, réaliser: 5 = 62.5%)
    indicateur_r3_3 = next(i for i in indicateurs if i.code == 'R3.3')
    for i in range(5):
        commune = communes[i % len(communes)]
        intervention = Intervention.objects.create(
            projet=indicateur_r3_3.projet,
            indicateur=indicateur_r3_3,
            commune=commune,
            type_intervention=type_hydraulique,
            libelle=f"Réhabilitation réseau AEP - {commune.nom} #{(i % 2) + 1}",
            nature='REALISATION',
            statut='TERMINE',
            date_intervention=(start_date + timedelta(days=120 + 60 * i)).date(),
            valeur_quantitative=1,
            geom=random_point_near(commune, radius_km=1)
        )
        interventions.append(intervention)

    print(f"  ✅ 5 réseaux AEP créés (R3.3): 5/8")

    # R3.4 - Cantines scolaires (cible: 1200, réaliser: 800 = 66%)
    indicateur_r3_4 = next(i for i in indicateurs if i.code == 'R3.4')
    cantines = [
        {'nom': 'École de Gathiary', 'eleves': 220},
        {'nom': 'École de Toumboura', 'eleves': 200},
        {'nom': 'École de Médina Foulbé', 'eleves': 180},
        {'nom': 'École de Sadatou', 'eleves': 200},
    ]

    for i, data in enumerate(cantines):
        commune = communes[i]
        intervention = Intervention.objects.create(
            projet=indicateur_r3_4.projet,
            indicateur=indicateur_r3_4,
            commune=commune,
            type_intervention=type_cantine,
            libelle=f"Appui cantine - {data['nom']}",
            nature='REALISATION',
            statut='TERMINE',
            date_intervention=(start_date + timedelta(days=150 + 30 * i)).date(),
            valeur_quantitative=data['eleves'],
            geom=random_point_near(commune, radius_km=1.5)
        )
        interventions.append(intervention)

    print(f"  ✅ 4 cantines scolaires créées (R3.4): {sum([c['eleves'] for c in cantines])}/1200 élèves")

    # R3.5 - Postes de santé (cible: 4, réaliser: 3 = 75%)
    indicateur_r3_5 = next(i for i in indicateurs if i.code == 'R3.5')
    for i in range(3):
        commune = communes[i]
        intervention = Intervention.objects.create(
            projet=indicateur_r3_5.projet,
            indicateur=indicateur_r3_5,
            commune=commune,
            type_intervention=type_sante,
            libelle=f"Équipement poste de santé - {commune.nom}",
            nature='REALISATION',
            statut='TERMINE',
            date_intervention=(start_date + timedelta(days=180 + 60 * i)).date(),
            valeur_quantitative=1,
            geom=random_point_near(commune, radius_km=0.5)
        )
        interventions.append(intervention)

    print(f"  ✅ 3 postes de santé équipés (R3.5): 3/4")

    print(f"\n✅ Total : {len(interventions)} interventions créées")
    return interventions


def main():
    """Fonction principale"""
    print("="*80)
    print("🚀 GÉNÉRATION DONNÉES DÉMO V2 - PROJET JAMM LEYDI")
    print("="*80)

    response = input("\n⚠️  Supprimer le projet JAMM-LEYDI-V2 s'il existe ? (oui/non) : ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        return

    clear_existing_data()

    # Récupérer l'équipe GRDR existante
    equipe_grdr = EquipeGRDR.objects.get(code='GRDR-SN-BAKEL')
    print(f"\n👥 Équipe GRDR : {equipe_grdr.nom}")

    # Récupérer les communes existantes
    communes = list(Commune.objects.filter(
        code_commune__in=['SN-KEN-GATH', 'SN-KEN-TOUM', 'SN-KEN-MEDF', 'SN-KEN-SADA']
    ).order_by('nom'))
    print(f"🏘️  Communes : {', '.join([c.nom for c in communes])}")

    # Créer le projet
    projet = create_projet(equipe_grdr, communes)

    # Créer les données
    thematiques = create_thematiques(projet)
    indicateurs = create_indicateurs_realistes(thematiques, communes)

    # Récupérer les types existants
    types_intervention = list(TypeIntervention.objects.all())

    interventions = create_interventions_realistes(types_intervention, indicateurs, communes)

    # Résumé
    print("\n" + "="*80)
    print("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS !")
    print("="*80)
    print(f"""
    📊 Résumé des données créées pour JAMM LEYDI V2 :

    - 1 projet : {projet.code_projet}
    - {len(communes)} communes
    - {len(thematiques)} thématiques
    - {len(indicateurs)} indicateurs
    - {len(interventions)} interventions

    🎯 Avancement global attendu : ~66%

    🌐 Accédez au dashboard et sélectionnez "JAMM LEYDI V2"
    """)
    print("="*80)


if __name__ == '__main__':
    main()
