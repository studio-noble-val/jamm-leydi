"""
Administration des entités géolocalisées
"""
from django.contrib.gis import admin as gis_admin
from .models import Infrastructure, Acteur


@gis_admin.register(Infrastructure)
class InfrastructureAdmin(gis_admin.GISModelAdmin):
    """Administration des infrastructures"""
    list_display = ('nom', 'type_infrastructure', 'commune', 'projet', 'statut', 'nb_beneficiaires')
    list_filter = ('projet', 'type_infrastructure', 'statut', 'commune')
    search_fields = ('nom', 'description', 'village', 'adresse')
    autocomplete_fields = ['projet', 'commune', 'type_infrastructure']
    readonly_fields = ('date_creation',)

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'type_infrastructure')
        }),
        ('Rattachement', {
            'fields': ('projet', 'commune')
        }),
        ('Géolocalisation', {
            'fields': ('geom', 'adresse', 'village')
        }),
        ('Bénéficiaires', {
            'fields': ('nb_beneficiaires', 'nb_beneficiaires_indirects')
        }),
        ('Statut et dates', {
            'fields': ('statut', 'date_construction', 'date_mise_en_service')
        }),
        ('Caractéristiques techniques', {
            'fields': ('caracteristiques', 'cout_construction'),
            'classes': ('collapse',)
        }),
        ('Médias', {
            'fields': ('photo',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'actif'),
            'classes': ('collapse',)
        })
    )


@gis_admin.register(Acteur)
class ActeurAdmin(gis_admin.GISModelAdmin):
    """Administration des acteurs/organisations"""
    list_display = ('denomination', 'sigle', 'type_acteur', 'commune', 'projet', 'statut', 'nb_adherents')
    list_filter = ('projet', 'type_acteur', 'statut', 'commune')
    search_fields = ('denomination', 'sigle', 'responsable', 'village')
    autocomplete_fields = ['projet', 'commune', 'type_acteur']
    readonly_fields = ('date_ajout',)

    fieldsets = (
        ('Informations générales', {
            'fields': ('denomination', 'sigle', 'description', 'type_acteur')
        }),
        ('Rattachement', {
            'fields': ('projet', 'commune')
        }),
        ('Géolocalisation', {
            'fields': ('geom', 'adresse', 'village')
        }),
        ('Composition', {
            'fields': ('nb_adherents', 'nb_femmes', 'nb_hommes', 'nb_jeunes')
        }),
        ('Contact', {
            'fields': ('responsable', 'telephone', 'email')
        }),
        ('Statut et dates', {
            'fields': ('statut', 'date_creation_org', 'date_reconnaissance')
        }),
        ('Activités', {
            'fields': ('domaines_activite',),
            'classes': ('collapse',)
        }),
        ('Médias', {
            'fields': ('photo',)
        }),
        ('Métadonnées', {
            'fields': ('date_ajout', 'actif'),
            'classes': ('collapse',)
        })
    )
