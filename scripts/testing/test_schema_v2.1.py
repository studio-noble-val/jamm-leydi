#!/usr/bin/env python
"""
Test rapide du schema V2.1
Vérifier que les liens directs projet fonctionnent correctement
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamm_leydi.settings')
django.setup()

from suivi.models import Indicateur, Intervention
from core.models import Projet

print('\n' + '=' * 70)
print('VERIFICATION FINALE DU SCHEMA V2.1')
print('=' * 70)
print()

# Test 1 : Liste des projets
projets = Projet.objects.all()
print(f'Nombre de projets : {projets.count()}')
print()

for projet in projets:
    nb_ind = projet.indicateurs.count()
    nb_int = projet.interventions.count()
    print(f'  - {projet.code_projet}')
    print(f'      Indicateurs : {nb_ind}')
    print(f'      Interventions : {nb_int}')
print()

# Test 2 : Comparaison méthodes anciennes vs nouvelles
print('=' * 70)
print('TEST REQUETES SIMPLIFIEES')
print('=' * 70)
print()

jamm = Projet.objects.get(code_projet='JAMM-LEYDI-2024')

# Nouvelle méthode (directe)
nb_ind_direct = jamm.indicateurs.count()
nb_int_direct = jamm.interventions.count()

# Ancienne méthode (via thematiques)
nb_ind_via_them = Indicateur.objects.filter(thematique__projet=jamm).count()
nb_int_via_ind = Intervention.objects.filter(indicateur__thematique__projet=jamm).count()

print(f'Projet: {jamm.code_projet}')
print()
print('Indicateurs:')
print(f'  - Methode directe (NOUVELLE) : {nb_ind_direct}')
print(f'  - Via thematiques (ANCIENNE)  : {nb_ind_via_them}')
print(f'  - Resultat identique : {nb_ind_direct == nb_ind_via_them}')
print()
print('Interventions:')
print(f'  - Methode directe (NOUVELLE) : {nb_int_direct}')
print(f'  - Via indicateurs (ANCIENNE)  : {nb_int_via_ind}')
print(f'  - Resultat identique : {nb_int_direct == nb_int_via_ind}')
print()

# Test 3 : Cohérence des données
print('=' * 70)
print('TEST COHERENCE DES DONNEES')
print('=' * 70)
print()

errors = []

# Vérifier les indicateurs
for ind in Indicateur.objects.select_related('thematique__projet').all():
    if ind.projet_id != ind.thematique.projet_id:
        errors.append(f'Indicateur {ind.code}: projet incohérent')

# Vérifier les interventions
for inter in Intervention.objects.select_related('indicateur__projet').all():
    if inter.projet_id != inter.indicateur.projet_id:
        errors.append(f'Intervention {inter.id}: projet incohérent')

if errors:
    print('ERREURS DETECTEES:')
    for error in errors:
        print(f'  - {error}')
else:
    print('OK Toutes les donnees sont coherentes')
    print('OK Tous les indicateurs ont projet_id == thematique.projet_id')
    print('OK Toutes les interventions ont projet_id == indicateur.projet_id')

print()
print('=' * 70)
if not errors:
    print('SUCCES : SCHEMA V2.1 FONCTIONNE CORRECTEMENT')
else:
    print('ECHEC : DES INCOHERENCES ONT ETE DETECTEES')
print('=' * 70)
print()
