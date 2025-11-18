from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Count, Sum
from referentiels.models import Commune
from suivi.models import Indicateur, Intervention, ValeurIndicateur


@login_required
def dashboard_home(request):
    """Page d'accueil du tableau de bord administrateur"""

    # Récupérer le projet depuis la session
    projet_id = request.session.get('projet_id')

    # Filtrer par projet si disponible
    if projet_id:
        from suivi.models import Thematique, CibleIndicateur
        from core.models import Projet

        projet = Projet.objects.get(id=projet_id)
        interventions = Intervention.objects.filter(projet_id=projet_id)
        indicateurs_filter = {'indicateur__projet_id': projet_id}

        # KPI 1 : Interventions réalisées
        interventions_realisees = interventions.filter(statut='TERMINE').count()

        # Interventions réalisées ce mois
        from datetime import datetime, timedelta
        debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        interventions_ce_mois = interventions.filter(
            statut='TERMINE',
            date_intervention__gte=debut_mois
        ).count()

        # KPI 2 : Bénéficiaires touchés (somme des valeur_quantitative des interventions terminées)
        beneficiaires_touches = interventions.filter(statut='TERMINE').aggregate(
            total=Sum('valeur_quantitative')
        )['total'] or 0

        # Statistiques par thématique
        thematiques = Thematique.objects.filter(projet=projet).order_by('ordre')
        thematiques_stats = []

        for thematique in thematiques:
            # Récupérer les indicateurs de cette thématique
            indicateurs = Indicateur.objects.filter(thematique=thematique)

            # Calculer la somme des cibles pour cette thématique (toutes communes confondues)
            total_cible = CibleIndicateur.objects.filter(
                indicateur__in=indicateurs,
                annee=2025
            ).aggregate(total=Sum('valeur_cible'))['total'] or 0

            # Calculer la somme des réalisations depuis les interventions terminées
            total_realise = Intervention.objects.filter(
                indicateur__in=indicateurs,
                statut='TERMINE'
            ).aggregate(total=Sum('valeur_quantitative'))['total'] or 0

            # Calculer le pourcentage
            if total_cible > 0:
                pourcentage = round((total_realise / total_cible) * 100, 1)
            else:
                pourcentage = 0

            thematiques_stats.append({
                'id': thematique.id,
                'code': thematique.code,
                'libelle': thematique.libelle,
                'pourcentage': pourcentage,
                'total_realise': total_realise,
                'total_cible': total_cible,
            })

        # KPI 3 : Avancement global (moyenne des pourcentages des thématiques)
        if thematiques_stats:
            avancement_global = round(
                sum([t['pourcentage'] for t in thematiques_stats]) / len(thematiques_stats),
                1
            )
        else:
            avancement_global = 0

        # Statistiques par commune
        from referentiels.models import Commune
        communes = Commune.objects.filter(
            commune_projets__projet_id=projet_id
        ).distinct().order_by('nom')

        communes_stats = []
        for commune in communes:
            # Interventions terminées dans cette commune
            interventions_commune = interventions.filter(
                commune=commune,
                statut='TERMINE'
            ).aggregate(total=Sum('valeur_quantitative'))['total'] or 0

            # Cibles pour cette commune (somme des cibles par commune)
            cibles_commune = CibleIndicateur.objects.filter(
                indicateur__projet_id=projet_id,
                commune=commune,
                annee=2025
            ).aggregate(total=Sum('valeur_cible'))['total'] or 0

            if cibles_commune > 0:
                pourcentage_commune = round((interventions_commune / cibles_commune) * 100, 1)
            else:
                pourcentage_commune = 0

            communes_stats.append({
                'nom': commune.nom,
                'pourcentage': pourcentage_commune,
                'realise': interventions_commune,
                'cible': cibles_commune,
            })

    else:
        interventions = Intervention.objects.all()
        indicateurs_filter = {}
        interventions_realisees = 0
        interventions_ce_mois = 0
        beneficiaires_touches = 0
        avancement_global = 0
        thematiques_stats = []
        communes_stats = []

    # Statistiques générales (KPI)
    stats = {
        'interventions_realisees': interventions_realisees,
        'interventions_ce_mois': interventions_ce_mois,
        'beneficiaires_touches': beneficiaires_touches,
        'avancement_global': avancement_global,
    }

    # Activités récentes
    activites_recentes = interventions.select_related(
        'commune', 'type_intervention', 'indicateur__thematique'
    ).order_by('-date_creation')[:10]

    context = {
        'stats': stats,
        'thematiques_stats': thematiques_stats,
        'communes_stats': communes_stats,
        'activites_recentes': activites_recentes,
    }

    return render(request, 'dashboard/home.html', context)


