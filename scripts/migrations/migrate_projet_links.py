#!/usr/bin/env python
"""
Script de migration des données après ajout des FK vers Projet
dans les modèles Indicateur et Intervention

Ce script doit être exécuté APRÈS la migration Django
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamm_leydi.settings')
django.setup()

from suivi.models import Indicateur, Intervention


def migrate_indicateurs():
    """
    Remplir le champ projet pour tous les indicateurs existants
    à partir de leur thématique
    """
    print("=" * 70)
    print("MIGRATION DES INDICATEURS")
    print("=" * 70)
    print()

    indicateurs = Indicateur.objects.select_related('thematique__projet').all()
    total = indicateurs.count()

    if total == 0:
        print("Aucun indicateur à migrer")
        return

    print(f"Nombre d'indicateurs à traiter : {total}")
    print()

    updated = 0
    for indicateur in indicateurs:
        if not indicateur.projet_id:
            indicateur.projet = indicateur.thematique.projet
            indicateur.save(update_fields=['projet'])
            updated += 1
            print(f"  OK {indicateur.code} -> Projet: {indicateur.projet.code_projet}")

    print()
    print(f"Total indicateurs mis à jour : {updated}/{total}")
    print()


def migrate_interventions():
    """
    Remplir le champ projet pour toutes les interventions existantes
    à partir de leur indicateur
    """
    print("=" * 70)
    print("MIGRATION DES INTERVENTIONS")
    print("=" * 70)
    print()

    interventions = Intervention.objects.select_related(
        'indicateur__thematique__projet'
    ).all()
    total = interventions.count()

    if total == 0:
        print("Aucune intervention à migrer")
        return

    print(f"Nombre d'interventions à traiter : {total}")
    print()

    updated = 0
    for intervention in interventions:
        if not intervention.projet_id:
            intervention.projet = intervention.indicateur.thematique.projet
            intervention.save(update_fields=['projet'])
            updated += 1
            if updated <= 10:  # Afficher les 10 premières
                print(f"  OK {intervention.id} -> Projet: {intervention.projet.code_projet}")
            elif updated == 11:
                print(f"  ... ({total - 10} autres interventions)")

    print()
    print(f"Total interventions mises à jour : {updated}/{total}")
    print()


def verify_integrity():
    """
    Vérifier l'intégrité des données après migration
    """
    print("=" * 70)
    print("VERIFICATION DE L'INTEGRITE")
    print("=" * 70)
    print()

    # Vérifier les indicateurs
    errors_indicateurs = []
    for indicateur in Indicateur.objects.select_related('thematique__projet').all():
        if indicateur.projet_id != indicateur.thematique.projet_id:
            errors_indicateurs.append(
                f"Indicateur {indicateur.code}: projet_id={indicateur.projet_id} "
                f"mais thematique.projet_id={indicateur.thematique.projet_id}"
            )

    if errors_indicateurs:
        print("ERREURS DETECTEES DANS LES INDICATEURS:")
        for error in errors_indicateurs:
            print(f"  - {error}")
    else:
        print("OK Tous les indicateurs ont un projet coherent avec leur thematique")

    print()

    # Vérifier les interventions
    errors_interventions = []
    for intervention in Intervention.objects.select_related(
        'indicateur__thematique__projet'
    ).all():
        if intervention.projet_id != intervention.indicateur.thematique.projet_id:
            errors_interventions.append(
                f"Intervention {intervention.id}: projet_id={intervention.projet_id} "
                f"mais indicateur.projet_id={intervention.indicateur.thematique.projet_id}"
            )

    if errors_interventions:
        print("ERREURS DETECTEES DANS LES INTERVENTIONS:")
        for error in errors_interventions:
            print(f"  - {error}")
    else:
        print("OK Toutes les interventions ont un projet coherent avec leur indicateur")

    print()

    if errors_indicateurs or errors_interventions:
        print("ATTENTION: Des erreurs d'integrite ont ete detectees !")
        return False
    else:
        print("SUCCES: Toutes les donnees sont coherentes")
        return True


def main():
    print()
    print("=" * 70)
    print("MIGRATION DES LIENS VERS PROJET")
    print("Script de mise à jour des données après modification du schéma")
    print("=" * 70)
    print()

    try:
        # Étape 1 : Migrer les indicateurs
        migrate_indicateurs()

        # Étape 2 : Migrer les interventions
        migrate_interventions()

        # Étape 3 : Vérifier l'intégrité
        success = verify_integrity()

        print("=" * 70)
        if success:
            print("MIGRATION TERMINEE AVEC SUCCES")
        else:
            print("MIGRATION TERMINEE AVEC DES ERREURS")
        print("=" * 70)
        print()

    except Exception as e:
        print()
        print("ERREUR LORS DE LA MIGRATION:")
        print(f"  {e}")
        print()
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
