"""
Administration des entités géolocalisées
"""
from django.contrib.gis import admin as gis_admin
from django.contrib import admin
from .models import Infrastructure, Acteur, Admin2, CellulesGRDR


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


@admin.register(Admin2)
class Admin2Admin(gis_admin.GISModelAdmin):
    """
    Administration des pays (niveau Admin2 OSM)
    Table en lecture seule (managed=False)
    """
    list_display = ('id', 'name', 'admin_leve', 'boundary')
    search_fields = ('name', 'osm_id')
    list_filter = ('admin_leve', 'boundary')
    readonly_fields = ('id', 'osm_id', 'osm_way_id', 'name', 'type', 'admin_leve',
                       'boundary', 'place', 'other_tags')

    # Vue en lecture seule
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CellulesGRDR)
class CellulesGRDRAdmin(gis_admin.GISModelAdmin):
    """
    Administration des cellules GRDR
    Table en lecture seule (managed=False)
    """
    list_display = ('id', 'nom')
    search_fields = ('nom',)
    readonly_fields = ('id', 'nom', 'geom')

    # Vue en lecture seule
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
