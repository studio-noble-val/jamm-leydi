"""
Modèles pour le monitoring de la sécurité (R1)
"""
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils import timezone
from core.models import Projet, User
from referentiels.models import Commune


class TypeInsecurite(models.Model):
    """
    Types d'incidents de sécurité
    Ex: Conflit foncier, Vol de bétail, Tensions intercommunautaires, etc.
    """
    libelle = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    # Niveau de gravité par défaut
    GRAVITE_CHOICES = [
        ('FAIBLE', 'Faible'),
        ('MOYENNE', 'Moyenne'),
        ('ELEVEE', 'Élevée'),
        ('CRITIQUE', 'Critique'),
    ]
    gravite_defaut = models.CharField(max_length=10, choices=GRAVITE_CHOICES,
                                     default='MOYENNE',
                                     help_text="Niveau de gravité par défaut")

    # Couleur pour visualisation
    couleur_hex = models.CharField(max_length=7, default="#DC3545",
                                  help_text="Couleur pour les cartes et graphiques")

    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Type d'insécurité"
        verbose_name_plural = "Types d'insécurité"
        ordering = ['libelle']

    def __str__(self):
        return f"{self.code} - {self.libelle}"


class SecurityReport(gis_models.Model):
    """
    Rapports d'incidents de sécurité
    Géolocalisés pour cartographie des zones à risque
    """
    GRAVITE_CHOICES = [
        ('FAIBLE', 'Faible'),
        ('MOYENNE', 'Moyenne'),
        ('ELEVEE', 'Élevée'),
        ('CRITIQUE', 'Critique'),
    ]

    STATUT_CHOICES = [
        ('SIGNALE', 'Signalé'),
        ('EN_VERIFICATION', 'En vérification'),
        ('CONFIRME', 'Confirmé'),
        ('RESOLU', 'Résolu'),
        ('CLOS', 'Clos'),
        ('FAUSSE_ALERTE', 'Fausse alerte'),
    ]

    # Relations
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE,
                              related_name='security_reports')
    type_insecurite = models.ForeignKey(TypeInsecurite, on_delete=models.PROTECT,
                                       related_name='reports')
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE,
                               related_name='security_reports')

    # Informations de base
    libelle = models.CharField(max_length=255,
                              help_text="Titre court de l'incident")
    description = models.TextField(help_text="Description détaillée de l'incident")

    # Gravité et impact
    gravite = models.CharField(max_length=10, choices=GRAVITE_CHOICES)
    nb_personnes_affectees = models.IntegerField(null=True, blank=True,
                                                 help_text="Nombre de personnes affectées")
    impact_economique = models.TextField(blank=True, null=True,
                                        help_text="Description de l'impact économique")

    # Géolocalisation
    geom = gis_models.PointField(srid=4326, null=True, blank=True,
                                help_text="Localisation de l'incident")
    village = models.CharField(max_length=100, blank=True, null=True)
    lieu_dit = models.CharField(max_length=200, blank=True, null=True,
                               help_text="Lieu-dit ou localisation descriptive")

    # Dates
    date_incident = models.DateField(help_text="Date de l'incident")
    heure_incident = models.TimeField(null=True, blank=True)
    date_signalement = models.DateTimeField(default=timezone.now)

    # Parties impliquées
    parties_impliquees = models.TextField(blank=True, null=True,
                                         help_text="Acteurs/communautés impliqués")
    temoins = models.TextField(blank=True, null=True)

    # Suivi et résolution
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES,
                            default='SIGNALE')
    actions_entreprises = models.TextField(blank=True, null=True,
                                          help_text="Actions de médiation/résolution")
    date_resolution = models.DateField(null=True, blank=True)
    resolution_description = models.TextField(blank=True, null=True)

    # Source du signalement
    SOURCE_CHOICES = [
        ('TERRAIN', 'Équipe terrain'),
        ('COMMUNAUTE', 'Communauté locale'),
        ('AUTORITE', 'Autorités'),
        ('PARTENAIRE', 'Partenaire'),
        ('KOBO', 'Formulaire Kobo'),
        ('AUTRE', 'Autre'),
    ]
    source_signalement = models.CharField(max_length=20, choices=SOURCE_CHOICES,
                                         default='TERRAIN')
    contact_signalant = models.CharField(max_length=100, blank=True, null=True,
                                        help_text="Nom/contact de la personne ayant signalé")

    # Confidentialité
    confidentiel = models.BooleanField(default=False,
                                      help_text="Marquer comme confidentiel (non publié)")
    notes_confidentielles = models.TextField(blank=True, null=True,
                                            help_text="Notes internes confidentielles")

    # Métadonnées
    date_creation = models.DateTimeField(default=timezone.now)
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL,
                                null=True, related_name='security_reports_crees')
    modifie_par = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='security_reports_modifies')
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rapport de sécurité"
        verbose_name_plural = "Rapports de sécurité"
        ordering = ['-date_incident', '-date_signalement']
        indexes = [
            models.Index(fields=['projet', 'commune', 'date_incident']),
            models.Index(fields=['type_insecurite', 'statut']),
            models.Index(fields=['gravite']),
        ]

    def __str__(self):
        return f"{self.libelle} - {self.commune.nom} ({self.date_incident})"

    def save(self, *args, **kwargs):
        """Initialise la gravité depuis le type si non définie"""
        if not self.gravite and self.type_insecurite:
            self.gravite = self.type_insecurite.gravite_defaut
        super().save(*args, **kwargs)