@login_required
def indicateurs_view(request):
    """Vue des indicateurs de suivi"""

    # Récupérer le projet depuis la session
    projet_id = request.session.get('projet_id')

    # Récupérer les indicateurs du projet avec leurs thématiques
    if projet_id:
        indicateurs = Indicateur.objects.filter(projet_id=projet_id).select_related('thematique', 'projet')
    else:
        indicateurs = Indicateur.objects.select_related('thematique', 'projet').all()

    # Calculer les valeurs actuelles pour chaque indicateur
    def get_valeur_actuelle(indicateur):
        """Calculer la valeur actuelle d'un indicateur"""
        derniere_valeur = ValeurIndicateur.objects.filter(
            indicateur=indicateur
        ).order_by('-date_mesure').first()

        if derniere_valeur:
            # Récupérer la cible (globale, sans commune spécifique)
            from suivi.models import CibleIndicateur
            cible = CibleIndicateur.objects.filter(
                indicateur=indicateur,
                commune__isnull=True
            ).order_by('-annee').first()

            pourcentage = 0
            if cible and cible.valeur_cible > 0:
                pourcentage = round((float(derniere_valeur.valeur_realisee) / float(cible.valeur_cible)) * 100, 1)

            return {
                'valeur': derniere_valeur.valeur_realisee,
                'pourcentage': pourcentage,
                'periode': derniere_valeur.date_mesure.strftime('%d/%m/%Y')
            }
        return {'valeur': 0, 'pourcentage': 0, 'periode': 'Aucune donnée'}

    # Enrichir les indicateurs avec leurs valeurs actuelles
    for indicateur in indicateurs:
        indicateur.valeur_actuelle = get_valeur_actuelle(indicateur)

    context = {
        'indicateurs': indicateurs,
    }

    return render(request, 'dashboard/indicateurs.html', context)


@login_required
def activites_view(request):
    """Vue de gestion des activités"""

    # Récupérer le projet depuis la session
    projet_id = request.session.get('projet_id')

    # Filtres
    commune_filter = request.GET.get('commune')
    statut_filter = request.GET.get('statut')

    # Base queryset filtré par projet
    if projet_id:
        activites = Intervention.objects.filter(projet_id=projet_id).select_related('commune', 'type_intervention', 'projet')
    else:
        activites = Intervention.objects.select_related('commune', 'type_intervention', 'projet').all()

    if commune_filter:
        activites = activites.filter(commune_id=commune_filter)

    if statut_filter:
        activites = activites.filter(statut=statut_filter)

    activites = activites.order_by('-date_creation')

    # Pour les filtres
    communes = Commune.objects.all()
    statuts = Intervention.STATUT_CHOICES

    context = {
        'activites': activites,
        'communes': communes,
        'statuts': statuts,
        'commune_filter': commune_filter,
        'statut_filter': statut_filter,
    }

    return render(request, 'dashboard/activites.html', context)


