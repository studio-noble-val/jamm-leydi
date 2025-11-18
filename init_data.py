#!/usr/bin/env python
"""
Script d'initialisation des données de base pour JAMM LEYDI - Architecture V2
Crée : Projet, Communes, Thématiques, Indicateurs, Types
"""
import os
import django
from datetime import date
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamm_leydi.settings')
django.setup()

from core.models import User, Projet, UserProjet
from referentiels.models import (
    Commune, ProjetCommune, TypeIntervention,
    TypeInfrastructure, TypeActeur
)
from suivi.models import Thematique, Indicateur, CibleIndicateur
from securite.models import TypeInsecurite


def create_superuser():
    """Créer un superutilisateur"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@jammleydi.org',
            password='admin123',
            telephone='+221 77 123 45 67',
            organisation='GRDR'
        )
        print("OK Superutilisateur créé (admin/admin123)")
    else:
        print("OK Superutilisateur existe déjà")

    return User.objects.get(username='admin')


def create_projet(admin_user):
    """Créer le projet JAMM LEYDI"""
    projet, created = Projet.objects.get_or_create(
        code_projet='JAMM-LEYDI-2024',
        defaults={
            'libelle': 'JAMM LEYDI - Prévention des conflits liés au changement climatique',
            'description': (
                "Projet de prévention des conflits liés au changement climatique "
                "dans l'arrondissement de Kéniéba. Interventions dans 4 communes "
                "pour 14 700 bénéficiaires ciblés."
            ),
            'pays': 'Sénégal',
            'equipe_grdr': 'Antenne Sénégal - Kédougou',
            'bailleurs': 'Union Européenne',
            'zone_intervention': 'Arrondissement de Kéniéba, Région de Kédougou, Sénégal',
            'date_debut': date(2024, 1, 1),
            'date_fin': date(2026, 12, 31),
            'budget': Decimal('2500000.00'),
            'devise': 'EUR',
            'statut': 'EN_COURS',
            'actif': True,
        }
    )

    if created:
        print(f"OK Projet créé : {projet.code_projet}")
    else:
        print(f"OK Projet existe : {projet.code_projet}")

    # Lier l'admin au projet avec rôle ADMIN_PROJET
    user_projet, created = UserProjet.objects.get_or_create(
        user=admin_user,
        projet=projet,
        defaults={
            'role': 'ADMIN_PROJET',
            'actif': True,
        }
    )

    if created:
        print(f"  OK Admin assigné au projet avec rôle ADMIN_PROJET")

    return projet


def create_communes(projet):
    """Créer les 4 communes de l'arrondissement de Kéniéba"""
    communes_data = [
        {
            'nom': 'Gathiary',
            'code_commune': 'SN-KD-KEN-GAT',
            'departement': 'Kédougou',
            'region': 'Kédougou',
            'population': 8500,
            'annee_recensement': 2023,
        },
        {
            'nom': 'Toumboura',
            'code_commune': 'SN-KD-KEN-TOU',
            'departement': 'Kédougou',
            'region': 'Kédougou',
            'population': 6200,
            'annee_recensement': 2023,
        },
        {
            'nom': 'Médina Foulbé',
            'code_commune': 'SN-KD-KEN-MED',
            'departement': 'Kédougou',
            'region': 'Kédougou',
            'population': 4800,
            'annee_recensement': 2023,
        },
        {
            'nom': 'Sadatou',
            'code_commune': 'SN-KD-KEN-SAD',
            'departement': 'Kédougou',
            'region': 'Kédougou',
            'population': 5300,
            'annee_recensement': 2023,
        },
    ]

    communes_creees = []

    for data in communes_data:
        commune, created = Commune.objects.get_or_create(
            code_commune=data['code_commune'],
            defaults=data
        )

        if created:
            print(f"OK Commune créée : {commune.nom}")
        else:
            print(f"OK Commune existe : {commune.nom}")

        # Lier la commune au projet
        projet_commune, pc_created = ProjetCommune.objects.get_or_create(
            projet=projet,
            commune=commune,
            defaults={'prioritaire': True}
        )

        if pc_created:
            print(f"  OK Commune liée au projet")

        communes_creees.append(commune)

    return communes_creees


