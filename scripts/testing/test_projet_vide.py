#!/usr/bin/env python
"""
Script pour créer un projet de test sans thématiques
Pour tester l'affichage de la card "Créer les thématiques"
"""
import os
import django
from datetime import date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamm_leydi.settings')
django.setup()

from core.models import User, Projet, UserProjet

def main():
    print("=" * 70)
    print("CREATION D'UN PROJET DE TEST SANS THEMATIQUES")
    print("=" * 70)
    print()

    # Récupérer l'admin
    admin_user = User.objects.get(username='admin')

    # Créer le projet
    projet, created = Projet.objects.get_or_create(
        code_projet='TEST-VIDE-2025',
        defaults={
            'libelle': 'Projet Test Vide (sans thématiques)',
            'description': 'Projet de test pour vérifier l\'affichage de la card de création de thématiques',
            'pays': 'Test',
            'equipe_grdr': 'Équipe Test',
            'bailleurs': 'Bailleur Test',
            'zone_intervention': 'Zone Test',
            'date_debut': date(2025, 1, 1),
            'date_fin': date(2027, 12, 31),
            'budget': Decimal('1000000.00'),
            'devise': 'EUR',
            'statut': 'EN_COURS',
            'actif': True,
        }
    )

    if created:
        print(f"OK Projet créé : {projet.code_projet}")
    else:
        print(f"OK Projet existe : {projet.code_projet}")

    # Lier l'admin au projet
    user_projet, created = UserProjet.objects.get_or_create(
        user=admin_user,
        projet=projet,
        defaults={
            'role': 'ADMIN_PROJET',
            'actif': True,
        }
    )

    if created:
        print(f"OK Admin assigné au projet")

    print()
    print("=" * 70)
    print("PROJET DE TEST CREE AVEC SUCCES")
    print("=" * 70)
    print()
    print(f"Code projet : {projet.code_projet}")
    print(f"Libellé : {projet.libelle}")
    print(f"Nombre de thématiques : 0 (volontairement)")
    print()
    print("Allez sur /projets/ et sélectionnez ce projet pour tester")

if __name__ == '__main__':
    main()
