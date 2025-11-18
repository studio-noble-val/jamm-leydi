# -*- coding: utf-8 -*-
"""
Script de génération de données de démonstration V3 pour le projet JAMM LEYDI
Données ultra-réalistes avec :
- Interventions programmées (100% des cibles)
- Interventions terminées (avancement variable par thématique)
- R1 : 75% (en avance)
- R2 : 50% (mi-parcours)
- R3 : 40% (en retard)
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
from core.models import Projet
from referentiels.models import Commune, ProjetCommune, TypeIntervention, EquipeGRDR
from suivi.models import Thematique, Indicateur, CibleIndicateur, Intervention


def clear_existing_data():
    """Supprime les données du projet JAMM LEYDI V3"""
    print("🗑️  Suppression des données existantes...")

    Intervention.objects.filter(projet__code_projet='JAMM-LEYDI-V3').delete()
    CibleIndicateur.objects.filter(indicateur__projet__code_projet='JAMM-LEYDI-V3').delete()
    Indicateur.objects.filter(projet__code_projet='JAMM-LEYDI-V3').delete()
    Thematique.objects.filter(projet__code_projet='JAMM-LEYDI-V3').delete()
    Projet.objects.filter(code_projet='JAMM-LEYDI-V3').delete()

    print("✅ Données existantes supprimées")


def create_projet(equipe_grdr, communes):
    """Crée le projet JAMM LEYDI V3"""
    print("\n📋 Création du projet JAMM LEYDI V3...")

    projet = Projet.objects.create(
        code_projet='JAMM-LEYDI-V3',
        libelle='JAMM LEYDI V3 - Situation Réaliste',
        description="""
        Projet avec planification complète et avancement réaliste :
        - R1 : 75% (en avance)
        - R2 : 50% (mi-parcours)
        - R3 : 40% (en retard)
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

    for commune in communes:
        ProjetCommune.objects.create(projet=projet, commune=commune, prioritaire=True)

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
        print(f"  ✅ Thématique créée : {thematique.code}")

    return thematiques


def create_indicateurs(thematiques, communes):
    """Crée les indicateurs"""
    print("\n📊 Création des indicateurs...")

    r1 = next(t for t in thematiques if t.code == 'R1')
    r2 = next(t for t in thematiques if t.code == 'R2')
    r3 = next(t for t in thematiques if t.code == 'R3')

    indicateurs_data = [
        # R1
        {'thematique': r1, 'code': 'R1.1', 'libelle': 'Nombre de participants aux formations', 'unite': 'Personnes', 'cible': 300},
        {'thematique': r1, 'code': 'R1.2', 'libelle': 'Nombre d\'organisations renforcées', 'unite': 'Organisations', 'cible': 15},
        # R2
        {'thematique': r2, 'code': 'R2.1', 'libelle': 'Nombre de rencontres intercommunales', 'unite': 'Rencontres', 'cible': 12},
        {'thematique': r2, 'code': 'R2.2', 'libelle': 'Nombre de participants aux rencontres', 'unite': 'Personnes', 'cible': 240},
        # R3
        {'thematique': r3, 'code': 'R3.1', 'libelle': 'Nombre de périmètres maraîchers aménagés', 'unite': 'Périmètres', 'cible': 8},
        {'thematique': r3, 'code': 'R3.2', 'libelle': 'Nombre de femmes bénéficiaires (maraîchage)', 'unite': 'Femmes', 'cible': 240},
        {'thematique': r3, 'code': 'R3.3', 'libelle': 'Nombre de réseaux AEP réhabilités', 'unite': 'Réseaux', 'cible': 8},
        {'thematique': r3, 'code': 'R3.4', 'libelle': 'Nombre d\'élèves bénéficiant de cantines', 'unite': 'Élèves', 'cible': 1200},
        {'thematique': r3, 'code': 'R3.5', 'libelle': 'Nombre de postes de santé équipés', 'unite': 'Postes', 'cible': 4},
    ]

    indicateurs = []
    for i, data in enumerate(indicateurs_data):
        indicateur = Indicateur.objects.create(
            projet=data['thematique'].projet,
            thematique=data['thematique'],
            code=data['code'],
            libelle=data['libelle'],
            unite_mesure=data['unite'],
            type_calcul='SOMME',
            ordre=i + 1
        )

        # Créer les cibles par commune
        for commune in communes:
            total_pop = sum(c.population for c in communes)
            ratio = commune.population / total_pop
            cible_commune = int(data['cible'] * ratio)

            for annee in [2024, 2025, 2026]:
                CibleIndicateur.objects.create(
                    indicateur=indicateur,
                    commune=commune,
                    annee=annee,
                    valeur_cible=cible_commune
                )

        indicateurs.append(indicateur)
        print(f"  ✅ {indicateur.code} - Cible: {data['cible']} {data['unite']}")

    return indicateurs