@login_required
def creer_thematiques_view(request):
    """Gérer les thématiques du projet (créer, éditer, supprimer)"""
    from suivi.models import Thematique
    from core.models import Projet
    from django.contrib import messages

    projet_id = request.session.get('projet_id')

    if not projet_id:
        messages.error(request, "Aucun projet sélectionné.")
        return redirect('liste_projets')

    projet = Projet.objects.get(id=projet_id)

    # Récupérer les thématiques existantes
    thematiques_existantes = Thematique.objects.filter(
        projet=projet
    ).order_by('code')

    # Mode wizard si aucune thématique n'existe
    is_wizard = thematiques_existantes.count() == 0

    if request.method == 'POST':
        action = request.POST.get('action', 'create')

        if action == 'delete':
            # Supprimer une thématique
            thematique_id = request.POST.get('thematique_id')
            thematique = get_object_or_404(Thematique, id=thematique_id, projet=projet)
            libelle = thematique.libelle
            thematique.delete()
            messages.success(request, f"Thématique {libelle} supprimée.")
            return redirect('creer_thematiques')

        elif action == 'update':
            # Mettre à jour une thématique existante
            thematique_id = request.POST.get('thematique_id')
            thematique = get_object_or_404(Thematique, id=thematique_id, projet=projet)
            thematique.code = request.POST.get('code')
            thematique.libelle = request.POST.get('libelle')
            thematique.description = request.POST.get('description', '')
            thematique.save()
            messages.success(request, f"Thématique {thematique.libelle} mise à jour.")
            return redirect('creer_thematiques')

        else:
            # Créer de nouvelles thématiques
            thematiques_data = []
            i = 1
            while f'code_{i}' in request.POST:
                code = request.POST.get(f'code_{i}')
                libelle = request.POST.get(f'libelle_{i}')
                description = request.POST.get(f'description_{i}', '')

                if code and libelle:
                    thematiques_data.append({
                        'code': code,
                        'libelle': libelle,
                        'description': description
                    })
                i += 1

            # Créer les thématiques
            for data in thematiques_data:
                Thematique.objects.create(
                    projet=projet,
                    code=data['code'],
                    libelle=data['libelle'],
                    description=data['description']
                )

            if thematiques_data:
                messages.success(request, f"{len(thematiques_data)} thématique(s) créée(s) avec succès.")

            # En mode wizard, rediriger vers indicateurs
            if is_wizard and thematiques_data:
                return redirect('configurer_indicateurs')

            return redirect('creer_thematiques')

    context = {
        'projet': projet,
        'thematiques_existantes': thematiques_existantes,
        'is_wizard': is_wizard,
    }

    return render(request, 'dashboard/creer_thematiques.html', context)


@login_required
def menu_configuration_view(request):
    """Menu de configuration du projet"""
    from suivi.models import Thematique
    from core.models import Projet

    projet_id = request.session.get('projet_id')

    if not projet_id:
        messages.error(request, "Aucun projet sélectionné.")
        return redirect('liste_projets')

    projet = Projet.objects.get(id=projet_id)
    thematiques = Thematique.objects.filter(projet=projet)
    indicateurs = Indicateur.objects.filter(projet=projet)

    context = {
        'projet': projet,
        'nb_thematiques': thematiques.count(),
        'nb_indicateurs': indicateurs.count(),
    }

    return render(request, 'dashboard/menu_configuration.html', context)


