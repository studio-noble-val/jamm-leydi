"""
Administration des modèles core (Users, Projets)
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Projet, UserProjet


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administration personnalisée du modèle User"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'organisation', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'organisation')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'organisation')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('telephone', 'organisation')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('telephone', 'organisation')
        }),
    )


class UserProjetInline(admin.TabularInline):
    """Inline pour gérer les utilisateurs d'un projet"""
    model = UserProjet
    extra = 1
    autocomplete_fields = ['user']


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    """Administration des projets"""
    list_display = ('code_projet', 'libelle', 'date_debut', 'date_fin', 'statut', 'actif')
    list_filter = ('statut', 'actif', 'date_debut')
    search_fields = ('code_projet', 'libelle', 'bailleurs')
    readonly_fields = ('date_creation',)
    inlines = [UserProjetInline]

    fieldsets = (
        ('Informations générales', {
            'fields': ('code_projet', 'libelle', 'description', 'equipe_grdr')
        }),
        ('Localisation et zone', {
            'fields': ('pays', 'zone_intervention')
        }),
        ('Bailleurs', {
            'fields': ('bailleurs',)
        }),
        ('Planning', {
            'fields': ('date_debut', 'date_fin', 'statut')
        }),
        ('Budget', {
            'fields': ('budget', 'devise'),
            'classes': ('collapse',)
        }),
        ('Médias', {
            'fields': ('logo',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'actif'),
            'classes': ('collapse',)
        })
    )


@admin.register(UserProjet)
class UserProjetAdmin(admin.ModelAdmin):
    """Administration des relations User-Projet"""
    list_display = ('user', 'projet', 'role', 'actif', 'date_ajout')
    list_filter = ('role', 'actif', 'projet')
    search_fields = ('user__username', 'user__email', 'projet__code_projet')
    autocomplete_fields = ['user', 'projet']
    readonly_fields = ('date_ajout',)

    fieldsets = (
        ('Affectation', {
            'fields': ('user', 'projet', 'role')
        }),
        ('Statut', {
            'fields': ('actif', 'date_ajout')
        })
    )
