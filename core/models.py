"""
Modèles de base pour la gestion multi-projets et utilisateurs
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Utilisateur personnalisé pour la plateforme GRDR
    Hérite de AbstractUser pour flexibilité future
    """
    telephone = models.CharField(max_length=20, blank=True, null=True)
    organisation = models.CharField(max_length=200, blank=True, null=True,
                                   help_text="Organisation d'appartenance (GRDR, partenaire, etc.)")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.get_full_name() or self.username


class Projet(models.Model):
    """
    Projet de développement (ex: JAMM LEYDI)
    Permet de gérer plusieurs projets sur la même plateforme
    """
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('SUSPENDU', 'Suspendu'),
        ('PLANIFIE', 'Planifié'),
    ]

    # Code projet généré automatiquement au format PROJ-{id}
    code_projet = models.CharField(max_length=50, unique=True, editable=False, blank=True,
                                   help_text="Code unique auto-généré (ex: PROJ-1)")
    libelle = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Localisation géographique (sélection en cascade)
    # Zone d'intervention définie par une sélection multi-niveaux
    zone_pays = models.ManyToManyField('geo.Admin2', blank=True,
                                       related_name='projets_zone',
                                       help_text="Pays de la zone d'intervention")
    zone_regions = models.ManyToManyField('geo.Admin4', blank=True,
                                          related_name='projets_zone',
                                          help_text="Régions de la zone d'intervention")
    zone_departements = models.ManyToManyField('geo.Admin5', blank=True,
                                               related_name='projets_zone',
                                               help_text="Départements de la zone d'intervention")
    zone_arrondissements = models.ManyToManyField('geo.Admin7', blank=True,
                                                  related_name='projets_zone',
                                                  help_text="Arrondissements de la zone d'intervention")
    zone_communes = models.ManyToManyField('geo.Admin8', blank=True,
                                           related_name='projets_zone',
                                           help_text="Communes de la zone d'intervention")

    # Équipe GRDR (cellule géolocalisée)
    cellule_grdr = models.ForeignKey('geo.CellulesGRDR', on_delete=models.SET_NULL,
                                    null=True, blank=True,
                                    related_name='projets',
                                    db_constraint=False,
                                    help_text="Cellule GRDR de rattachement")

    # Bailleurs et partenaires
    bailleurs = models.TextField(help_text="Liste des bailleurs (ex: Union Européenne, AFD...)")

    # Dates
    date_debut = models.DateField()
    date_fin = models.DateField()

    # Financier
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                help_text="Budget total en FCFA ou EUR")
    devise = models.CharField(max_length=3, default="EUR",
                            help_text="EUR, FCFA, USD...")

    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_COURS')

    # Médias
    logo = models.ImageField(upload_to='projets/logos/', null=True, blank=True)

    # Métadonnées
    date_creation = models.DateTimeField(default=timezone.now)
    actif = models.BooleanField(default=True)

    # Utilisateurs avec accès à ce projet (relation Many-to-Many via UserProjet)
    users = models.ManyToManyField(User, through='UserProjet', related_name='projets')

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.code_projet} - {self.libelle}"

    def save(self, *args, **kwargs):
        """Génération automatique du code_projet au format PROJ-{id}"""
        if not self.code_projet:
            # Sauvegarder d'abord pour obtenir l'ID
            super().save(*args, **kwargs)
            # Générer le code et resauvegarder
            self.code_projet = f"PROJ-{self.id}"
            # Mettre à jour sans créer une boucle infinie
            kwargs['force_insert'] = False
            super().save(update_fields=['code_projet'])
        else:
            super().save(*args, **kwargs)

    @property
    def est_actif(self):
        """Vérifie si le projet est en cours et dans les dates"""
        if not self.actif or self.statut != 'EN_COURS':
            return False
        now = timezone.now().date()
        return self.date_debut <= now <= self.date_fin

    @property
    def zone_intervention_description(self):
        """Retourne une description textuelle de la zone d'intervention"""
        zones = []

        if self.zone_pays.exists():
            zones.append(f"Pays: {', '.join([p.name for p in self.zone_pays.all()])}")
        if self.zone_regions.exists():
            zones.append(f"Régions: {', '.join([r.name for r in self.zone_regions.all()])}")
        if self.zone_departements.exists():
            zones.append(f"Départements: {', '.join([d.name for d in self.zone_departements.all()])}")
        if self.zone_arrondissements.exists():
            zones.append(f"Arrondissements: {', '.join([a.name for a in self.zone_arrondissements.all()])}")
        if self.zone_communes.exists():
            zones.append(f"Communes: {', '.join([c.name for c in self.zone_communes.all()])}")

        return " | ".join(zones) if zones else "Zone non définie"


class UserProjet(models.Model):
    """
    Relation Many-to-Many entre User et Projet avec rôles
    Un utilisateur peut avoir des rôles différents sur plusieurs projets
    """
    ROLE_CHOICES = [
        ('ADMIN_PROJET', 'Administrateur du projet'),
        ('CONTRIBUTEUR', 'Contributeur (saisie des données)'),
        ('LECTEUR', 'Lecteur (consultation uniquement)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_projets')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='projet_users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Métadonnées
    date_ajout = models.DateTimeField(default=timezone.now)
    actif = models.BooleanField(default=True,
                               help_text="Permet de désactiver l'accès sans supprimer")

    class Meta:
        verbose_name = "Utilisateur-Projet"
        verbose_name_plural = "Utilisateurs-Projets"
        unique_together = ['user', 'projet']
        ordering = ['projet', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.projet.code_projet} ({self.get_role_display()})"