def create_interventions_programmees_et_terminees(types_intervention, indicateurs, communes):
    """
    Crée des interventions pour atteindre 100% des cibles
    Marque certaines comme TERMINE selon l'avancement souhaité :
    - R1 : 75% terminé
    - R2 : 50% terminé
    - R3 : 40% terminé
    """
    print("\n🗺️  Création des interventions (PROGRAMME + TERMINE)...")

    interventions = []
    start_date = datetime(2024, 1, 1)
    now = datetime.now()

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

    print("\n  === R1 : Renforcement des capacités (Cible: 75%) ===")

    # R1.1 - Formations (cible: 300, terminer: 225 = 75%)
    indicateur_r1_1 = next(i for i in indicateurs if i.code == 'R1.1')
    formations = [
        {'titre': 'Formation adaptation changement climatique', 'participants': 50, 'termine': True},
        {'titre': 'Atelier prévention des conflits', 'participants': 45, 'termine': True},
        {'titre': 'Formation gestion ressources naturelles', 'participants': 40, 'termine': True},
        {'titre': 'Atelier de co-actualisation des plans', 'participants': 45, 'termine': True},
        {'titre': 'Formation des relais communautaires', 'participants': 45, 'termine': True},
        {'titre': 'Atelier gouvernance locale', 'participants': 40, 'termine': False},  # Programmée
        {'titre': 'Formation suivi-évaluation participatif', 'participants': 35, 'termine': False},  # Programmée
    ]

    termine_count = sum([1 for f in formations if f['termine']])
    total_participants_termine = sum([f['participants'] for f in formations if f['termine']])

    for i, data in enumerate(formations):
        commune = communes[i % len(communes)]
        date_intervention = start_date + timedelta(days=30 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r1_1.projet,
            indicateur=indicateur_r1_1,
            commune=commune,
            type_intervention=type_rencontre,
            libelle=data['titre'],
            nature='ACTIVITE',
            statut='TERMINE' if data['termine'] else 'PROGRAMME',
            date_intervention=date_intervention.date() if data['termine'] else (now + timedelta(days=30 * (i - termine_count + 1))).date(),
            valeur_quantitative=data['participants'],
            geom=random_point_near(commune)
        )
        interventions.append(intervention)

    print(f"  ✅ R1.1 Formations: {total_participants_termine}/300 participants ({(total_participants_termine/300*100):.0f}%)")

    # R1.2 - Organisations (cible: 15, terminer: 11 = 73%)
    indicateur_r1_2 = next(i for i in indicateurs if i.code == 'R1.2')
    for i in range(15):
        commune = communes[i % len(communes)]
        termine = i < 11  # Les 11 premières sont terminées
        date_intervention = start_date + timedelta(days=45 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r1_2.projet,
            indicateur=indicateur_r1_2,
            commune=commune,
            type_intervention=type_rencontre,
            libelle=f"Appui organisation - {commune.nom} #{(i % 3) + 1}",
            nature='ACTIVITE',
            statut='TERMINE' if termine else 'PROGRAMME',
            date_intervention=date_intervention.date() if termine else (now + timedelta(days=30 * (i - 11 + 1))).date(),
            valeur_quantitative=1,
            geom=random_point_near(commune)
        )
        interventions.append(intervention)

    print(f"  ✅ R1.2 Organisations: 11/15 ({(11/15*100):.0f}%)")

    print("\n  === R2 : Cohésion sociale (Cible: 50%) ===")

    # R2.1 - Rencontres (cible: 12, terminer: 6 = 50%)
    indicateur_r2_1 = next(i for i in indicateurs if i.code == 'R2.1')
    for i in range(12):
        commune = communes[i % len(communes)]
        termine = i < 6
        date_intervention = start_date + timedelta(days=40 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r2_1.projet,
            indicateur=indicateur_r2_1,
            commune=commune,
            type_intervention=type_rencontre,
            libelle=f"Rencontre intercommunale #{i+1}",
            nature='ACTIVITE',
            statut='TERMINE' if termine else 'PROGRAMME',
            date_intervention=date_intervention.date() if termine else (now + timedelta(days=40 * (i - 6 + 1))).date(),
            valeur_quantitative=1,
            geom=random_point_near(commune)
        )
        interventions.append(intervention)

    print(f"  ✅ R2.1 Rencontres: 6/12 (50%)")

    # R2.2 - Participants (cible: 240, terminer: 120 = 50%)
    indicateur_r2_2 = next(i for i in indicateurs if i.code == 'R2.2')
    participants_data = [
        {'nb': 22, 'termine': True}, {'nb': 18, 'termine': True}, {'nb': 25, 'termine': True},
        {'nb': 19, 'termine': True}, {'nb': 21, 'termine': True}, {'nb': 15, 'termine': True},
        {'nb': 20, 'termine': False}, {'nb': 18, 'termine': False}, {'nb': 22, 'termine': False},
        {'nb': 20, 'termine': False}, {'nb': 20, 'termine': False}, {'nb': 20, 'termine': False},
    ]

    termine_participants = sum([p['nb'] for p in participants_data if p['termine']])
    termine_count_r2 = sum([1 for p in participants_data if p['termine']])

    for i, data in enumerate(participants_data):
        commune = communes[i % len(communes)]
        date_intervention = start_date + timedelta(days=40 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r2_2.projet,
            indicateur=indicateur_r2_2,
            commune=commune,
            type_intervention=type_rencontre,
            libelle=f"Concertation gestion ressources - {commune.nom} #{(i % 3) + 1}",
            nature='ACTIVITE',
            statut='TERMINE' if data['termine'] else 'PROGRAMME',
            date_intervention=date_intervention.date() if data['termine'] else (now + timedelta(days=40 * (i - termine_count_r2 + 1))).date(),
            valeur_quantitative=data['nb'],
            geom=random_point_near(commune)
        )
        interventions.append(intervention)

    print(f"  ✅ R2.2 Participants: {termine_participants}/240 ({(termine_participants/240*100):.0f}%)")

    print("\n  === R3 : Résilience et services (Cible: 40%) ===")

    # R3.1 - Périmètres (cible: 8, terminer: 3 = 37.5%)
    indicateur_r3_1 = next(i for i in indicateurs if i.code == 'R3.1')
    for i in range(8):
        commune = communes[i % len(communes)]
        termine = i < 3
        date_intervention = start_date + timedelta(days=60 + 45 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r3_1.projet,
            indicateur=indicateur_r3_1,
            commune=commune,
            type_intervention=type_perimetre,
            libelle=f"Périmètre maraîcher - {commune.nom} #{(i % 2) + 1}",
            nature='REALISATION',
            statut='TERMINE' if termine else 'PROGRAMME',
            date_intervention=date_intervention.date() if termine else (now + timedelta(days=60 + 45 * (i - 3 + 1))).date(),
            valeur_quantitative=1,
            geom=random_point_near(commune, radius_km=3)
        )
        interventions.append(intervention)

    print(f"  ✅ R3.1 Périmètres: 3/8 (38%)")

    # R3.2 - Femmes bénéficiaires (cible: 240, terminer: 90 = 37.5%)
    indicateur_r3_2 = next(i for i in indicateurs if i.code == 'R3.2')
    for i in range(8):
        commune = communes[i % len(communes)]
        termine = i < 3
        date_intervention = start_date + timedelta(days=60 + 45 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r3_2.projet,
            indicateur=indicateur_r3_2,
            commune=commune,
            type_intervention=type_perimetre,
            libelle=f"Groupement femmes - Périmètre {commune.nom} #{(i % 2) + 1}",
            nature='REALISATION',
            statut='TERMINE' if termine else 'PROGRAMME',
            date_intervention=date_intervention.date() if termine else (now + timedelta(days=60 + 45 * (i - 3 + 1))).date(),
            valeur_quantitative=30,
            geom=random_point_near(commune, radius_km=3)
        )
        interventions.append(intervention)

    print(f"  ✅ R3.2 Femmes: 90/240 (38%)")

    # R3.3 - Réseaux AEP (cible: 8, terminer: 3 = 37.5%)
    indicateur_r3_3 = next(i for i in indicateurs if i.code == 'R3.3')
    for i in range(8):
        commune = communes[i % len(communes)]
        termine = i < 3
        date_intervention = start_date + timedelta(days=120 + 60 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r3_3.projet,
            indicateur=indicateur_r3_3,
            commune=commune,
            type_intervention=type_hydraulique,
            libelle=f"Réhabilitation réseau AEP - {commune.nom} #{(i % 2) + 1}",
            nature='REALISATION',
            statut='TERMINE' if termine else 'PROGRAMME',
            date_intervention=date_intervention.date() if termine else (now + timedelta(days=120 + 60 * (i - 3 + 1))).date(),
            valeur_quantitative=1,
            geom=random_point_near(commune, radius_km=1)
        )
        interventions.append(intervention)

    print(f"  ✅ R3.3 Réseaux AEP: 3/8 (38%)")

    # R3.4 - Cantines (cible: 1200, terminer: 500 = 42%)
    indicateur_r3_4 = next(i for i in indicateurs if i.code == 'R3.4')
    cantines = [
        {'nom': 'École de Gathiary Centre', 'eleves': 180, 'termine': True},
        {'nom': 'École de Toumboura Village', 'eleves': 160, 'termine': True},
        {'nom': 'École de Médina Foulbé', 'eleves': 160, 'termine': True},
        {'nom': 'École de Sadatou', 'eleves': 200, 'termine': False},
        {'nom': 'École de Gathiary Ouest', 'eleves': 150, 'termine': False},
        {'nom': 'École de Toumboura Nord', 'eleves': 170, 'termine': False},
        {'nom': 'École rurale Médina', 'eleves': 90, 'termine': False},
        {'nom': 'École rurale Sadatou', 'eleves': 90, 'termine': False},
    ]

    termine_eleves = sum([c['eleves'] for c in cantines if c['termine']])
    termine_count_cantines = sum([1 for c in cantines if c['termine']])

    for i, data in enumerate(cantines):
        commune = communes[i % len(communes)]
        date_intervention = start_date + timedelta(days=150 + 30 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r3_4.projet,
            indicateur=indicateur_r3_4,
            commune=commune,
            type_intervention=type_cantine,
            libelle=f"Appui cantine - {data['nom']}",
            nature='REALISATION',
            statut='TERMINE' if data['termine'] else 'PROGRAMME',
            date_intervention=date_intervention.date() if data['termine'] else (now + timedelta(days=30 * (i - termine_count_cantines + 1))).date(),
            valeur_quantitative=data['eleves'],
            geom=random_point_near(commune, radius_km=1.5)
        )
        interventions.append(intervention)

    print(f"  ✅ R3.4 Cantines: {termine_eleves}/1200 élèves ({(termine_eleves/1200*100):.0f}%)")

    # R3.5 - Postes de santé (cible: 4, terminer: 2 = 50%)
    indicateur_r3_5 = next(i for i in indicateurs if i.code == 'R3.5')
    for i in range(4):
        commune = communes[i]
        termine = i < 2
        date_intervention = start_date + timedelta(days=180 + 60 * i)

        intervention = Intervention.objects.create(
            projet=indicateur_r3_5.projet,
            indicateur=indicateur_r3_5,
            commune=commune,
            type_intervention=type_sante,
            libelle=f"Équipement poste de santé - {commune.nom}",
            nature='REALISATION',
            statut='TERMINE' if termine else 'PROGRAMME',
            date_intervention=date_intervention.date() if termine else (now + timedelta(days=60 * (i - 2 + 1))).date(),
            valeur_quantitative=1,
            geom=random_point_near(commune, radius_km=0.5)
        )
        interventions.append(intervention)

    print(f"  ✅ R3.5 Postes santé: 2/4 (50%)")

    termine_total = len([i for i in interventions if i.statut == 'TERMINE'])
    programme_total = len([i for i in interventions if i.statut == 'PROGRAMME'])

    print(f"\n✅ Total : {len(interventions)} interventions créées")
    print(f"   - {termine_total} TERMINÉES")
    print(f"   - {programme_total} PROGRAMMÉES")

    return interventions


