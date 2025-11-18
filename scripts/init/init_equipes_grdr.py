"""
Script pour initialiser les équipes GRDR
À exécuter avec: python init_equipes_grdr.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamm_leydi.settings')
django.setup()

from referentiels.models import EquipeGRDR


def init_equipes():
    """Créer les équipes GRDR de base"""

    equipes = [
        {
            'nom': 'Siège GRDR - Paris',
            'code': 'FR-PARIS',
            'type_equipe': 'SIEGE',
            'pays': 'France',
            'ville': 'Montreuil',
            'email': 'siege@grdr.org',
            'responsable': 'Direction Générale'
        },
        {
            'nom': 'Antenne Sénégal - Dakar',
            'code': 'SN-DAKAR',
            'type_equipe': 'ANTENNE',
            'pays': 'Sénégal',
            'ville': 'Dakar',
            'email': 'senegal@grdr.org',
        },
        {
            'nom': 'Antenne Sénégal - Kédougou',
            'code': 'SN-KEDOUGOU',
            'type_equipe': 'ANTENNE',
            'pays': 'Sénégal',
            'ville': 'Kédougou',
            'email': 'kedougou@grdr.org',
        },
        {
            'nom': 'Antenne Mali - Bamako',
            'code': 'ML-BAMAKO',
            'type_equipe': 'ANTENNE',
            'pays': 'Mali',
            'ville': 'Bamako',
            'email': 'mali@grdr.org',
        },
        {
            'nom': 'Bureau Mali - Kayes',
            'code': 'ML-KAYES',
            'type_equipe': 'BUREAU',
            'pays': 'Mali',
            'ville': 'Kayes',
        },
        {
            'nom': 'Antenne Mauritanie - Nouakchott',
            'code': 'MR-NOUAKCHOTT',
            'type_equipe': 'ANTENNE',
            'pays': 'Mauritanie',
            'ville': 'Nouakchott',
            'email': 'mauritanie@grdr.org',
        },
        {
            'nom': 'Coordination Afrique de l\'Ouest',
            'code': 'AO-COORD',
            'type_equipe': 'COORDINATION',
            'pays': 'Sénégal',
            'ville': 'Dakar',
            'email': 'coordination.ao@grdr.org',
        },
    ]

    created_count = 0
    updated_count = 0

    for eq_data in equipes:
        equipe, created = EquipeGRDR.objects.update_or_create(
            code=eq_data['code'],
            defaults=eq_data
        )

        if created:
            created_count += 1
            print(f"[OK] Creee: {equipe.nom}")
        else:
            updated_count += 1
            print(f"[UPDATE] Mise a jour: {equipe.nom}")

    print(f"\nResume: {created_count} equipe(s) creee(s), {updated_count} mise(s) a jour")
    print(f"Total: {EquipeGRDR.objects.count()} equipe(s) GRDR dans la base")


if __name__ == '__main__':
    print("Initialisation des equipes GRDR...")
    init_equipes()
    print("Termine!")
