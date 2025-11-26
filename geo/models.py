"""
Modèles géolocalisés : Infrastructures, Acteurs, Admin2 (pays) et Cellules GRDR
"""
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils import timezone
from core.models import Projet
from referentiels.models import Commune, TypeInfrastructure, TypeActeur


class Admin2(gis_models.Model):
    """
    Niveau administratif 2 (pays)
    Table miroir de geo.admin-2 pour l'intégration dans Django ORM
    """
    geom = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    osm_id = models.CharField(max_length=254, blank=True, null=True)
    osm_way_id = models.CharField(max_length=254, blank=True, null=True)
    name = models.CharField(max_length=254, blank=True, null=True,
                           help_text="Nom du pays")
    type = models.CharField(max_length=254, blank=True, null=True)
    aeroway = models.CharField(max_length=254, blank=True, null=True)
    amenity = models.CharField(max_length=254, blank=True, null=True)
    admin_leve = models.CharField(max_length=254, blank=True, null=True,
                                 db_column='admin_leve',
                                 help_text="Niveau administratif")
    barrier = models.CharField(max_length=254, blank=True, null=True)
    boundary = models.CharField(max_length=254, blank=True, null=True)
    building = models.CharField(max_length=254, blank=True, null=True)
    craft = models.CharField(max_length=254, blank=True, null=True)
    geological = models.CharField(max_length=254, blank=True, null=True)
    historic = models.CharField(max_length=254, blank=True, null=True)
    land_area = models.CharField(max_length=254, blank=True, null=True)
    landuse = models.CharField(max_length=254, blank=True, null=True)
    leisure = models.CharField(max_length=254, blank=True, null=True)
    man_made = models.CharField(max_length=254, blank=True, null=True)
    military = models.CharField(max_length=254, blank=True, null=True)
    natural = models.CharField(max_length=254, blank=True, null=True)
    office = models.CharField(max_length=254, blank=True, null=True)
    place = models.CharField(max_length=254, blank=True, null=True)
    shop = models.CharField(max_length=254, blank=True, null=True)
    sport = models.CharField(max_length=254, blank=True, null=True)
    tourism = models.CharField(max_length=254, blank=True, null=True)
    other_tags = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        db_table = '"geo"."admin-2"'
        managed = False  # Table gérée en dehors de Django
        verbose_name = "Pays (Admin2)"
        verbose_name_plural = "Pays (Admin2)"

    def __str__(self):
        return self.name or f"Admin2 #{self.id}"


class CellulesGRDR(gis_models.Model):
    """
    Cellules (antennes, bureaux) du GRDR avec géolocalisation
    Table miroir de geo."cellules-grdr"
    """
    nom = models.CharField(max_length=255,
                          help_text="Nom officiel de la cellule")
    geom = gis_models.PointField(srid=4326, null=True, blank=True,
                                 help_text="Coordonnées géographiques de la cellule (SRID 4326)")

    class Meta:
        db_table = '"geo"."cellules-grdr"'  # Guillemets requis à cause du trait d'union
        managed = False  # Table gérée en dehors de Django
        verbose_name = "Cellule GRDR"
        verbose_name_plural = "Cellules GRDR"

    def __str__(self):
        return self.nom


class Admin4(gis_models.Model):
    """
    Niveau administratif 4 - Régions
    Table miroir de geo.admin-4
    """
    geom = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    osm_id = models.CharField(max_length=254, blank=True, null=True)
    osm_way_id = models.CharField(max_length=254, blank=True, null=True)
    name = models.CharField(max_length=254, blank=True, null=True,
                           help_text="Nom de la région")
    admin_leve = models.CharField(max_length=254, blank=True, null=True)
    boundary = models.CharField(max_length=254, blank=True, null=True)
    place = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        db_table = '"geo"."admin-4"'
        managed = False
        verbose_name = "Région (Admin4)"
        verbose_name_plural = "Régions (Admin4)"

    def __str__(self):
        return self.name or f"Admin4 #{self.id}"