@login_required
def configurer_indicateurs_view(request):
    """Gérer les indicateurs par thématique (créer, éditer, supprimer)"""
    from suivi.models import Thematique, CibleIndicateur
    from core.models import Projet
    from datetime import datetime

    projet_id = request.session.get('projet_id')

    if not projet_id:
        messages.error(request, "Aucun projet sélectionné.")
        return redirect('liste_projets')

    projet = Projet.objects.get(id=projet_id)
    thematiques = Thematique.objects.filter(projet=projet).order_by('code')

    # Récupérer les indicateurs existants avec leurs cibles
    indicateurs_existants = {}
    for thematique in thematiques:
        indicateurs_existants[thematique.id] = Indicateur.objects.filter(
            projet=projet,
            thematique=thematique
        ).select_related('thematique').prefetch_related('cibles').order_by('code')

    # Mode wizard si aucun indicateur n'existe
    is_wizard = Indicateur.objects.filter(projet=projet).count() == 0

    if request.method == 'POST':
        action = request.POST.get('action', 'create')

        if action == 'delete':
            # Supprimer un indicateur
            indicateur_id = request.POST.get('indicateur_id')
            indicateur = get_object_or_404(Indicateur, id=indicateur_id, projet=projet)
            indicateur.delete()
            messages.success(request, f"Indicateur {indicateur.libelle} supprimé.")
            return redirect('configurer_indicateurs')

        elif action == 'update':
            # Mettre à jour un indicateur existant
            indicateur_id = request.POST.get('indicateur_id')
            indicateur = get_object_or_404(Indicateur, id=indicateur_id, projet=projet)
            indicateur.code = request.POST.get('code')
            indicateur.libelle = request.POST.get('libelle')
            indicateur.unite_mesure = request.POST.get('unite_mesure')
            indicateur.type_calcul = request.POST.get('type_calcul')
            indicateur.save()

            # Mettre à jour ou créer la cible
            valeur_cible = request.POST.get('valeur_cible')
            if valeur_cible:
                cible, created = CibleIndicateur.objects.update_or_create(
                    indicateur=indicateur,
                    commune=None,  # Cible globale
                    annee=datetime.now().year,
                    defaults={'valeur_cible': int(valeur_cible)}
                )

            messages.success(request, f"Indicateur {indicateur.libelle} mis à jour.")
            return redirect('configurer_indicateurs')

        else:
            # Créer de nouveaux indicateurs
            nb_created = 0
            for thematique in thematiques:
                i = 1
                while f'indicateur_code_{thematique.id}_{i}' in request.POST:
                    code = request.POST.get(f'indicateur_code_{thematique.id}_{i}')
                    libelle = request.POST.get(f'indicateur_libelle_{thematique.id}_{i}')
                    unite = request.POST.get(f'indicateur_unite_{thematique.id}_{i}', 'Nombre')
                    type_calcul = request.POST.get(f'indicateur_type_{thematique.id}_{i}', 'SOMME')
                    valeur_cible = request.POST.get(f'indicateur_cible_{thematique.id}_{i}')

                    if code and libelle:
                        indicateur = Indicateur.objects.create(
                            projet=projet,
                            thematique=thematique,
                            code=code,
                            libelle=libelle,
                            unite_mesure=unite,
                            type_calcul=type_calcul,
                            ordre=i
                        )

                        # Créer la cible si fournie
                        if valeur_cible:
                            CibleIndicateur.objects.create(
                                indicateur=indicateur,
                                commune=None,  # Cible globale
                                annee=datetime.now().year,
                                valeur_cible=int(valeur_cible)
                            )

                        nb_created += 1
                    i += 1

            if nb_created > 0:
                messages.success(request, f"{nb_created} indicateur(s) créé(s) avec succès.")

            # En mode wizard, rediriger vers paramètres
            if is_wizard and nb_created > 0:
                return redirect('configurer_parametres')

            return redirect('configurer_indicateurs')

    context = {
        'projet': projet,
        'thematiques': thematiques,
        'indicateurs_existants': indicateurs_existants,
        'is_wizard': is_wizard,
        'annee_courante': datetime.now().year,
    }

    return render(request, 'dashboard/configurer_indicateurs.html', context)


@login_required
def configurer_parametres_view(request):
    """Étape 3 : Configuration finale et paramètres"""
    from core.models import Projet

    projet_id = request.session.get('projet_id')

    if not projet_id:
        messages.error(request, "Aucun projet sélectionné.")
        return redirect('liste_projets')

    projet = Projet.objects.get(id=projet_id)

    if request.method == 'POST':
        messages.success(request, "Configuration du projet terminée !")
        return redirect('dashboard_home')

    context = {
        'projet': projet,
    }

    return render(request, 'dashboard/configurer_parametres.html', context)


@login_required
def liste_interventions_view(request):
    """Liste des interventions du projet"""
    from core.models import Projet

    projet_id = request.session.get('projet_id')
    if not projet_id:
        messages.error(request, "Aucun projet sélectionné.")
        return redirect('liste_projets')

    projet = Projet.objects.get(id=projet_id)
    interventions = Intervention.objects.filter(projet=projet).select_related(
        'indicateur', 'commune', 'type_intervention'
    ).order_by('-date_creation')

    context = {
        'projet': projet,
        'interventions': interventions,
    }

    return render(request, 'dashboard/liste_interventions.html', context)


