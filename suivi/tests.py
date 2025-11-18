"""
Tests unitaires pour l'application suivi (indicateurs & interventions)
"""
from datetime import date, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from core.models import Projet
from referentiels.models import Commune, TypeIntervention
from .models import (
    Thematique, Indicateur, CibleIndicateur,
    Intervention, ValeurIndicateur
)

User = get_user_model()


class ThematiqueModelTest(TestCase):
    """Tests pour le modèle Thematique"""

    def setUp(self):
        """Créer les données de test"""
        self.projet = Projet.objects.create(
            code_projet='TEST-2024',
            libelle='Projet Test',
            zone_intervention='Zone de test',
            bailleurs='Bailleur Test',
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=365)
        )
        self.thematique = Thematique.objects.create(
            projet=self.projet,
            code='R1',
            libelle='Renforcement des capacités',
            description='Description de la thématique',
            ordre=1
        )

    def test_thematique_creation(self):
        """Vérifier que la thématique est bien créée"""
        self.assertEqual(self.thematique.code, 'R1')
        self.assertEqual(self.thematique.projet, self.projet)

    def test_thematique_str(self):
        """Vérifier la représentation string"""
        expected = 'TEST-2024 - R1: Renforcement des capacités'
        self.assertEqual(str(self.thematique), expected)

    def test_thematique_unique_together(self):
        """Vérifier que le code est unique par projet"""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Thematique.objects.create(
                projet=self.projet,
                code='R1',  # Même code
                libelle='Autre thématique'
            )


class IndicateurModelTest(TestCase):
    """Tests pour le modèle Indicateur"""

    def setUp(self):
        """Créer les données de test"""
        self.projet = Projet.objects.create(
            code_projet='TEST-2024',
            libelle='Projet Test',
            zone_intervention='Zone de test',
            bailleurs='Bailleur Test',
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=365)
        )
        self.thematique = Thematique.objects.create(
            projet=self.projet,
            code='R1',
            libelle='Renforcement des capacités'
        )
        self.indicateur = Indicateur.objects.create(
            projet=self.projet,
            thematique=self.thematique,
            code='R1.1',
            libelle='Nombre de formations réalisées',
            unite_mesure='Nombre',
            type_calcul='SOMME'
        )

    def test_indicateur_creation(self):
        """Vérifier que l'indicateur est bien créé"""
        self.assertEqual(self.indicateur.code, 'R1.1')
        self.assertEqual(self.indicateur.projet, self.projet)
        self.assertEqual(self.indicateur.thematique, self.thematique)

    def test_indicateur_str(self):
        """Vérifier la représentation string"""
        expected = 'TEST-2024 - R1.1 - Nombre de formations réalisées'
        self.assertEqual(str(self.indicateur), expected)

    def test_indicateur_clean_validation(self):
        """Vérifier que la thématique doit appartenir au même projet"""
        # Créer un autre projet avec sa thématique
        autre_projet = Projet.objects.create(
            code_projet='AUTRE-2024',
            libelle='Autre Projet',
            zone_intervention='Zone',
            bailleurs='Bailleur',
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=365)
        )
        autre_thematique = Thematique.objects.create(
            projet=autre_projet,
            code='R1',
            libelle='Autre thématique'
        )

        # Créer un indicateur avec thématique d'un autre projet
        indicateur_invalide = Indicateur(
            projet=self.projet,
            thematique=autre_thematique,  # Mauvais projet!
            code='R1.2',
            libelle='Test invalide'
        )

        with self.assertRaises(ValidationError):
            indicateur_invalide.clean()


class CibleIndicateurModelTest(TestCase):
    """Tests pour le modèle CibleIndicateur"""

    def setUp(self):
        """Créer les données de test"""
        self.projet = Projet.objects.create(
            code_projet='TEST-2024',
            libelle='Projet Test',
            zone_intervention='Zone de test',
            bailleurs='Bailleur Test',
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=365)
        )
        self.thematique = Thematique.objects.create(
            projet=self.projet,
            code='R1',
            libelle='Thématique Test'
        )
        self.indicateur = Indicateur.objects.create(
            projet=self.projet,
            thematique=self.thematique,
            code='R1.1',
            libelle='Indicateur Test'
        )
        self.cible = CibleIndicateur.objects.create(
            indicateur=self.indicateur,
            commune=None,  # Cible globale
            valeur_cible=1000,
            annee=2025
        )

    def test_cible_creation(self):
        """Vérifier que la cible est bien créée"""
        self.assertEqual(self.cible.valeur_cible, 1000)
        self.assertEqual(self.cible.annee, 2025)
        self.assertIsNone(self.cible.commune)

    def test_cible_str_globale(self):
        """Vérifier la représentation string d'une cible globale"""
        expected = 'R1.1 (global): 1000 (2025)'
        self.assertEqual(str(self.cible), expected)

    def test_cible_str_par_commune(self):
        """Vérifier la représentation string d'une cible par commune"""
        commune = Commune.objects.create(
            nom='Gathiary',
            code_commune='SN-KED-GAT'
        )
        cible_commune = CibleIndicateur.objects.create(
            indicateur=self.indicateur,
            commune=commune,
            valeur_cible=250,
            annee=2025
        )
        expected = 'R1.1 - Gathiary: 250 (2025)'
        self.assertEqual(str(cible_commune), expected)


