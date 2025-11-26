# Migration manuelle : Migration des données existantes
# Étape 2 : Migrer les données de pays (FK) vers zone_pays (M2M)

from django.db import migrations


def migrate_pays_to_zone_pays(apps, schema_editor):
    """Migrer les pays existants vers le champ zone_pays ManyToMany"""
    Projet = apps.get_model('core', 'Projet')

    for projet in Projet.objects.all():
        # Si le projet a un pays défini (FK), l'ajouter à zone_pays (M2M)
        if projet.pays_id:
            projet.zone_pays.add(projet.pays_id)

    print(f"[OK] Migration des pays terminee pour {Projet.objects.count()} projets")


def reverse_migration(apps, schema_editor):
    """Restaurer les données dans pays depuis zone_pays si nécessaire"""
    Projet = apps.get_model('core', 'Projet')

    for projet in Projet.objects.all():
        # Si le projet a des pays dans zone_pays, prendre le premier
        if projet.zone_pays.exists():
            premier_pays = projet.zone_pays.first()
            projet.pays_id = premier_pays.id
            projet.save(update_fields=['pays'])

    print(f"[OK] Restauration des pays terminee pour {Projet.objects.count()} projets")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_add_zone_multi_levels'),
    ]

    operations = [
        migrations.RunPython(migrate_pays_to_zone_pays, reverse_migration),
    ]
