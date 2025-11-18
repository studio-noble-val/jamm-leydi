"""
Administration des modèles de suivi (indicateurs, interventions)
"""
from django.contrib.gis import admin as gis_admin
from django.contrib import admin
from django import forms
from .models import (
    Thematique, Indicateur, CibleIndicateur, Intervention,
    ValeurIndicateur, InterventionActeur, InterventionInfrastructure
)


class InterventionAdminForm(forms.ModelForm):
    """Formulaire personnalisé pour l'admin Intervention"""
    class Meta:
        model = Intervention
        fields = '__all__'


class IndicateurInline(admin.TabularInline):
    """Inline pour les indicateurs d'une thématique"""
    model = Indicateur
    extra = 1
    fields = ('code', 'libelle', 'unite_mesure', 'type_calcul', 'ordre')


@admin.register(Thematique)
class ThematiqueAdmin(admin.ModelAdmin):
    """Administration des thématiques"""
    list_display = ('code', 'libelle', 'projet', 'ordre')
    list_filter = ('projet',)
    search_fields = ('code', 'libelle', 'projet__code_projet')
    inlines = [IndicateurInline]


class CibleIndicateurInline(admin.TabularInline):
    """Inline pour les cibles d'un indicateur"""
    model = CibleIndicateur
    extra = 1
    fields = ('commune', 'valeur_cible', 'annee')


@admin.register(Indicateur)
class IndicateurAdmin(admin.ModelAdmin):
    """Administration des indicateurs"""
    list_display = ('code', 'libelle', 'thematique', 'unite_mesure', 'type_calcul')
    list_filter = ('thematique__projet', 'thematique', 'type_calcul')
    search_fields = ('code', 'libelle')
    inlines = [CibleIndicateurInline]

    fieldsets = (
        ('Informations générales', {
            'fields': ('thematique', 'code', 'libelle', 'description')
        }),
        ('Mesure', {
            'fields': ('unite_mesure', 'type_calcul')
        }),
        ('Affichage', {
            'fields': ('ordre',)
        })
    )


@admin.register(CibleIndicateur)
class CibleIndicateurAdmin(admin.ModelAdmin):
    """Administration des cibles d'indicateurs"""
    list_display = ('indicateur', 'commune', 'valeur_cible', 'annee')
    list_filter = ('indicateur__thematique__projet', 'annee', 'commune')
    search_fields = ('indicateur__code', 'indicateur__libelle')


@gis_admin.register(Intervention)
class InterventionAdmin(gis_admin.GISModelAdmin):
    """Administration des interventions"""
    form = InterventionAdminForm
    list_display = ('libelle', 'nature', 'indicateur', 'commune', 'date_intervention', 'statut')
    list_filter = ('nature', 'type_intervention', 'statut', 'commune', 'indicateur__thematique')
    search_fields = ('libelle', 'description')
    readonly_fields = ('date_creation', 'date_validation', 'valide_par', 'get_projet')
    autocomplete_fields = ['indicateur', 'type_intervention', 'commune']

    # Configuration du widget OpenLayers pour la carte
    default_lon = -12.0  # Longitude centre Sénégal
    default_lat = 14.0   # Latitude centre Sénégal
    default_zoom = 8

    # Mode de dessin : drag-and-drop au lieu de click-and-follow
    point_zoom = 10
    map_width = 800
    map_height = 500

    # Utiliser le mode "modify" pour déplacer les points existants
    modifiable = True

    class Media:
        css = {
            'all': ('admin/css/intervention_map.css',)
        }
        js = ('admin/js/intervention_map.js',)

    fieldsets = (
        ('Informations générales', {
            'fields': ('libelle', 'description', 'nature', 'type_intervention')
        }),
        ('Rattachement', {
            'fields': ('get_projet', 'indicateur', 'commune')
        }),
        ('Valeur quantitative', {
            'fields': ('valeur_quantitative', 'date_intervention')
        }),
        ('Géolocalisation', {
            'fields': ('geom',),
            'description': 'Cliquez sur la carte pour localiser précisément cette intervention'
        }),
        ('Statut', {
            'fields': ('statut', 'notes')
        }),
        ('Médias', {
            'fields': ('photo',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'cree_par', 'valide_par', 'date_validation'),
            'classes': ('collapse',)
        })
    )

    def get_projet(self, obj):
        """Afficher le projet (calculé depuis l'indicateur)"""
        if obj.indicateur:
            return obj.indicateur.projet
        return obj.projet if hasattr(obj, 'projet') and obj.projet else "Non défini"
    get_projet.short_description = "Projet"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.cree_par = request.user
            # Remplir automatiquement le projet depuis l'indicateur
            if obj.indicateur:
                obj.projet = obj.indicateur.projet

        # Nettoyer le champ geom s'il est vide ou invalide
        if 'geom' in form.cleaned_data and not form.cleaned_data['geom']:
            obj.geom = None

        if obj.statut == 'VALIDE' and not obj.valide_par:
            obj.valide_par = request.user
            from django.utils import timezone
            obj.date_validation = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ValeurIndicateur)
class ValeurIndicateurAdmin(admin.ModelAdmin):
    """Administration des valeurs d'indicateurs"""
    list_display = ('indicateur', 'commune', 'valeur_realisee', 'date_mesure', 'source', 'statut')
    list_filter = ('indicateur__thematique__projet', 'indicateur', 'source', 'statut', 'commune')
    search_fields = ('indicateur__code', 'indicateur__libelle')
    readonly_fields = ('date_saisie', 'saisi_par')
    autocomplete_fields = ['indicateur', 'commune']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.saisi_par = request.user
        super().save_model(request, obj, form, change)


@admin.register(InterventionActeur)
class InterventionActeurAdmin(admin.ModelAdmin):
    """Administration des relations Intervention-Acteur"""
    list_display = ('intervention', 'acteur', 'role')
    autocomplete_fields = ['intervention', 'acteur']


@admin.register(InterventionInfrastructure)
class InterventionInfrastructureAdmin(admin.ModelAdmin):
    """Administration des relations Intervention-Infrastructure"""
    list_display = ('intervention', 'infrastructure')
    autocomplete_fields = ['intervention', 'infrastructure']
