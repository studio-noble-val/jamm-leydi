"""
Modèles de suivi des indicateurs et interventions
Cœur métier de la plateforme
"""
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils import timezone
from core.models import Projet, User
from referentiels.models import Commune, TypeIntervention


class Thematique(models.Model):
    """
    Thématiques/Résultats du cadre logique
    Ex: R1 - Renforcement des capacités, R2 - Cohésion sociale, R3 - Solutions locales
    """
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE,
                              related_name='thematiques')
    code = models.CharField(max_length=20,
                           help_text="Code court (ex: R1, R2, R3...)")
    libelle = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Ordre d'affichage
    ordre = models.IntegerField(default=0,
                               help_text="Pour trier les thématiques dans les dashboards")

    class Meta:
        verbose_name = "Thématique"
        verbose_name_plural = "Thématiques"
        unique_together = ['projet', 'code']
        ordering = ['projet', 'ordre', 'code']

    def __str__(self):
        return f"{self.projet.code_projet} - {self.code}: {self.libelle}"


class Indicateur(models.Model):
    """
    Indicateurs du cadre logique
    Rattaché directement à un Projet ET à une Thématique de ce projet
    """
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE,
                              related_name='indicateurs',
                              help_text="Projet auquel appartient cet indicateur")
    thematique = models.ForeignKey(Thematique, on_delete=models.CASCADE,
                                  related_name='indicateurs',
                                  help_text="Thématique du projet")
    code = models.CharField(max_length=50,
                           help_text="Code unique de l'indicateur (ex: R1.1, R2.3...)")
    libelle = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Unité de mesure
    unite_mesure = models.CharField(max_length=50, default="Nombre",
                                   help_text="Ex: Nombre, Personnes, Hectares, %, etc.")

    # Type de calcul pour l'agrégation
    TYPE_CALCUL_CHOICES = [
        ('SOMME', 'Somme des valeurs'),
        ('MOYENNE', 'Moyenne des valeurs'),
        ('DENOMBREMENT', 'Comptage des occurrences'),
        ('MANUEL', 'Saisie manuelle uniquement'),
    ]
    type_calcul = models.CharField(max_length=20, choices=TYPE_CALCUL_CHOICES,
                                  default='SOMME',
                                  help_text="Mode de calcul pour agréger les valeurs")

    # Ordre d'affichage
    ordre = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Indicateur"
        verbose_name_plural = "Indicateurs"
        unique_together = ['projet', 'code']
        ordering = ['projet', 'thematique__ordre', 'ordre', 'code']
        indexes = [
            models.Index(fields=['projet', 'thematique']),
        ]

    def __str__(self):
        return f"{self.projet.code_projet} - {self.code} - {self.libelle}"

    def clean(self):
        """Valider que la thématique appartient bien au même projet"""
        from django.core.exceptions import ValidationError
        if self.thematique and self.projet and self.thematique.projet_id != self.projet_id:
            raise ValidationError({
                'thematique': f"La thématique doit appartenir au projet {self.projet.code_projet}"
            })


class CibleIndicateur(models.Model):
    """
    Cibles pour chaque indicateur
    Peut être déclinée par commune ou globale pour le projet
    """
    indicateur = models.ForeignKey(Indicateur, on_delete=models.CASCADE,
                                  related_name='cibles')
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE,
                               null=True, blank=True,
                               help_text="Laisser vide pour une cible globale projet")

    # Valeur cible
    valeur_cible = models.IntegerField(help_text="Valeur à atteindre")

    # Période
    annee = models.IntegerField(help_text="Année de la cible (ex: 2025, 2026)")

    # Métadonnées
    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Cible d'indicateur"
        verbose_name_plural = "Cibles des indicateurs"
        unique_together = ['indicateur', 'commune', 'annee']
        ordering = ['indicateur', 'annee', 'commune']

    def __str__(self):
        commune_str = f" - {self.commune.nom}" if self.commune else " (global)"
        return f"{self.indicateur.code}{commune_str}: {self.valeur_cible} ({self.annee})"


