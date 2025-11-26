# Migration manuelle : Ajout des champs de zones multi-niveaux
# Étape 1 : Ajouter les nouveaux champs sans supprimer les anciens

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_projet_pays'),
        ('geo', '0004_admin4_admin5_admin7_admin8_alter_admin2_table_and_more'),
    ]

    operations = [
        # Ajouter les 5 nouveaux champs ManyToMany
        migrations.AddField(
            model_name='projet',
            name='zone_pays',
            field=models.ManyToManyField(
                blank=True,
                help_text="Pays de la zone d'intervention",
                related_name='projets_zone',
                to='geo.admin2'
            ),
        ),
        migrations.AddField(
            model_name='projet',
            name='zone_regions',
            field=models.ManyToManyField(
                blank=True,
                help_text="Régions de la zone d'intervention",
                related_name='projets_zone',
                to='geo.admin4'
            ),
        ),
        migrations.AddField(
            model_name='projet',
            name='zone_departements',
            field=models.ManyToManyField(
                blank=True,
                help_text="Départements de la zone d'intervention",
                related_name='projets_zone',
                to='geo.admin5'
            ),
        ),
        migrations.AddField(
            model_name='projet',
            name='zone_arrondissements',
            field=models.ManyToManyField(
                blank=True,
                help_text="Arrondissements de la zone d'intervention",
                related_name='projets_zone',
                to='geo.admin7'
            ),
        ),
        migrations.AddField(
            model_name='projet',
            name='zone_communes',
            field=models.ManyToManyField(
                blank=True,
                help_text="Communes de la zone d'intervention",
                related_name='projets_zone',
                to='geo.admin8'
            ),
        ),
    ]