@login_required
def creer_intervention_view(request):
    """Créer une nouvelle intervention"""
    from core.models import Projet
    from suivi.models import Thematique
    from referentiels.models import Commune, TypeIntervention
    from datetime import date

    projet_id = request.session.get('projet_id')
    if not projet_id:
        messages.error(request, "Aucun projet sélectionné.")
        return redirect('liste_projets')

    projet = Projet.objects.get(id=projet_id)

    if request.method == 'POST':
        # Récupérer les données du formulaire
        indicateur_id = request.POST.get('indicateur')
        indicateur = get_object_or_404(Indicateur, id=indicateur_id, projet=projet)

        commune_id = request.POST.get('commune')
        commune = get_object_or_404(Commune, id=commune_id)

        type_intervention_id = request.POST.get('type_intervention')
        type_intervention = get_object_or_404(TypeIntervention, id=type_intervention_id)

        # Créer l'intervention
        intervention = Intervention.objects.create(
            projet=projet,
            indicateur=indicateur,
            commune=commune,
            type_intervention=type_intervention,
            libelle=request.POST.get('libelle'),
            description=request.POST.get('description', ''),
            nature=request.POST.get('nature', 'ACTIVITE'),
            valeur_quantitative=request.POST.get('valeur_quantitative') or 1,
            date_intervention=request.POST.get('date_intervention') or date.today(),
            statut='PROGRAMME',
            cree_par=request.user
        )

        messages.success(request, f"Intervention '{intervention.libelle}' créée avec succès.")
        return redirect('liste_interventions')

    # GET : afficher le formulaire
    thematiques = Thematique.objects.filter(projet=projet).prefetch_related('indicateurs')
    communes = Commune.objects.all().order_by('nom')
    types_intervention = TypeIntervention.objects.filter(actif=True).order_by('libelle')

    context = {
        'projet': projet,
        'thematiques': thematiques,
        'communes': communes,
        'types_intervention': types_intervention,
    }

    return render(request, 'dashboard/creer_intervention.html', context)


@login_required
def thematique_detail_view(request, thematique_id):
    """Vue détaillée d'une thématique avec ses indicateurs et interventions"""
    from core.models import Projet
    from suivi.models import Thematique, CibleIndicateur

    projet_id = request.session.get('projet_id')
    if not projet_id:
        messages.error(request, "Aucun projet sélectionné.")
        return redirect('liste_projets')

    projet = Projet.objects.get(id=projet_id)
    thematique = get_object_or_404(Thematique, id=thematique_id, projet=projet)

    # Récupérer les indicateurs de cette thématique avec leurs statistiques
    indicateurs = Indicateur.objects.filter(thematique=thematique).order_by('ordre', 'code')

    indicateurs_stats = []
    for indicateur in indicateurs:
        # Cible globale
        cible = CibleIndicateur.objects.filter(
            indicateur=indicateur,
            commune__isnull=True,
            annee=2025
        ).first()

        # Réalisations depuis les interventions terminées
        total_realise = Intervention.objects.filter(
            indicateur=indicateur,
            statut='TERMINE'
        ).aggregate(total=Sum('valeur_quantitative'))['total'] or 0

        valeur_cible = cible.valeur_cible if cible else 0
        pourcentage = round((total_realise / valeur_cible) * 100, 1) if valeur_cible > 0 else 0

        indicateurs_stats.append({
            'indicateur': indicateur,
            'cible': valeur_cible,
            'realise': total_realise,
            'pourcentage': pourcentage,
        })

    # Interventions de cette thématique
    interventions = Intervention.objects.filter(
        indicateur__thematique=thematique
    ).select_related('indicateur', 'commune', 'type_intervention').order_by('-date_intervention')[:20]

    context = {
        'projet': projet,
        'thematique': thematique,
        'indicateurs_stats': indicateurs_stats,
        'interventions': interventions,
    }

    return render(request, 'dashboard/thematique_detail.html', context)


