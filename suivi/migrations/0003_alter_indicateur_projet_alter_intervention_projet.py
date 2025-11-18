# Generated manually on 2025-11-10 09:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_pays_equipe_to_projet'),
        ('suivi', '0002_alter_indicateur_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicateur',
            name='projet',
            field=models.ForeignKey(help_text='Projet auquel appartient cet indicateur', on_delete=django.db.models.deletion.CASCADE, related_name='indicateurs', to='core.projet'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='projet',
            field=models.ForeignKey(help_text='Projet auquel appartient cette intervention', on_delete=django.db.models.deletion.CASCADE, related_name='interventions', to='core.projet'),
        ),
    ]
