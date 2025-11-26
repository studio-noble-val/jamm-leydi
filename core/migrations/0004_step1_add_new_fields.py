# Migration étape 1 : Ajouter les nouveaux champs sans toucher aux anciens

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_equipe_grdr_to_foreignkey'),
        ('geo', '0003_admin2_cellulesgrdr'),
    ]

    operations = [
        # Ajouter le nouveau champ cellule_grdr
        migrations.AddField(
            model_name='projet',
            name='cellule_grdr',
            field=models.ForeignKey(
                blank=True,
                help_text='Cellule GRDR de rattachement',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='projets',
                to='geo.cellulesgrdr',
                db_constraint=False
            ),
        ),

        # Ajouter un nouveau champ pays_admin2 (temporaire)
        migrations.AddField(
            model_name='projet',
            name='pays_admin2',
            field=models.ForeignKey(
                blank=True,
                help_text="Pays d'intervention (niveau Admin2)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='projets_admin2',
                to='geo.admin2',
                db_constraint=False
            ),
        ),

        # Modifier code_projet pour auto-génération
        migrations.AlterField(
            model_name='projet',
            name='code_projet',
            field=models.CharField(
                blank=True,
                editable=False,
                help_text='Code unique auto-généré (ex: PROJ-1)',
                max_length=50,
                unique=True
            ),
        ),
    ]
