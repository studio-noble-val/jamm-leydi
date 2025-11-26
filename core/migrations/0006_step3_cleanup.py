# Migration étape 3 : Supprimer les anciens champs et renommer

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_step2_migrate_data'),
    ]

    operations = [
        # Supprimer l'ancien champ equipe_grdr
        migrations.RemoveField(
            model_name='projet',
            name='equipe_grdr',
        ),

        # Supprimer l'ancien champ pays (VARCHAR)
        migrations.RemoveField(
            model_name='projet',
            name='pays',
        ),

        # Renommer pays_admin2 en pays
        migrations.RenameField(
            model_name='projet',
            old_name='pays_admin2',
            new_name='pays',
        ),
    ]