def main():
    """Fonction principale"""
    print("="*80)
    print("🚀 GÉNÉRATION DONNÉES DÉMO V3 - JAMM LEYDI")
    print("="*80)

    response = input("\n⚠️  Supprimer JAMM-LEYDI-V3 s'il existe ? (oui/non) : ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        return

    clear_existing_data()

    equipe_grdr = EquipeGRDR.objects.get(code='GRDR-SN-BAKEL')
    communes = list(Commune.objects.filter(
        code_commune__in=['SN-KEN-GATH', 'SN-KEN-TOUM', 'SN-KEN-MEDF', 'SN-KEN-SADA']
    ).order_by('nom'))

    projet = create_projet(equipe_grdr, communes)
    thematiques = create_thematiques(projet)
    indicateurs = create_indicateurs(thematiques, communes)
    types_intervention = list(TypeIntervention.objects.all())
    interventions = create_interventions_programmees_et_terminees(types_intervention, indicateurs, communes)

    print("\n" + "="*80)
    print("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS !")
    print("="*80)
    print(f"""
    📊 Résumé JAMM LEYDI V3 :

    - 3 thématiques
    - 9 indicateurs
    - {len(interventions)} interventions
      → {len([i for i in interventions if i.statut == 'TERMINE'])} terminées
      → {len([i for i in interventions if i.statut == 'PROGRAMME'])} programmées

    🎯 Avancements attendus :
      - R1 : ~75% (en avance)
      - R2 : ~50% (mi-parcours)
      - R3 : ~40% (en retard)

    🌐 Sélectionnez "JAMM LEYDI V3" dans le dashboard
    """)
    print("="*80)


if __name__ == '__main__':
    main()
