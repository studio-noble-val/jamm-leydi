# Migration manuelle : Nettoyage des anciens champs
# Étape 3 : Supprimer les anciens champs pays (FK) et zone_intervention (CharField)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_migrate_zone_data'),
    ]

    operations = [
        # Supprimer l'ancien champ pays (ForeignKey)
        migrations.RemoveField(
            model_name='projet',
            name='pays',
        ),
        # Supprimer l'ancien champ zone_intervention (CharField)
        migrations.RemoveField(
            model_name='projet',
            name='zone_intervention',
        ),
    ]
