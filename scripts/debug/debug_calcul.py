"""
Script de débogage pour comprendre le calcul des pourcentages des thématiques
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamm_leydi.settings')
django.setup()

from django.db.models import Sum
from suivi.models import Thematique, Indicateur, CibleIndicateur, Intervention

# Récupérer le projet JAMM LEYDI
from core.models import Projet
projet = Projet.objects.get(code_projet='JAMM-LEYDI-2024')

print("="*80)
print(f"ANALYSE DES CALCULS POUR {projet.code_projet}")
print("="*80)

# Analyser chaque thématique
thematiques = Thematique.objects.filter(projet=projet).order_by('ordre')

for thematique in thematiques:
    print(f"\n{'='*80}")
    print(f"THÉMATIQUE: {thematique.code} - {thematique.libelle}")
    print(f"{'='*80}")

    # Récupérer les indicateurs de cette thématique
    indicateurs = Indicateur.objects.filter(thematique=thematique)
    print(f"\nNombre d'indicateurs: {indicateurs.count()}")

    for indicateur in indicateurs:
        print(f"\n  Indicateur {indicateur.code}: {indicateur.libelle}")

        # Cibles pour cet indicateur
        cibles = CibleIndicateur.objects.filter(
            indicateur=indicateur,
            annee=2025
        )
        total_cible = cibles.aggregate(total=Sum('valeur_cible'))['total'] or 0
        print(f"    Cible 2025: {total_cible}")

        # Détail par commune
        for cible in cibles:
            print(f"      - {cible.commune.nom}: {cible.valeur_cible}")

        # Interventions terminées pour cet indicateur
        interventions = Intervention.objects.filter(
            indicateur=indicateur,
            statut='TERMINE'
        )
        total_realise = interventions.aggregate(total=Sum('valeur_quantitative'))['total'] or 0
        print(f"    Réalisé: {total_realise}")
        print(f"    Nombre d'interventions TERMINE: {interventions.count()}")

        # Détail des interventions
        for intervention in interventions:
            print(f"      - {intervention.libelle}: {intervention.valeur_quantitative} ({intervention.commune.nom})")

    # Calcul global pour la thématique
    print(f"\n  {'~'*60}")
    total_cible_thematique = CibleIndicateur.objects.filter(
        indicateur__in=indicateurs,
        annee=2025
    ).aggregate(total=Sum('valeur_cible'))['total'] or 0

    total_realise_thematique = Intervention.objects.filter(
        indicateur__in=indicateurs,
        statut='TERMINE'
    ).aggregate(total=Sum('valeur_quantitative'))['total'] or 0

    if total_cible_thematique > 0:
        pourcentage = round((total_realise_thematique / total_cible_thematique) * 100, 1)
    else:
        pourcentage = 0

    print(f"  TOTAL THÉMATIQUE:")
    print(f"    Cible totale: {total_cible_thematique}")
    print(f"    Réalisé total: {total_realise_thematique}")
    print(f"    Pourcentage: {pourcentage}%")

print(f"\n{'='*80}")
print("FIN DE L'ANALYSE")
print("="*80)
