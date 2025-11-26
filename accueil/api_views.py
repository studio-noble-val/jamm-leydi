"""
Vues API pour la sélection géographique en cascade
"""
from django.http import JsonResponse
from django.contrib.gis.geos import GEOSGeometry
from geo.models import Admin2, Admin4, Admin5, Admin7, Admin8


def get_regions_by_pays(request):
    """
    Retourne les régions d'un ou plusieurs pays (filtrage spatial)

    GET /api/geo/regions/?pays_ids=1,2,3
    """
    pays_ids = request.GET.get('pays_ids', '')

    if not pays_ids:
        return JsonResponse({'regions': []})

    try:
        ids_list = [int(id.strip()) for id in pays_ids.split(',') if id.strip()]
        pays_list = Admin2.objects.filter(id__in=ids_list, geom__isnull=False)

        # Récupérer toutes les régions qui intersectent avec les pays sélectionnés
        regions = []
        regions_seen = set()

        for pays in pays_list:
            # Requête spatiale: régions qui intersectent le pays
            regions_intersect = Admin4.objects.filter(
                geom__intersects=pays.geom
            ).values('id', 'name')

            for region in regions_intersect:
                if region['id'] not in regions_seen:
                    regions.append(region)
                    regions_seen.add(region['id'])

        # Trier par nom
        regions.sort(key=lambda x: x['name'] or '')

        return JsonResponse({'regions': regions})

    except (ValueError, TypeError):
        return JsonResponse({'error': 'IDs invalides'}, status=400)


def get_departements_by_regions(request):
    """
    Retourne les départements d'une ou plusieurs régions (filtrage spatial)

    GET /api/geo/departements/?region_ids=1,2,3
    """
    region_ids = request.GET.get('region_ids', '')

    if not region_ids:
        return JsonResponse({'departements': []})

    try:
        ids_list = [int(id.strip()) for id in region_ids.split(',') if id.strip()]
        regions_list = Admin4.objects.filter(id__in=ids_list, geom__isnull=False)

        departements = []
        departements_seen = set()

        for region in regions_list:
            depts_intersect = Admin5.objects.filter(
                geom__intersects=region.geom
            ).values('id', 'name')

            for dept in depts_intersect:
                if dept['id'] not in departements_seen:
                    departements.append(dept)
                    departements_seen.add(dept['id'])

        departements.sort(key=lambda x: x['name'] or '')

        return JsonResponse({'departements': departements})

    except (ValueError, TypeError):
        return JsonResponse({'error': 'IDs invalides'}, status=400)


def get_arrondissements_by_departements(request):
    """
    Retourne les arrondissements d'un ou plusieurs départements (filtrage spatial)

    GET /api/geo/arrondissements/?departement_ids=1,2,3
    """
    departement_ids = request.GET.get('departement_ids', '')

    if not departement_ids:
        return JsonResponse({'arrondissements': []})

    try:
        ids_list = [int(id.strip()) for id in departement_ids.split(',') if id.strip()]
        departements_list = Admin5.objects.filter(id__in=ids_list, geom__isnull=False)

        arrondissements = []
        arrondissements_seen = set()

        for departement in departements_list:
            arrond_intersect = Admin7.objects.filter(
                geom__intersects=departement.geom
            ).values('id', 'name')

            for arrond in arrond_intersect:
                if arrond['id'] not in arrondissements_seen:
                    arrondissements.append(arrond)
                    arrondissements_seen.add(arrond['id'])

        arrondissements.sort(key=lambda x: x['name'] or '')

        return JsonResponse({'arrondissements': arrondissements})

    except (ValueError, TypeError):
        return JsonResponse({'error': 'IDs invalides'}, status=400)


def get_communes_by_arrondissements(request):
    """
    Retourne les communes d'un ou plusieurs arrondissements (filtrage spatial)

    GET /api/geo/communes/?arrondissement_ids=1,2,3
    """
    arrondissement_ids = request.GET.get('arrondissement_ids', '')

    if not arrondissement_ids:
        return JsonResponse({'communes': []})

    try:
        ids_list = [int(id.strip()) for id in arrondissement_ids.split(',') if id.strip()]
        arrondissements_list = Admin7.objects.filter(id__in=ids_list, geom__isnull=False)

        communes = []
        communes_seen = set()

        for arrondissement in arrondissements_list:
            communes_intersect = Admin8.objects.filter(
                geom__intersects=arrondissement.geom
            ).values('id', 'name')

            for commune in communes_intersect:
                if commune['id'] not in communes_seen:
                    communes.append(commune)
                    communes_seen.add(commune['id'])

        communes.sort(key=lambda x: x['name'] or '')

        return JsonResponse({'communes': communes})

    except (ValueError, TypeError):
        return JsonResponse({'error': 'IDs invalides'}, status=400)
