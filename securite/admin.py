"""
Administration des rapports de sécurité
"""
from django.contrib.gis import admin as gis_admin
from django.contrib import admin
from .models import TypeInsecurite, SecurityReport


@admin.register(TypeInsecurite)
class TypeInsecuriteAdmin(admin.ModelAdmin):
    """Administration des types d'insécurité"""
    list_display = ('code', 'libelle', 'gravite_defaut', 'couleur_hex', 'actif')
    list_filter = ('gravite_defaut', 'actif')
    search_fields = ('libelle', 'code')

    fieldsets = (
        ('Informations générales', {
            'fields': ('code', 'libelle', 'description')
        }),
        ('Paramètres', {
            'fields': ('gravite_defaut', 'couleur_hex', 'actif')
        })
    )


@gis_admin.register(SecurityReport)
class SecurityReportAdmin(gis_admin.GISModelAdmin):
    """Administration des rapports de sécurité"""
    list_display = ('libelle', 'type_insecurite', 'commune', 'gravite', 'statut', 'date_incident')
    list_filter = ('projet', 'type_insecurite', 'gravite', 'statut', 'commune', 'source_signalement')
    search_fields = ('libelle', 'description', 'village', 'parties_impliquees')
    autocomplete_fields = ['projet', 'type_insecurite', 'commune']
    readonly_fields = ('date_creation', 'date_modification', 'cree_par', 'modifie_par', 'date_signalement')

    fieldsets = (
        ('Informations générales', {
            'fields': ('libelle', 'description', 'type_insecurite')
        }),
        ('Rattachement', {
            'fields': ('projet', 'commune')
        }),
        ('Gravité et impact', {
            'fields': ('gravite', 'nb_personnes_affectees', 'impact_economique')
        }),
        ('Géolocalisation', {
            'fields': ('geom', 'village', 'lieu_dit')
        }),
        ('Dates', {
            'fields': ('date_incident', 'heure_incident', 'date_signalement')
        }),
        ('Parties impliquées', {
            'fields': ('parties_impliquees', 'temoins')
        }),
        ('Suivi et résolution', {
            'fields': ('statut', 'actions_entreprises', 'date_resolution', 'resolution_description')
        }),
        ('Source', {
            'fields': ('source_signalement', 'contact_signalant')
        }),
        ('Confidentialité', {
            'fields': ('confidentiel', 'notes_confidentielles'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'cree_par', 'date_modification', 'modifie_par'),
            'classes': ('collapse',)
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.cree_par = request.user
        else:
            obj.modifie_par = request.user
        super().save_model(request, obj, form, change)
