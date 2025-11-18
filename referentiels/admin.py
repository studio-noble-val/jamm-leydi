"""
Administration des référentiels mutualisés
"""
from django.contrib.gis import admin as gis_admin
from django.contrib import admin
from .models import (
    Commune, CommuneGeom, ChefLieu, ProjetCommune,
    TypeIntervention, TypeInfrastructure, TypeActeur,
    EquipeGRDR
)


class CommuneGeomInline(admin.StackedInline):
    """Inline pour la géométrie de la commune"""
    model = CommuneGeom
    extra = 0


class ChefLieuInline(admin.StackedInline):
    """Inline pour le chef-lieu"""
    model = ChefLieu
    extra = 0


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    """Administration des communes"""
    list_display = ('nom', 'code_commune', 'region', 'departement', 'population')
    list_filter = ('region', 'departement')
    search_fields = ('nom', 'code_commune', 'region')
    inlines = [CommuneGeomInline, ChefLieuInline]

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'code_commune')
        }),
        ('Localisation administrative', {
            'fields': ('departement', 'region')
        }),
        ('Démographie', {
            'fields': ('population', 'annee_recensement')
        })
    )


@gis_admin.register(CommuneGeom)
class CommuneGeomAdmin(gis_admin.GISModelAdmin):
    """Administration des géométries des communes"""
    list_display = ('commune', 'superficie')
    search_fields = ('commune__nom',)
    readonly_fields = ('centroid',)


@gis_admin.register(ChefLieu)
class ChefLieuAdmin(gis_admin.GISModelAdmin):
    """Administration des chefs-lieux"""
    list_display = ('nom', 'commune')
    search_fields = ('nom', 'commune__nom')


@admin.register(ProjetCommune)
class ProjetCommuneAdmin(admin.ModelAdmin):
    """Administration des relations Projet-Commune"""
    list_display = ('projet', 'commune', 'prioritaire', 'date_ajout')
    list_filter = ('projet', 'prioritaire')
    search_fields = ('projet__code_projet', 'commune__nom')
    autocomplete_fields = ['projet', 'commune']
    readonly_fields = ('date_ajout',)


@admin.register(TypeIntervention)
class TypeInterventionAdmin(admin.ModelAdmin):
    """Administration des types d'interventions"""
    list_display = ('code', 'libelle', 'couleur_hex', 'actif')
    list_filter = ('actif',)
    search_fields = ('libelle', 'code')

    fieldsets = (
        ('Informations générales', {
            'fields': ('code', 'libelle', 'description')
        }),
        ('Affichage', {
            'fields': ('couleur_hex', 'actif')
        })
    )


@admin.register(TypeInfrastructure)
class TypeInfrastructureAdmin(admin.ModelAdmin):
    """Administration des types d'infrastructures"""
    list_display = ('code', 'libelle', 'icone_poi', 'couleur_hex', 'actif')
    list_filter = ('actif',)
    search_fields = ('libelle', 'code')

    fieldsets = (
        ('Informations générales', {
            'fields': ('code', 'libelle', 'description')
        }),
        ('Affichage cartographique', {
            'fields': ('icone_poi', 'couleur_hex', 'actif')
        })
    )


@admin.register(TypeActeur)
class TypeActeurAdmin(admin.ModelAdmin):
    """Administration des types d'acteurs"""
    list_display = ('code', 'libelle', 'icone_poi', 'couleur_hex', 'actif')
    list_filter = ('actif',)
    search_fields = ('libelle', 'code')

    fieldsets = (
        ('Informations générales', {
            'fields': ('code', 'libelle', 'description')
        }),
        ('Affichage cartographique', {
            'fields': ('icone_poi', 'couleur_hex', 'actif')
        })
    )


@admin.register(EquipeGRDR)
class EquipeGRDRAdmin(admin.ModelAdmin):
    """Administration des équipes GRDR"""
    list_display = ('nom', 'code', 'type_equipe', 'pays', 'ville', 'responsable', 'actif')
    list_filter = ('type_equipe', 'pays', 'actif')
    search_fields = ('nom', 'code', 'pays', 'ville', 'responsable')

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'code', 'type_equipe')
        }),
        ('Localisation', {
            'fields': ('pays', 'ville')
        }),
        ('Contact', {
            'fields': ('email', 'telephone', 'responsable')
        }),
        ('Statut', {
            'fields': ('actif', 'date_creation'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('date_creation',)