class InterventionModelTest(TestCase):
    """Tests pour le modèle Intervention"""

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
        self.thematique = Thematique.objects.create(
            projet=self.projet,
            code='R1',
            libelle='Thématique Test'
        )
        self.indicateur = Indicateur.objects.create(
            projet=self.projet,
            thematique=self.thematique,
            code='R1.1',
            libelle='Indicateur Test'
        )
        self.commune = Commune.objects.create(
            nom='Gathiary',
            code_commune='SN-KED-GAT'
        )
        self.type_intervention = TypeIntervention.objects.create(
            libelle='Formation',
            code='FORM'
        )
        self.intervention = Intervention.objects.create(
            projet=self.projet,
            indicateur=self.indicateur,
            type_intervention=self.type_intervention,
            commune=self.commune,
            nature='ACTIVITE',
            libelle='Formation sur la gestion des conflits',
            valeur_quantitative=50,
            date_intervention=date.today(),
            statut='TERMINE',
            cree_par=self.user
        )

    def test_intervention_creation(self):
        """Vérifier que l'intervention est bien créée"""
        self.assertEqual(self.intervention.libelle, 'Formation sur la gestion des conflits')
        self.assertEqual(self.intervention.statut, 'TERMINE')
        self.assertEqual(self.intervention.valeur_quantitative, 50)

    def test_intervention_str(self):
        """Vérifier la représentation string"""
        today = date.today()
        expected = f'TEST-2024 - Formation sur la gestion des conflits - Gathiary ({today})'
        self.assertEqual(str(self.intervention), expected)

    def test_intervention_clean_validation(self):
        """Vérifier que l'indicateur doit appartenir au même projet"""
        # Créer un autre projet avec son indicateur
        autre_projet = Projet.objects.create(
            code_projet='AUTRE-2024',
            libelle='Autre Projet',
            zone_intervention='Zone',
            bailleurs='Bailleur',
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=365)
        )
        autre_thematique = Thematique.objects.create(
            projet=autre_projet,
            code='R1',
            libelle='Autre thématique'
        )
        autre_indicateur = Indicateur.objects.create(
            projet=autre_projet,
            thematique=autre_thematique,
            code='R1.1',
            libelle='Autre indicateur'
        )

        # Créer une intervention avec indicateur d'un autre projet
        intervention_invalide = Intervention(
            projet=self.projet,
            indicateur=autre_indicateur,  # Mauvais projet!
            type_intervention=self.type_intervention,
            commune=self.commune,
            libelle='Test invalide',
            date_intervention=date.today()
        )

        with self.assertRaises(ValidationError):
            intervention_invalide.clean()

    def test_intervention_statuts(self):
        """Vérifier les changements de statut"""
        self.intervention.statut = 'PROGRAMME'
        self.intervention.save()
        self.assertEqual(self.intervention.statut, 'PROGRAMME')

        self.intervention.statut = 'ANNULEE'
        self.intervention.save()
        self.assertEqual(self.intervention.statut, 'ANNULEE')


