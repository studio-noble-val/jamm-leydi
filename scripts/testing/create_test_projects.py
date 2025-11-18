#!/usr/bin/env python
"""
Script pour créer 5 projets de test
"""
import os
import django
from datetime import date
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamm_leydi.settings')
django.setup()

from core.models import Projet, User, UserProjet


def main():
    print("=" * 70)
    print("CREATION DE 5 PROJETS DE TEST")
    print("=" * 70)
    print()

    # Récupérer l'admin
    admin_user = User.objects.get(username='admin')

    projets_test = [
        {
            'code_projet': 'ACCES-EAU-2024',
            'libelle': 'Accès à l\'eau potable en zone rurale',
            'description': 'Projet d\'amélioration de l\'accès à l\'eau potable dans les villages ruraux',
            'pays': 'Mali',
            'equipe_grdr': 'Antenne Mali - Kayes',
            'bailleurs': 'Agence Française de Développement (AFD)',
            'zone_intervention': 'Région de Kayes, Mali',
            'date_debut': date(2024, 3, 1),
            'date_fin': date(2027, 2, 28),
            'budget': Decimal('1800000.00'),
            'devise': 'EUR',
            'statut': 'EN_COURS',
        },
        {
            'code_projet': 'AGRO-ECOLOGIE-2023',
            'libelle': 'Transition agro-écologique en Mauritanie',
            'description': 'Accompagnement des producteurs vers des pratiques agro-écologiques',
            'pays': 'Mauritanie',
            'equipe_grdr': 'Antenne Mauritanie - Nouakchott',
            'bailleurs': 'Union Européenne, AFD',
            'zone_intervention': 'Région du Guidimakha, Mauritanie',
            'date_debut': date(2023, 6, 1),
            'date_fin': date(2026, 5, 31),
            'budget': Decimal('2100000.00'),
            'devise': 'EUR',
            'statut': 'EN_COURS',
        },
        {
            'code_projet': 'JEUNESSE-EMPLOI-2025',
            'libelle': 'Insertion professionnelle des jeunes',
            'description': 'Programme d\'insertion professionnelle des jeunes en milieu rural et urbain',
            'pays': 'Guinée',
            'equipe_grdr': 'Antenne Guinée - Conakry',
            'bailleurs': 'Coopération Suisse, AFD',
            'zone_intervention': 'Régions de Labé et Conakry, Guinée',
            'date_debut': date(2025, 1, 1),
            'date_fin': date(2027, 12, 31),
            'budget': Decimal('1500000.00'),
            'devise': 'EUR',
            'statut': 'PLANIFIE',
        },
        {
            'code_projet': 'MIGRATION-DEV-2022',
            'libelle': 'Migration et co-développement France-Sénégal',
            'description': 'Renforcer les liens entre diasporas et territoires d\'origine',
            'pays': 'France',
            'equipe_grdr': 'Siège Paris - Montreuil',
            'bailleurs': 'Ministère de l\'Europe et des Affaires Étrangères (MEAE)',
            'zone_intervention': 'Île-de-France et Vallée du fleuve Sénégal',
            'date_debut': date(2022, 9, 1),
            'date_fin': date(2025, 8, 31),
            'budget': Decimal('980000.00'),
            'devise': 'EUR',
            'statut': 'EN_COURS',
        },
        {
            'code_projet': 'FORESTERIE-2021',
            'libelle': 'Gestion durable des forêts communautaires',
            'description': 'Programme de gestion durable et de valorisation des forêts communautaires',
            'pays': 'Sénégal',
            'equipe_grdr': 'Antenne Sénégal - Tambacounda',
            'bailleurs': 'Fonds Français pour l\'Environnement Mondial (FFEM)',
            'zone_intervention': 'Région de Tambacounda, Sénégal',
            'date_debut': date(2021, 4, 1),
            'date_fin': date(2024, 12, 31),
            'budget': Decimal('750000.00'),
            'devise': 'EUR',
            'statut': 'TERMINE',
        },
    ]

    for projet_data in projets_test:
        projet, created = Projet.objects.get_or_create(
            code_projet=projet_data['code_projet'],
            defaults=projet_data
        )

        if created:
            print(f"OK Projet cree : {projet.code_projet} - {projet.libelle}")

            # Lier l'admin au projet
            UserProjet.objects.get_or_create(
                user=admin_user,
                projet=projet,
                defaults={
                    'role': 'ADMIN_PROJET',
                    'actif': True,
                }
            )
            print(f"  -> Admin lie au projet")
        else:
            print(f"OK Projet existe : {projet.code_projet}")

    print()
    print("=" * 70)
    print("PROJETS DE TEST CRÉÉS AVEC SUCCÈS")
    print("=" * 70)
    print()
    print(f"Total projets dans la base : {Projet.objects.count()}")
    print(f"Projets accessibles par admin : {UserProjet.objects.filter(user=admin_user).count()}")
    print()
    print("Vous pouvez maintenant tester le scroll sur /projets/")


if __name__ == '__main__':
    main()