def create_thematiques(projet):
    """Créer les 3 thématiques (R1, R2, R3)"""
    thematiques_data = [
        {
            'code': 'R1',
            'libelle': 'Renforcement des capacités locales de prévention des conflits',
            'description': (
                "Renforcement des capacités des acteurs locaux (collectivités, OSC) "
                "pour la prévention et la gestion des conflits liés au changement climatique."
            ),
            'ordre': 1,
        },
        {
            'code': 'R2',
            'libelle': 'Amélioration de la cohésion sociale et de la gouvernance locale',
            'description': (
                "Soutien aux dynamiques de cohésion sociale et amélioration de la "
                "gouvernance locale pour une meilleure gestion concertée des ressources."
            ),
            'ordre': 2,
        },
        {
            'code': 'R3',
            'libelle': 'Solutions locales pour l\'amélioration de la résilience',
            'description': (
                "Mise en œuvre de solutions locales concrètes pour améliorer la résilience "
                "des populations face aux effets du changement climatique."
            ),
            'ordre': 3,
        },
    ]

    thematiques_creees = []

    for data in thematiques_data:
        thematique, created = Thematique.objects.get_or_create(
            projet=projet,
            code=data['code'],
            defaults={
                'libelle': data['libelle'],
                'description': data['description'],
                'ordre': data['ordre'],
            }
        )

        if created:
            print(f"OK Thématique créée : {thematique.code} - {thematique.libelle}")
        else:
            print(f"OK Thématique existe : {thematique.code}")

        thematiques_creees.append(thematique)

    return thematiques_creees


