# Generated manually on 2025-11-11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_pays_equipe_to_projet'),
        ('referentiels', '0002_equipegrdr'),
    ]

    operations = [
        # Étape 1: Renommer l'ancien champ
        migrations.RenameField(
            model_name='projet',
            old_name='equipe_grdr',
            new_name='equipe_grdr_old',
        ),
        # Étape 2: Créer le nouveau champ ForeignKey
        migrations.AddField(
            model_name='projet',
            name='equipe_grdr',
            field=models.ForeignKey(
                blank=True,
                help_text='Équipe GRDR de rattachement',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='projets',
                to='referentiels.equipegrdr'
            ),
        ),
        # Étape 3: Supprimer l'ancien champ (les données texte seront perdues)
        migrations.RemoveField(
            model_name='projet',
            name='equipe_grdr_old',
        ),
    ]