class ValeurIndicateurModelTest(TestCase):
    """Tests pour le modèle ValeurIndicateur"""

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
        self.thematique = Thematique.objects.create(
            projet=self.projet,
            code='R1',
            libelle='Thématique Test'
        )
        self.indicateur = Indicateur.objects.create(
            projet=self.projet,
            thematique=self.thematique,
            code='R1.1',
            libelle='Indicateur Test'
        )
        self.valeur = ValeurIndicateur.objects.create(
            indicateur=self.indicateur,
            commune=None,
            valeur_realisee=500,
            date_mesure=date(2025, 3, 31),
            source='SAISIE_MANUELLE',
            saisi_par=self.user
        )

    def test_valeur_creation(self):
        """Vérifier que la valeur est bien créée"""
        self.assertEqual(self.valeur.valeur_realisee, 500)
        self.assertEqual(self.valeur.source, 'SAISIE_MANUELLE')

    def test_valeur_trimestre(self):
        """Vérifier le calcul automatique du trimestre"""
        # T1 : janvier-mars
        self.valeur.date_mesure = date(2025, 3, 31)
        self.assertEqual(self.valeur.trimestre, 'T1')

        # T2 : avril-juin
        self.valeur.date_mesure = date(2025, 6, 30)
        self.assertEqual(self.valeur.trimestre, 'T2')

        # T3 : juillet-septembre
        self.valeur.date_mesure = date(2025, 9, 30)
        self.assertEqual(self.valeur.trimestre, 'T3')

        # T4 : octobre-décembre
        self.valeur.date_mesure = date(2025, 12, 31)
        self.assertEqual(self.valeur.trimestre, 'T4')

    def test_valeur_annee(self):
        """Vérifier la propriété année"""
        self.assertEqual(self.valeur.annee, 2025)


class CalculAvancementTest(TestCase):
    """Tests pour le calcul de l'avancement des indicateurs"""

    def setUp(self):
        """Créer les données de test complètes"""
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
        self.thematique = Thematique.objects.create(
            projet=self.projet,
            code='R1',
            libelle='Thématique Test'
        )
        self.indicateur = Indicateur.objects.create(
            projet=self.projet,
            thematique=self.thematique,
            code='R1.1',
            libelle='Indicateur Test',
            type_calcul='SOMME'
        )
        self.commune = Commune.objects.create(
            nom='Gathiary',
            code_commune='SN-KED-GAT'
        )
        self.type_intervention = TypeIntervention.objects.create(
            libelle='Formation',
            code='FORM'
        )

        # Créer une cible
        self.cible = CibleIndicateur.objects.create(
            indicateur=self.indicateur,
            commune=None,
            valeur_cible=100,
            annee=2025
        )

    def test_calcul_avancement_zero(self):
        """Vérifier le calcul avec aucune intervention"""
        from django.db.models import Sum
        total_realise = Intervention.objects.filter(
            indicateur=self.indicateur,
            statut='TERMINE'
        ).aggregate(total=Sum('valeur_quantitative'))['total'] or 0

        self.assertEqual(total_realise, 0)

    def test_calcul_avancement_partiel(self):
        """Vérifier le calcul avec des interventions partielles"""
        from django.db.models import Sum

        # Créer des interventions
        Intervention.objects.create(
            projet=self.projet,
            indicateur=self.indicateur,
            type_intervention=self.type_intervention,
            commune=self.commune,
            libelle='Intervention 1',
            valeur_quantitative=30,
            date_intervention=date.today(),
            statut='TERMINE',
            cree_par=self.user
        )
        Intervention.objects.create(
            projet=self.projet,
            indicateur=self.indicateur,
            type_intervention=self.type_intervention,
            commune=self.commune,
            libelle='Intervention 2',
            valeur_quantitative=20,
            date_intervention=date.today(),
            statut='TERMINE',
            cree_par=self.user
        )

        total_realise = Intervention.objects.filter(
            indicateur=self.indicateur,
            statut='TERMINE'
        ).aggregate(total=Sum('valeur_quantitative'))['total'] or 0

        self.assertEqual(total_realise, 50)

        # Calculer le pourcentage
        pourcentage = (total_realise / self.cible.valeur_cible) * 100
        self.assertEqual(pourcentage, 50.0)

    def test_interventions_non_terminees_exclues(self):
        """Vérifier que seules les interventions terminées sont comptées"""
        from django.db.models import Sum

        # Intervention terminée
        Intervention.objects.create(
            projet=self.projet,
            indicateur=self.indicateur,
            type_intervention=self.type_intervention,
            commune=self.commune,
            libelle='Terminée',
            valeur_quantitative=50,
            date_intervention=date.today(),
            statut='TERMINE',
            cree_par=self.user
        )

        # Intervention programmée (ne doit pas être comptée)
        Intervention.objects.create(
            projet=self.projet,
            indicateur=self.indicateur,
            type_intervention=self.type_intervention,
            commune=self.commune,
            libelle='Programmée',
            valeur_quantitative=100,
            date_intervention=date.today(),
            statut='PROGRAMME',
            cree_par=self.user
        )

        total_realise = Intervention.objects.filter(
            indicateur=self.indicateur,
            statut='TERMINE'
        ).aggregate(total=Sum('valeur_quantitative'))['total'] or 0

        # Seule l'intervention terminée doit être comptée
        self.assertEqual(total_realise, 50)