def create_indicateurs(thematiques):
    """Créer les indicateurs du cadre logique avec leurs cibles"""
    # Récupérer les thématiques
    r1, r2, r3 = thematiques

    indicateurs_data = [
        # Indicateurs R1
        {
            'thematique': r1,
            'code': 'R1.1',
            'libelle': 'Nombre de participants à la co-actualisation des plans d\'actions locales',
            'description': 'Participants aux ateliers de co-actualisation des PAL dans les 4 communes',
            'unite_mesure': 'Personnes',
            'type_calcul': 'SOMME',
            'ordre': 1,
            'cible': 60,
        },
        {
            'thematique': r1,
            'code': 'R1.2',
            'libelle': 'Nombre d\'entités formées ou soutenues pour la prévention',
            'description': 'Collectivités locales, OSC et acteurs locaux formés ou soutenus',
            'unite_mesure': 'Entités',
            'type_calcul': 'DENOMBREMENT',
            'ordre': 2,
            'cible': 80,
        },
        {
            'thematique': r1,
            'code': 'R1.3',
            'libelle': 'Nombre de structures bénéficiaires agissant pour la prévention',
            'description': '4 conseils municipaux, 10 OSC, 1 cadre de concertation',
            'unite_mesure': 'Structures',
            'type_calcul': 'DENOMBREMENT',
            'ordre': 3,
            'cible': 15,
        },
        # Indicateurs R2
        {
            'thematique': r2,
            'code': 'R2.1',
            'libelle': 'Nombre d\'entités/réseaux soutenus ou formés',
            'description': 'Réseaux d\'acteurs locaux soutenus pour améliorer la cohésion sociale',
            'unite_mesure': 'Entités',
            'type_calcul': 'DENOMBREMENT',
            'ordre': 1,
            'cible': 10,
        },
        {
            'thematique': r2,
            'code': 'R2.2',
            'libelle': 'Nombre de personnes formées ayant amélioré leurs compétences',
            'description': 'Personnes ayant participé aux formations et amélioré leurs compétences',
            'unite_mesure': 'Personnes',
            'type_calcul': 'SOMME',
            'ordre': 2,
            'cible': 250,
        },
        {
            'thematique': r2,
            'code': 'R2.3',
            'libelle': 'Nombre de personnes bénéficiant directement des interventions',
            'description': 'Bénéficiaires directs de l\'ensemble des actions du projet',
            'unite_mesure': 'Personnes',
            'type_calcul': 'SOMME',
            'ordre': 3,
            'cible': 14700,
        },
        # Indicateurs R3
        {
            'thematique': r3,
            'code': 'R3.1',
            'libelle': 'Nombre de communes avec PDC intégrant la prévention des conflits',
            'description': 'Plans de Développement Communaux actualisés avec volet prévention',
            'unite_mesure': 'Communes',
            'type_calcul': 'DENOMBREMENT',
            'ordre': 1,
            'cible': 4,
        },
        {
            'thematique': r3,
            'code': 'R3.2',
            'libelle': 'Nombre d\'initiatives économiques mises en œuvre',
            'description': 'Initiatives économiques soutenues (AGR, micro-entreprises, etc.)',
            'unite_mesure': 'Initiatives',
            'type_calcul': 'DENOMBREMENT',
            'ordre': 2,
            'cible': 20,
        },
        {
            'thematique': r3,
            'code': 'R3.3',
            'libelle': 'Nombre de réseaux AEP réhabilités/construits',
            'description': 'Réseaux d\'Adduction d\'Eau Potable réhabilités ou construits',
            'unite_mesure': 'Réseaux',
            'type_calcul': 'DENOMBREMENT',
            'ordre': 3,
            'cible': 8,
        },
        {
            'thematique': r3,
            'code': 'R3.4',
            'libelle': 'Nombre d\'élèves ayant accès à des repas scolaires',
            'description': 'Élèves bénéficiant de cantines scolaires fonctionnelles',
            'unite_mesure': 'Élèves',
            'type_calcul': 'SOMME',
            'ordre': 4,
            'cible': 1200,
        },
        {
            'thematique': r3,
            'code': 'R3.5',
            'libelle': 'Nombre de postes de santé réhabilités',
            'description': 'Postes de santé réhabilités et équipés',
            'unite_mesure': 'Postes',
            'type_calcul': 'DENOMBREMENT',
            'ordre': 5,
            'cible': 5,
        },
        {
            'thematique': r3,
            'code': 'R3.6',
            'libelle': 'Perception du niveau de sécurité par les habitants',
            'description': 'Pourcentage d\'habitants percevant une amélioration de la sécurité',
            'unite_mesure': '% d\'amélioration',
            'type_calcul': 'MANUEL',
            'ordre': 6,
            'cible': 33,  # Au moins 1/3 des habitants
        },
    ]

    for data in indicateurs_data:
        thematique = data.pop('thematique')
        cible_valeur = data.pop('cible')

        indicateur, created = Indicateur.objects.get_or_create(
            projet=thematique.projet,
            code=data['code'],
            defaults={
                'thematique': thematique,
                **data
            }
        )

        if created:
            print(f"OK Indicateur créé : {indicateur.code} - {indicateur.libelle[:50]}...")
        else:
            print(f"OK Indicateur existe : {indicateur.code}")

        # Créer la cible globale (sans commune spécifique) pour 2025 et 2026
        for annee in [2025, 2026]:
            cible, cible_created = CibleIndicateur.objects.get_or_create(
                indicateur=indicateur,
                commune=None,  # Cible globale
                annee=annee,
                defaults={'valeur_cible': cible_valeur}
            )

            if cible_created:
                print(f"  OK Cible créée pour {annee} : {cible_valeur}")


def create_types_interventions():
    """Créer les 6 types d'interventions"""
    types_data = [
        {
            'libelle': 'Rencontres et Événements',
            'code': 'RENCONTRES',
            'description': 'Ateliers, réunions, événements de sensibilisation (R1 & R2)',
            'couleur_hex': '#3498db',  # Bleu
            'actif': True,
        },
        {
            'libelle': 'Activités Agro-sylvo-pastorales',
            'code': 'AGRO',
            'description': 'Périmètres maraîchers, mares pastorales, aménagements agricoles (R3.1)',
            'couleur_hex': '#2ecc71',  # Vert
            'actif': True,
        },
        {
            'libelle': 'Initiatives Économiques',
            'code': 'ECO',
            'description': 'Entreprises, AGR, micro-finances (R3.2)',
            'couleur_hex': '#f39c12',  # Orange
            'actif': True,
        },
        {
            'libelle': 'Infrastructures Hydrauliques',
            'code': 'HYDRO',
            'description': 'Réseaux AEP, forages, puits (R3.3)',
            'couleur_hex': '#3498db',  # Bleu clair
            'actif': True,
        },
        {
            'libelle': 'Cantines Scolaires',
            'code': 'CANTINES',
            'description': 'Construction et équipement de cantines scolaires (R3.4)',
            'couleur_hex': '#e74c3c',  # Rouge
            'actif': True,
        },
        {
            'libelle': 'Postes de Santé',
            'code': 'SANTE',
            'description': 'Réhabilitation et équipement de postes de santé (R3.5)',
            'couleur_hex': '#9b59b6',  # Violet
            'actif': True,
        },
    ]

    for data in types_data:
        type_intervention, created = TypeIntervention.objects.get_or_create(
            code=data['code'],
            defaults=data
        )

        if created:
            print(f"OK Type d'intervention créé : {type_intervention.libelle}")
        else:
            print(f"OK Type d'intervention existe : {type_intervention.libelle}")


