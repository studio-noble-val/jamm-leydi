"""
Tests unitaires pour l'application core (multi-projets & utilisateurs)
"""
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Projet, UserProjet

User = get_user_model()


class UserModelTest(TestCase):
    """Tests pour le modèle User personnalisé"""

    def setUp(self):
        """Créer un utilisateur de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            telephone='+221771234567',
            organisation='GRDR'
        )

    def test_user_creation(self):
        """Vérifier que l'utilisateur est bien créé"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.telephone, '+221771234567')
        self.assertEqual(self.user.organisation, 'GRDR')

    def test_user_str(self):
        """Vérifier la représentation string de l'utilisateur"""
        # Avec nom complet
        self.assertEqual(str(self.user), 'Test User')

        # Sans nom complet
        user_no_name = User.objects.create_user(
            username='noname',
            password='testpass123'
        )
        self.assertEqual(str(user_no_name), 'noname')

    def test_user_full_name(self):
        """Vérifier get_full_name()"""
        self.assertEqual(self.user.get_full_name(), 'Test User')


class ProjetModelTest(TestCase):
    """Tests pour le modèle Projet"""

    def setUp(self):
        """Créer un projet de test"""
        self.projet = Projet.objects.create(
            code_projet='TEST-2024',
            libelle='Projet Test',
            zone_intervention='Zone de test',
            bailleurs='Bailleur Test',
            date_debut=date.today() - timedelta(days=30),
            date_fin=date.today() + timedelta(days=365),
            budget=100000,
            devise='EUR',
            statut='EN_COURS'
        )

    def test_projet_creation(self):
        """Vérifier que le projet est bien créé"""
        self.assertEqual(self.projet.code_projet, 'TEST-2024')
        self.assertEqual(self.projet.libelle, 'Projet Test')
        self.assertEqual(self.projet.statut, 'EN_COURS')

    def test_projet_str(self):
        """Vérifier la représentation string du projet"""
        self.assertEqual(str(self.projet), 'TEST-2024 - Projet Test')

    def test_projet_est_actif(self):
        """Vérifier la propriété est_actif"""
        # Projet en cours dans les dates
        self.assertTrue(self.projet.est_actif)

        # Projet terminé
        self.projet.statut = 'TERMINE'
        self.projet.save()
        self.assertFalse(self.projet.est_actif)

        # Projet en cours mais date passée
        self.projet.statut = 'EN_COURS'
        self.projet.date_fin = date.today() - timedelta(days=1)
        self.projet.save()
        self.assertFalse(self.projet.est_actif)

    def test_projet_code_unique(self):
        """Vérifier que le code projet est unique"""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Projet.objects.create(
                code_projet='TEST-2024',  # Même code
                libelle='Autre Projet',
                zone_intervention='Autre zone',
                bailleurs='Autre bailleur',
                date_debut=date.today(),
                date_fin=date.today() + timedelta(days=365)
            )


class UserProjetModelTest(TestCase):
    """Tests pour le modèle UserProjet (liaison utilisateur-projet)"""

    def setUp(self):
        """Créer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.projet = Projet.objects.create(
            code_projet='TEST-2024',
            libelle='Projet Test',
            zone_intervention='Zone de test',
            bailleurs='Bailleur Test',
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=365)
        )
        self.user_projet = UserProjet.objects.create(
            user=self.user,
            projet=self.projet,
            role='CONTRIBUTEUR'
        )

    def test_user_projet_creation(self):
        """Vérifier que la liaison est bien créée"""
        self.assertEqual(self.user_projet.user, self.user)
        self.assertEqual(self.user_projet.projet, self.projet)
        self.assertEqual(self.user_projet.role, 'CONTRIBUTEUR')
        self.assertTrue(self.user_projet.actif)

    def test_user_projet_str(self):
        """Vérifier la représentation string"""
        expected = 'testuser - TEST-2024 (Contributeur (saisie des données))'
        self.assertEqual(str(self.user_projet), expected)

    def test_user_projet_unique_together(self):
        """Vérifier qu'un utilisateur ne peut être lié qu'une fois à un projet"""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            UserProjet.objects.create(
                user=self.user,
                projet=self.projet,
                role='ADMIN_PROJET'
            )

    def test_user_projet_roles(self):
        """Vérifier les différents rôles disponibles"""
        roles = ['ADMIN_PROJET', 'CONTRIBUTEUR', 'LECTEUR']
        for role in roles:
            self.user_projet.role = role
            self.user_projet.save()
            self.assertEqual(self.user_projet.role, role)

    def test_projet_users_relation(self):
        """Vérifier la relation Many-to-Many via UserProjet"""
        # Le projet doit avoir l'utilisateur dans ses users
        self.assertIn(self.user, self.projet.users.all())

        # L'utilisateur doit avoir le projet dans ses projets
        self.assertIn(self.projet, self.user.projets.all())


class ProjetManagerTest(TestCase):
    """Tests pour les requêtes sur les projets"""

    def setUp(self):
        """Créer plusieurs projets de test"""
        # Projet actif
        self.projet_actif = Projet.objects.create(
            code_projet='ACTIF-2024',
            libelle='Projet Actif',
            zone_intervention='Zone',
            bailleurs='Bailleur',
            date_debut=date.today() - timedelta(days=30),
            date_fin=date.today() + timedelta(days=365),
            statut='EN_COURS',
            actif=True
        )

        # Projet terminé
        self.projet_termine = Projet.objects.create(
            code_projet='TERMINE-2024',
            libelle='Projet Terminé',
            zone_intervention='Zone',
            bailleurs='Bailleur',
            date_debut=date.today() - timedelta(days=365),
            date_fin=date.today() - timedelta(days=30),
            statut='TERMINE',
            actif=True
        )

    def test_filter_by_statut(self):
        """Filtrer les projets par statut"""
        projets_en_cours = Projet.objects.filter(statut='EN_COURS')
        self.assertEqual(projets_en_cours.count(), 1)
        self.assertEqual(projets_en_cours.first(), self.projet_actif)

    def test_filter_actifs(self):
        """Filtrer les projets actifs"""
        projets_actifs = Projet.objects.filter(actif=True)
        self.assertEqual(projets_actifs.count(), 2)