@login_required
def changer_statut_intervention_view(request, intervention_id):
    """Changer le statut d'une intervention via AJAX"""
    import json
    from django.http import JsonResponse
    from core.models import Projet

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

    projet_id = request.session.get('projet_id')
    if not projet_id:
        return JsonResponse({'success': False, 'error': 'Aucun projet sélectionné'}, status=403)

    try:
        projet = Projet.objects.get(id=projet_id)
        intervention = get_object_or_404(Intervention, id=intervention_id, projet=projet)

        data = json.loads(request.body)
        nouveau_statut = data.get('statut')

        # Valider le statut
        statuts_valides = ['PROGRAMME', 'TERMINE', 'ANNULEE']
        if nouveau_statut not in statuts_valides:
            return JsonResponse({'success': False, 'error': 'Statut invalide'}, status=400)

        intervention.statut = nouveau_statut
        intervention.save()

        return JsonResponse({'success': True, 'message': 'Statut mis à jour'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def logout_view(request):
    """Vue de déconnexion personnalisée"""
    logout(request)
    return redirect('landing_page')


# ========================================
# MODULE CARTOGRAPHIE SIG
# ========================================

@login_required
def carte_sig_view(request):
    """Interface SIG 3D avec MapLibre GL JS"""
    from core.models import Projet

    projet_id = request.session.get('projet_id')
    if not projet_id:
        messages.error(request, "Aucun projet sélectionné.")
        return redirect('liste_projets')

    projet = Projet.objects.get(id=projet_id)

    # Calculer le centre de la zone d'intervention
    from referentiels.models import CommuneGeom
    communes_geom = CommuneGeom.objects.filter(
        commune__commune_projets__projet=projet
    )

    # Centre par défaut sur Kéniéba (Sénégal)
    center_lng = -11.75
    center_lat = 13.05

    if communes_geom.exists():
        # Calculer le centroïde de toutes les communes du projet
        from django.contrib.gis.db.models.functions import Union
        from django.db.models import Avg

        centroid = communes_geom.aggregate(
            avg_lng=Avg('centroide__x'),
            avg_lat=Avg('centroide__y')
        )

        if centroid['avg_lng'] and centroid['avg_lat']:
            center_lng = centroid['avg_lng']
            center_lat = centroid['avg_lat']

    context = {
        'projet': projet,
        'center_lng': center_lng,
        'center_lat': center_lat,
    }

    return render(request, 'dashboard/carte_sig.html', context)


# ========================================
# API GEOJSON POUR MAPLIBRE
# ========================================

@login_required
def api_communes_geojson(request):
    """API GeoJSON pour les communes du projet"""
    from django.http import JsonResponse
    from django.core.serializers import serialize
    from referentiels.models import CommuneGeom, Commune
    from django.contrib.gis.geos import GEOSGeometry
    import json

    projet_id = request.session.get('projet_id')
    if not projet_id:
        return JsonResponse({'error': 'Aucun projet sélectionné'}, status=403)

    # Récupérer les géométries des communes du projet
    communes_geom = CommuneGeom.objects.filter(
        commune__commune_projets__projet_id=projet_id
    ).select_related('commune')

    features = []
    for commune_geom in communes_geom:
        # Statistiques de la commune
        from suivi.models import Intervention, CibleIndicateur

        interventions_count = Intervention.objects.filter(
            projet_id=projet_id,
            commune=commune_geom.commune,
            statut='TERMINE'
        ).count()

        beneficiaires = Intervention.objects.filter(
            projet_id=projet_id,
            commune=commune_geom.commune,
            statut='TERMINE'
        ).aggregate(total=Sum('valeur_quantitative'))['total'] or 0

        cibles = CibleIndicateur.objects.filter(
            indicateur__projet_id=projet_id,
            commune=commune_geom.commune,
            annee=2025
        ).aggregate(total=Sum('valeur_cible'))['total'] or 0

        feature = {
            'type': 'Feature',
            'geometry': json.loads(commune_geom.geom.geojson) if commune_geom.geom else None,
            'properties': {
                'id': commune_geom.commune.id,
                'nom': commune_geom.commune.nom,
                'code_commune': commune_geom.commune.code_commune,
                'departement': commune_geom.commune.departement,
                'region': commune_geom.commune.region,
                'interventions_count': interventions_count,
                'beneficiaires': int(beneficiaires),
                'cibles': int(cibles),
                'avancement': round((beneficiaires / cibles * 100), 1) if cibles > 0 else 0,
            }
        }
        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    return JsonResponse(geojson, safe=False)


@login_required
def api_interventions_geojson(request):
    """API GeoJSON pour les interventions du projet"""
    from django.http import JsonResponse
    from suivi.models import Intervention
    import json

    projet_id = request.session.get('projet_id')
    if not projet_id:
        return JsonResponse({'error': 'Aucun projet sélectionné'}, status=403)

    # Filtres optionnels
    statut = request.GET.get('statut')
    commune_id = request.GET.get('commune_id')

    interventions = Intervention.objects.filter(
        projet_id=projet_id,
        geom__isnull=False
    ).select_related('commune', 'type_intervention', 'indicateur__thematique')

    if statut:
        interventions = interventions.filter(statut=statut)

    if commune_id:
        interventions = interventions.filter(commune_id=commune_id)

    features = []
    for intervention in interventions:
        feature = {
            'type': 'Feature',
            'geometry': json.loads(intervention.geom.geojson),
            'properties': {
                'id': intervention.id,
                'libelle': intervention.libelle,
                'description': intervention.description,
                'nature': intervention.nature,
                'statut': intervention.statut,
                'statut_display': intervention.get_statut_display(),
                'type_intervention': intervention.type_intervention.libelle if intervention.type_intervention else None,
                'commune': intervention.commune.nom if intervention.commune else None,
                'thematique': intervention.indicateur.thematique.code if intervention.indicateur and intervention.indicateur.thematique else None,
                'indicateur': intervention.indicateur.libelle if intervention.indicateur else None,
                'valeur_quantitative': int(intervention.valeur_quantitative),
                'date_intervention': intervention.date_intervention.strftime('%Y-%m-%d') if intervention.date_intervention else None,
                'date_creation': intervention.date_creation.strftime('%Y-%m-%d'),
            }
        }
        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    return JsonResponse(geojson, safe=False)


@login_required
def api_infrastructures_geojson(request):
    """API GeoJSON pour les infrastructures du projet"""
    from django.http import JsonResponse
    from geo.models import Infrastructure
    import json

    projet_id = request.session.get('projet_id')
    if not projet_id:
        return JsonResponse({'error': 'Aucun projet sélectionné'}, status=403)

    infrastructures = Infrastructure.objects.filter(
        projet_id=projet_id,
        geom__isnull=False
    ).select_related('commune', 'type_infrastructure')

    features = []
    for infra in infrastructures:
        feature = {
            'type': 'Feature',
            'geometry': json.loads(infra.geom.geojson),
            'properties': {
                'id': infra.id,
                'libelle': infra.libelle,
                'type': infra.type_infrastructure.libelle if infra.type_infrastructure else None,
                'commune': infra.commune.nom if infra.commune else None,
                'statut': infra.statut,
                'statut_display': infra.get_statut_display(),
                'nb_beneficiaires': infra.nb_beneficiaires,
                'cout_construction': float(infra.cout_construction) if infra.cout_construction else None,
                'date_construction': infra.date_construction.strftime('%Y-%m-%d') if infra.date_construction else None,
            }
        }
        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    return JsonResponse(geojson, safe=False)


@login_required
def api_acteurs_geojson(request):
    """API GeoJSON pour les acteurs du projet"""
    from django.http import JsonResponse
    from geo.models import Acteur
    import json

    projet_id = request.session.get('projet_id')
    if not projet_id:
        return JsonResponse({'error': 'Aucun projet sélectionné'}, status=403)

    acteurs = Acteur.objects.filter(
        projet_id=projet_id,
        geom__isnull=False
    ).select_related('commune', 'type_acteur')

    features = []
    for acteur in acteurs:
        feature = {
            'type': 'Feature',
            'geometry': json.loads(acteur.geom.geojson),
            'properties': {
                'id': acteur.id,
                'libelle': acteur.libelle,
                'type': acteur.type_acteur.libelle if acteur.type_acteur else None,
                'commune': acteur.commune.nom if acteur.commune else None,
                'nb_adherents': acteur.nb_adherents,
                'nb_femmes': acteur.nb_femmes,
                'nb_hommes': acteur.nb_hommes,
                'nb_jeunes': acteur.nb_jeunes,
                'responsable': acteur.responsable,
                'telephone': acteur.telephone,
                'email': acteur.email,
            }
        }
        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    return JsonResponse(geojson, safe=False)