def create_types_infrastructures():
    """Créer les types d'infrastructures"""
    types_data = [
        {
            'libelle': 'Forage',
            'code': 'FORAGE',
            'description': 'Forage avec pompe solaire ou manuelle',
            'icone_poi': 'tint',
            'couleur_hex': '#3498db',
        },
        {
            'libelle': 'Réseau AEP',
            'code': 'AEP',
            'description': 'Réseau d\'Adduction d\'Eau Potable',
            'icone_poi': 'water',
            'couleur_hex': '#2980b9',
        },
        {
            'libelle': 'Périmètre maraîcher',
            'code': 'MARAICHAGE',
            'description': 'Périmètre agricole aménagé et irrigué',
            'icone_poi': 'leaf',
            'couleur_hex': '#27ae60',
        },
        {
            'libelle': 'Mare pastorale',
            'code': 'MARE',
            'description': 'Mare aménagée pour l\'abreuvement du bétail',
            'icone_poi': 'tint',
            'couleur_hex': '#16a085',
        },
        {
            'libelle': 'Cantine scolaire',
            'code': 'CANTINE',
            'description': 'Cantine scolaire équipée',
            'icone_poi': 'utensils',
            'couleur_hex': '#e67e22',
        },
        {
            'libelle': 'Poste de santé',
            'code': 'SANTE',
            'description': 'Poste de santé réhabilité et équipé',
            'icone_poi': 'hospital',
            'couleur_hex': '#e74c3c',
        },
        {
            'libelle': 'École',
            'code': 'ECOLE',
            'description': 'École primaire ou secondaire',
            'icone_poi': 'graduation-cap',
            'couleur_hex': '#9b59b6',
        },
        {
            'libelle': 'Magasin de stockage',
            'code': 'MAGASIN',
            'description': 'Magasin de stockage des récoltes',
            'icone_poi': 'warehouse',
            'couleur_hex': '#95a5a6',
        },
    ]

    for data in types_data:
        type_infra, created = TypeInfrastructure.objects.get_or_create(
            code=data['code'],
            defaults=data
        )

        if created:
            print(f"OK Type d'infrastructure créé : {type_infra.libelle}")
        else:
            print(f"OK Type d'infrastructure existe : {type_infra.libelle}")


def create_types_acteurs():
    """Créer les types d'acteurs"""
    types_data = [
        {
            'libelle': 'Groupement féminin',
            'code': 'GF',
            'description': 'Groupement de femmes pour activités économiques',
            'icone_poi': 'female',
            'couleur_hex': '#e91e63',
        },
        {
            'libelle': 'Association d\'éleveurs',
            'code': 'ELEVEURS',
            'description': 'Association pour la gestion du bétail',
            'icone_poi': 'paw',
            'couleur_hex': '#795548',
        },
        {
            'libelle': 'Coopérative agricole',
            'code': 'COOP_AGRI',
            'description': 'Coopérative pour la production agricole',
            'icone_poi': 'seedling',
            'couleur_hex': '#4caf50',
        },
        {
            'libelle': 'Comité de gestion',
            'code': 'COMITE',
            'description': 'Comité de gestion d\'infrastructure (eau, école, etc.)',
            'icone_poi': 'users-cog',
            'couleur_hex': '#607d8b',
        },
        {
            'libelle': 'Organisation de la Société Civile',
            'code': 'OSC',
            'description': 'OSC locale intervenant dans le développement',
            'icone_poi': 'hands-helping',
            'couleur_hex': '#ff9800',
        },
        {
            'libelle': 'Conseil Municipal',
            'code': 'CM',
            'description': 'Conseil Municipal de la commune',
            'icone_poi': 'landmark',
            'couleur_hex': '#3f51b5',
        },
    ]

    for data in types_data:
        type_acteur, created = TypeActeur.objects.get_or_create(
            code=data['code'],
            defaults=data
        )

        if created:
            print(f"OK Type d'acteur créé : {type_acteur.libelle}")
        else:
            print(f"OK Type d'acteur existe : {type_acteur.libelle}")


