# Migration étape 2 : Migrer les données de l'ancien vers le nouveau champ

from django.db import migrations


def migrate_pays_data(apps, schema_editor):
    """
    Migrer les données du champ pays (CharField) vers pays_admin2 (ForeignKey)
    """
    Projet = apps.get_model('core', 'Projet')

    # Pour chaque projet, essayer de mapper le pays texte vers Admin2
    db_alias = schema_editor.connection.alias

    for projet in Projet.objects.using(db_alias).all():
        if projet.pays:
            pays_name = projet.pays.strip()

            # Mapper vers l'ID Admin2 correspondant
            # Sénégal = ID 2 (d'après check_tables.py)
            pays_mapping = {
                'Sénégal': 2,
                'Mali': None,  # À compléter si nécessaire
                'Mauritanie': 3,
                'France': None,
            }

            if pays_name in pays_mapping and pays_mapping[pays_name]:
                # Utiliser une requête UPDATE directe
                schema_editor.execute(
                    "UPDATE core_projet SET pays_admin2_id = %s WHERE id = %s",
                    [pays_mapping[pays_name], projet.id]
                )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_step1_add_new_fields'),
    ]

    operations = [
        migrations.RunPython(migrate_pays_data, reverse_code=migrations.RunPython.noop),
    ]