class Admin5(gis_models.Model):
    """
    Niveau administratif 5 - Départements
    Table miroir de geo.admin-5
    """
    geom = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    osm_id = models.CharField(max_length=254, blank=True, null=True)
    osm_way_id = models.CharField(max_length=254, blank=True, null=True)
    name = models.CharField(max_length=254, blank=True, null=True,
                           help_text="Nom du département")
    admin_leve = models.CharField(max_length=254, blank=True, null=True)
    boundary = models.CharField(max_length=254, blank=True, null=True)
    place = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        db_table = '"geo"."admin-5"'
        managed = False
        verbose_name = "Département (Admin5)"
        verbose_name_plural = "Départements (Admin5)"

    def __str__(self):
        return self.name or f"Admin5 #{self.id}"


class Admin7(gis_models.Model):
    """
    Niveau administratif 7 - Arrondissements
    Table miroir de geo.admin-7
    """
    geom = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    osm_id = models.CharField(max_length=254, blank=True, null=True)
    osm_way_id = models.CharField(max_length=254, blank=True, null=True)
    name = models.CharField(max_length=254, blank=True, null=True,
                           help_text="Nom de l'arrondissement")
    admin_leve = models.CharField(max_length=254, blank=True, null=True)
    boundary = models.CharField(max_length=254, blank=True, null=True)
    place = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        db_table = '"geo"."admin-7"'
        managed = False
        verbose_name = "Arrondissement (Admin7)"
        verbose_name_plural = "Arrondissements (Admin7)"

    def __str__(self):
        return self.name or f"Admin7 #{self.id}"


class Admin8(gis_models.Model):
    """
    Niveau administratif 8 - Communes
    Table miroir de geo.admin-8
    """
    geom = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    osm_id = models.CharField(max_length=254, blank=True, null=True)
    osm_way_id = models.CharField(max_length=254, blank=True, null=True)
    name = models.CharField(max_length=254, blank=True, null=True,
                           help_text="Nom de la commune")
    admin_leve = models.CharField(max_length=254, blank=True, null=True)
    boundary = models.CharField(max_length=254, blank=True, null=True)
    place = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        db_table = '"geo"."admin-8"'
        managed = False
        verbose_name = "Commune (Admin8)"
        verbose_name_plural = "Communes (Admin8)"

    def __str__(self):
        return self.name or f"Admin8 #{self.id}"


class Infrastructure(gis_models.Model):
    """
    Infrastructures géolocalisées
    Ex: Forages, Écoles, Maraîchages, Cantines scolaires, Postes de santé, etc.
    """
    STATUT_CHOICES = [
        ('PLANIFIE', 'Planifié'),
        ('EN_CONSTRUCTION', 'En construction'),
        ('FONCTIONNEL', 'Fonctionnel'),
        ('EN_PANNE', 'En panne'),
        ('ABANDONNE', 'Abandonné'),
    ]

    # Relations
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE,
                              related_name='infrastructures')
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE,
                               related_name='infrastructures')
    type_infrastructure = models.ForeignKey(TypeInfrastructure,
                                           on_delete=models.PROTECT,
                                           related_name='infrastructures')

    # Informations de base
    nom = models.CharField(max_length=255,
                          help_text="Nom de l'infrastructure (ex: Forage de Gathiary)")
    description = models.TextField(blank=True, null=True)

    # Géolocalisation
    geom = gis_models.PointField(srid=4326,
                                help_text="Localisation GPS de l'infrastructure")
    adresse = models.CharField(max_length=255, blank=True, null=True,
                              help_text="Adresse ou localisation descriptive")
    village = models.CharField(max_length=100, blank=True, null=True)

    # Bénéficiaires
    nb_beneficiaires = models.IntegerField(null=True, blank=True,
                                          help_text="Nombre de bénéficiaires directs")
    nb_beneficiaires_indirects = models.IntegerField(null=True, blank=True)

    # Statut et dates
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES,
                            default='PLANIFIE')
    date_construction = models.DateField(null=True, blank=True)
    date_mise_en_service = models.DateField(null=True, blank=True)

    # Caractéristiques techniques (JSON pour flexibilité)
    caracteristiques = models.JSONField(default=dict, blank=True,
                                       help_text="Caractéristiques spécifiques (débit, capacité, etc.)")

    # Coût
    cout_construction = models.DecimalField(max_digits=12, decimal_places=2,
                                           null=True, blank=True,
                                           help_text="Coût en devise du projet")

    # Médias
    photo = models.ImageField(upload_to='infrastructures/', null=True, blank=True)

    # Métadonnées
    date_creation = models.DateTimeField(default=timezone.now)
    actif = models.BooleanField(default=True)

    # Relations Many-to-Many avec Interventions (via InterventionInfrastructure)
    interventions = models.ManyToManyField('suivi.Intervention',
                                          through='suivi.InterventionInfrastructure',
                                          related_name='infrastructures_liees')

    class Meta:
        verbose_name = "Infrastructure"
        verbose_name_plural = "Infrastructures"
        ordering = ['commune', 'nom']
        indexes = [
            models.Index(fields=['projet', 'commune']),
            models.Index(fields=['type_infrastructure']),
        ]

    def __str__(self):
        return f"{self.nom} ({self.type_infrastructure.libelle}) - {self.commune.nom}"