def create_types_insecurite():
    """Créer les types d'insécurité"""
    types_data = [
        {
            'libelle': 'Conflit foncier',
            'code': 'FONCIER',
            'description': 'Conflit lié à l\'accès ou la propriété de terres',
            'couleur_hex': '#e74c3c',
        },
        {
            'libelle': 'Vol de bétail',
            'code': 'VOL_BETAIL',
            'description': 'Vol ou divagation de bétail',
            'couleur_hex': '#e67e22',
        },
        {
            'libelle': 'Conflit autour de l\'eau',
            'code': 'EAU',
            'description': 'Conflit lié à l\'accès aux ressources en eau',
            'couleur_hex': '#3498db',
        },
        {
            'libelle': 'Tensions intercommunautaires',
            'code': 'TENSIONS',
            'description': 'Tensions entre différentes communautés',
            'couleur_hex': '#c0392b',
        },
        {
            'libelle': 'Dégradation environnementale',
            'code': 'ENVIRONNEMENT',
            'description': 'Dégradation des ressources naturelles causant des tensions',
            'couleur_hex': '#27ae60',
        },
        {
            'libelle': 'Autre',
            'code': 'AUTRE',
            'description': 'Autre type d\'insécurité',
            'couleur_hex': '#95a5a6',
        },
    ]

    for data in types_data:
        type_insecurite, created = TypeInsecurite.objects.get_or_create(
            code=data['code'],
            defaults=data
        )

        if created:
            print(f"OK Type d'insécurité créé : {type_insecurite.libelle}")
        else:
            print(f"OK Type d'insécurité existe : {type_insecurite.libelle}")


def main():
    """Fonction principale"""
    print("=" * 70)
    print("INITIALISATION DES DONNÉES JAMM LEYDI - ARCHITECTURE V2")
    print("=" * 70)
    print()

    # 1. Créer le superutilisateur
    print("1. SUPERUTILISATEUR")
    admin_user = create_superuser()
    print()

    # 2. Créer le projet
    print("2. PROJET JAMM LEYDI")
    projet = create_projet(admin_user)
    print()

    # 3. Créer les communes
    print("3. COMMUNES")
    communes = create_communes(projet)
    print()

    # 4. Créer les thématiques
    print("4. THÉMATIQUES")
    thematiques = create_thematiques(projet)
    print()

    # 5. Créer les indicateurs
    print("5. INDICATEURS")
    create_indicateurs(thematiques)
    print()

    # 6. Créer les types d'interventions
    print("6. TYPES D'INTERVENTIONS")
    create_types_interventions()
    print()

    # 7. Créer les types d'infrastructures
    print("7. TYPES D'INFRASTRUCTURES")
    create_types_infrastructures()
    print()

    # 8. Créer les types d'acteurs
    print("8. TYPES D'ACTEURS")
    create_types_acteurs()
    print()

    # 9. Créer les types d'insécurité
    print("9. TYPES D'INSÉCURITÉ")
    create_types_insecurite()
    print()

    print("=" * 70)
    print("INITIALISATION TERMINÉE AVEC SUCCÈS")
    print("=" * 70)
    print()
    print("Statistiques :")
    print(f"  • 1 Projet créé : {projet.code_projet}")
    print(f"  • {len(communes)} Communes créées")
    print(f"  • {len(thematiques)} Thématiques créées")
    print(f"  • {Indicateur.objects.count()} Indicateurs créés")
    print(f"  • {TypeIntervention.objects.count()} Types d'interventions")
    print(f"  • {TypeInfrastructure.objects.count()} Types d'infrastructures")
    print(f"  • {TypeActeur.objects.count()} Types d'acteurs")
    print(f"  • {TypeInsecurite.objects.count()} Types d'insécurité")
    print()
    print("Accès à l'interface :")
    print("  • Admin Django : http://localhost:8000/admin/")
    print("  • Dashboard : http://localhost:8000/dashboard/")
    print("  • Login : admin")
    print("  • Mot de passe : admin123")
    print()


if __name__ == '__main__':
    main()