class Intervention(gis_models.Model):
    """
    Interventions/Activités/Réalisations du projet
    Unifie les notions d'activités (immatériel) et réalisations (matériel)
    Rattaché directement à un Projet ET à un Indicateur de ce projet
    """
    TYPE_INTERVENTION_CHOICES = [
        ('ACTIVITE', 'Activité (formation, réunion, sensibilisation...)'),
        ('REALISATION', 'Réalisation (infrastructure, équipement...)'),
    ]

    STATUT_CHOICES = [
        ('PROGRAMME', 'Programmé'),
        ('TERMINE', 'Terminé'),
        ('ANNULEE', 'Annulée'),
    ]

    # Relations
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE,
                              related_name='interventions',
                              help_text="Projet auquel appartient cette intervention")
    indicateur = models.ForeignKey(Indicateur, on_delete=models.CASCADE,
                                  related_name='interventions',
                                  help_text="Indicateur du projet")
    type_intervention = models.ForeignKey(TypeIntervention, on_delete=models.PROTECT,
                                         related_name='interventions')
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE,
                               related_name='interventions')

    # Type
    nature = models.CharField(max_length=20, choices=TYPE_INTERVENTION_CHOICES,
                            default='ACTIVITE',
                            help_text="Activité (immatériel) ou Réalisation (matériel)")

    # Informations de base
    libelle = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Valeur quantitative pour le suivi
    valeur_quantitative = models.IntegerField(null=True, blank=True,
                                             help_text="Nb participants, bénéficiaires, quantité produite...")

    # Dates
    date_intervention = models.DateField(help_text="Date de l'intervention")
    date_creation = models.DateTimeField(default=timezone.now)

    # Géolocalisation
    geom = gis_models.PointField(srid=4326, null=True, blank=True,
                                help_text="Localisation précise de l'intervention")

    # Statut de l'intervention
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES,
                            default='PROGRAMME')
    notes = models.TextField(blank=True, null=True,
                            help_text="Notes ou commentaires")

    # Traçabilité
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL,
                                null=True, related_name='interventions_creees')
    valide_par = models.ForeignKey(User, on_delete=models.SET_NULL,
                                  null=True, blank=True,
                                  related_name='interventions_validees')
    date_validation = models.DateTimeField(null=True, blank=True)

    # Médias
    photo = models.ImageField(upload_to='interventions/', null=True, blank=True)

    class Meta:
        verbose_name = "Intervention"
        verbose_name_plural = "Interventions"
        ordering = ['-date_intervention']
        indexes = [
            models.Index(fields=['projet', 'indicateur', 'commune', 'date_intervention']),
            models.Index(fields=['projet', 'statut']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"{self.projet.code_projet} - {self.libelle} - {self.commune.nom} ({self.date_intervention})"

    def clean(self):
        """Valider que l'indicateur appartient bien au même projet"""
        from django.core.exceptions import ValidationError
        if self.indicateur and self.projet and self.indicateur.projet_id != self.projet_id:
            raise ValidationError({
                'indicateur': f"L'indicateur doit appartenir au projet {self.projet.code_projet}"
            })


class ValeurIndicateur(models.Model):
    """
    Saisie trimestrielle des valeurs d'indicateurs
    Permet le suivi dans le temps avec graphiques d'évolution
    """
    SOURCE_CHOICES = [
        ('SAISIE_MANUELLE', 'Saisie manuelle'),
        ('CALCUL_AUTO', 'Calcul automatique'),
        ('IMPORT_EXTERNE', 'Import externe (Excel, Kobo...)'),
    ]

    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('VALIDE', 'Validé'),
        ('PUBLIE', 'Publié'),
    ]

    # Relations
    indicateur = models.ForeignKey(Indicateur, on_delete=models.CASCADE,
                                  related_name='valeurs')
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE,
                               null=True, blank=True,
                               help_text="Laisser vide pour valeur globale projet")

    # Valeur
    valeur_realisee = models.IntegerField(help_text="Valeur réalisée (nombre entier)")
    date_mesure = models.DateField(help_text="Date de la mesure/saisie")

    # Source et validation
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES,
                            default='SAISIE_MANUELLE')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES,
                            default='BROUILLON')

    # Métadonnées
    commentaire = models.TextField(blank=True, null=True)
    date_saisie = models.DateTimeField(default=timezone.now)
    saisi_par = models.ForeignKey(User, on_delete=models.SET_NULL,
                                 null=True, related_name='valeurs_saisies')

    class Meta:
        verbose_name = "Valeur d'indicateur"
        verbose_name_plural = "Valeurs des indicateurs"
        ordering = ['-date_mesure']
        indexes = [
            models.Index(fields=['indicateur', 'date_mesure']),
            models.Index(fields=['commune', 'date_mesure']),
        ]

    def __str__(self):
        commune_str = f" - {self.commune.nom}" if self.commune else " (global)"
        return f"{self.indicateur.code}{commune_str}: {self.valeur_realisee} ({self.date_mesure})"

    @property
    def trimestre(self):
        """Calcul automatique du trimestre à partir de la date"""
        return f"T{(self.date_mesure.month - 1) // 3 + 1}"

    @property
    def annee(self):
        """Année de la mesure"""
        return self.date_mesure.year


# Tables de liaison Many-to-Many

class InterventionActeur(models.Model):
    """
    Liaison entre Intervention et Acteurs (organisations impliquées)
    """
    intervention = models.ForeignKey('Intervention', on_delete=models.CASCADE)
    acteur = models.ForeignKey('geo.Acteur', on_delete=models.CASCADE)
    role = models.CharField(max_length=100, blank=True, null=True,
                           help_text="Rôle de l'acteur dans l'intervention")

    class Meta:
        verbose_name = "Intervention-Acteur"
        verbose_name_plural = "Interventions-Acteurs"
        unique_together = ['intervention', 'acteur']


class InterventionInfrastructure(models.Model):
    """
    Liaison entre Intervention et Infrastructures
    """
    intervention = models.ForeignKey('Intervention', on_delete=models.CASCADE)
    infrastructure = models.ForeignKey('geo.Infrastructure', on_delete=models.CASCADE)
    commentaire = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Intervention-Infrastructure"
        verbose_name_plural = "Interventions-Infrastructures"
        unique_together = ['intervention', 'infrastructure']
