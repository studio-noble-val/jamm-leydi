"""
Modèles de référentiels mutualisés entre projets
"""
from django.contrib.gis.db import models as gis_models
from django.db import models
from core.models import Projet


class Commune(models.Model):
    """
    Référentiel national des communes du Sénégal
    Mutualisé entre plusieurs projets
    """
    nom = models.CharField(max_length=100)
    code_commune = models.CharField(max_length=20, unique=True,
                                   help_text="Code officiel de la commune")
    departement = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    population = models.IntegerField(null=True, blank=True,
                                    help_text="Population recensée")
    annee_recensement = models.IntegerField(null=True, blank=True,
                                           help_text="Année du dernier recensement")

    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.code_commune})"


class CommuneGeom(gis_models.Model):
    """
    Géométries (contours) des communes
    Séparé pour optimisation des requêtes spatiales
    """
    commune = models.OneToOneField(Commune, on_delete=models.CASCADE,
                                  related_name='geometrie')
    geom = gis_models.MultiPolygonField(srid=4326,
                                       help_text="Contour administratif de la commune")
    centroid = gis_models.PointField(srid=4326, null=True, blank=True,
                                    help_text="Centroïde calculé automatiquement")
    superficie = models.FloatField(null=True, blank=True,
                                  help_text="Superficie en km²")

    class Meta:
        verbose_name = "Géométrie de commune"
        verbose_name_plural = "Géométries des communes"

    def __str__(self):
        return f"Géométrie de {self.commune.nom}"

    def save(self, *args, **kwargs):
        """Calcul automatique du centroïde"""
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid
        super().save(*args, **kwargs)


class ChefLieu(gis_models.Model):
    """
    Chef-lieu (point) des communes
    """
    commune = models.OneToOneField(Commune, on_delete=models.CASCADE,
                                  related_name='chef_lieu')
    nom = models.CharField(max_length=100,
                          help_text="Nom du chef-lieu (peut différer de la commune)")
    geom = gis_models.PointField(srid=4326)

    class Meta:
        verbose_name = "Chef-lieu"
        verbose_name_plural = "Chefs-lieux"

    def __str__(self):
        return f"Chef-lieu de {self.commune.nom}: {self.nom}"


class ProjetCommune(models.Model):
    """
    Table de liaison entre Projet et Commune
    Un projet peut concerner plusieurs communes
    """
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE,
                              related_name='projet_communes')
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE,
                               related_name='commune_projets')

    # Métadonnées spécifiques au projet-commune
    date_ajout = models.DateTimeField(auto_now_add=True)
    prioritaire = models.BooleanField(default=False,
                                     help_text="Commune prioritaire pour ce projet")

    class Meta:
        verbose_name = "Projet-Commune"
        verbose_name_plural = "Projets-Communes"
        unique_together = ['projet', 'commune']
        ordering = ['projet', 'commune']

    def __str__(self):
        return f"{self.projet.code_projet} - {self.commune.nom}"


class TypeIntervention(models.Model):
    """
    Types d'interventions/activités
    Ex: Rencontres, Agro-sylvo-pastorales, Économiques, Hydrauliques, Cantines, Santé
    """
    libelle = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True,
                           help_text="Code court (ex: ASP, ECO, HYD...)")
    description = models.TextField(blank=True, null=True)
    couleur_hex = models.CharField(max_length=7, default="#0066CC",
                                  help_text="Couleur pour les graphiques (ex: #FF5733)")

    # Permet d'activer/désactiver des types selon les projets
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Type d'intervention"
        verbose_name_plural = "Types d'interventions"
        ordering = ['libelle']

    def __str__(self):
        return f"{self.code} - {self.libelle}"


class TypeInfrastructure(models.Model):
    """
    Types d'infrastructures
    Ex: Forage, École, Maraîchage, Cantine scolaire, Poste de santé...
    """
    libelle = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    # Icône pour la cartographie (FontAwesome ou nom de fichier)
    icone_poi = models.CharField(max_length=50, default="map-marker",
                                help_text="Nom de l'icône FontAwesome ou chemin fichier")
    couleur_hex = models.CharField(max_length=7, default="#28A745",
                                  help_text="Couleur du marqueur sur la carte")

    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Type d'infrastructure"
        verbose_name_plural = "Types d'infrastructures"
        ordering = ['libelle']

    def __str__(self):
        return f"{self.code} - {self.libelle}"


class TypeActeur(models.Model):
    """
    Types d'acteurs/organisations
    Ex: Groupement féminin, Association d'éleveurs, Coopérative agricole, Comité de gestion...
    """
    libelle = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    # Icône pour la cartographie
    icone_poi = models.CharField(max_length=50, default="users",
                                help_text="Nom de l'icône FontAwesome")
    couleur_hex = models.CharField(max_length=7, default="#FFC107",
                                  help_text="Couleur du marqueur")

    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Type d'acteur"
        verbose_name_plural = "Types d'acteurs"
        ordering = ['libelle']

    def __str__(self):
        return f"{self.code} - {self.libelle}"


class EquipeGRDR(models.Model):
    """
    Équipes GRDR (antennes, sièges, bureaux)
    Ex: Antenne Sénégal - Kédougou, Siège Paris, Bureau Mali - Kayes, etc.
    """
    TYPE_CHOICES = [
        ('SIEGE', 'Siège'),
        ('ANTENNE', 'Antenne'),
        ('BUREAU', 'Bureau'),
        ('COORDINATION', 'Coordination'),
    ]

    nom = models.CharField(max_length=200, unique=True,
                          help_text="Ex: Antenne Sénégal - Kédougou")
    code = models.CharField(max_length=50, unique=True,
                           help_text="Code court (ex: SN-KED, FR-PARIS)")
    type_equipe = models.CharField(max_length=20, choices=TYPE_CHOICES, default='ANTENNE')

    # Localisation
    pays = models.CharField(max_length=100,
                           help_text="Pays d'implantation")
    ville = models.CharField(max_length=100, blank=True, null=True)

    # Contact
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)

    # Responsable
    responsable = models.CharField(max_length=200, blank=True, null=True,
                                  help_text="Nom du responsable de l'équipe")

    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Équipe GRDR"
        verbose_name_plural = "Équipes GRDR"
        ordering = ['type_equipe', 'pays', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.get_type_equipe_display()})"