class Acteur(gis_models.Model):
    """
    Acteurs/Organisations géolocalisés
    Ex: Groupements féminins, Associations d'éleveurs, Coopératives agricoles, etc.
    """
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('EN_CREATION', 'En création'),
    ]

    # Relations
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE,
                              related_name='acteurs')
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE,
                               related_name='acteurs')
    type_acteur = models.ForeignKey(TypeActeur, on_delete=models.PROTECT,
                                   related_name='acteurs')

    # Informations de base
    denomination = models.CharField(max_length=255,
                                   help_text="Nom de l'organisation")
    sigle = models.CharField(max_length=50, blank=True, null=True,
                            help_text="Sigle ou acronyme")
    description = models.TextField(blank=True, null=True)

    # Géolocalisation
    geom = gis_models.PointField(srid=4326,
                                help_text="Localisation du siège/local de l'organisation")
    adresse = models.CharField(max_length=255, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)

    # Composition
    nb_adherents = models.IntegerField(null=True, blank=True,
                                      help_text="Nombre de membres/adhérents")
    nb_femmes = models.IntegerField(null=True, blank=True,
                                   help_text="Nombre de femmes membres")
    nb_hommes = models.IntegerField(null=True, blank=True,
                                  help_text="Nombre d'hommes membres")
    nb_jeunes = models.IntegerField(null=True, blank=True,
                                   help_text="Nombre de jeunes (< 35 ans)")

    # Contact
    responsable = models.CharField(max_length=100, blank=True, null=True,
                                  help_text="Nom du responsable/président")
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Statut et dates
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES,
                            default='ACTIF')
    date_creation_org = models.DateField(null=True, blank=True,
                                        help_text="Date de création de l'organisation")
    date_reconnaissance = models.DateField(null=True, blank=True,
                                          help_text="Date de reconnaissance officielle")

    # Domaines d'activité
    domaines_activite = models.JSONField(default=list, blank=True,
                                        help_text="Liste des domaines d'activité")

    # Médias
    photo = models.ImageField(upload_to='acteurs/', null=True, blank=True,
                             help_text="Photo du groupe ou du local")

    # Métadonnées
    date_ajout = models.DateTimeField(default=timezone.now)
    actif = models.BooleanField(default=True)

    # Relations Many-to-Many avec Interventions (via InterventionActeur)
    interventions = models.ManyToManyField('suivi.Intervention',
                                          through='suivi.InterventionActeur',
                                          related_name='acteurs_impliques')

    class Meta:
        verbose_name = "Acteur"
        verbose_name_plural = "Acteurs"
        ordering = ['commune', 'denomination']
        indexes = [
            models.Index(fields=['projet', 'commune']),
            models.Index(fields=['type_acteur']),
        ]

    def __str__(self):
        sigle_str = f" ({self.sigle})" if self.sigle else ""
        return f"{self.denomination}{sigle_str} - {self.commune.nom}"
