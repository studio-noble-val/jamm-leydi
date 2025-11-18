"""
Vues pour l'accueil et la sélection de projets
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from core.models import Projet, UserProjet


def landing_page(request):
    """
    Landing Page SIG GRDR avec formulaire de connexion
    """
    # Si l'utilisateur est déjà connecté, rediriger vers la liste des projets
    if request.user.is_authenticated:
        return redirect('liste_projets')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('liste_projets')
        else:
            messages.error(request, 'Identifiants incorrects')

    return render(request, 'accueil/landing.html')


@login_required
def liste_projets(request):
    """
    Liste des projets accessibles par l'utilisateur connecté
    Affiche des cards avec les informations clés
    """
    # Récupérer les projets auxquels l'utilisateur a accès
    user_projets = UserProjet.objects.filter(
        user=request.user,
        actif=True
    ).select_related('projet').order_by('-projet__date_creation')

    # Si l'utilisateur est superuser, afficher tous les projets
    if request.user.is_superuser:
        projets = Projet.objects.filter(actif=True).order_by('-date_creation')
        user_projets_data = [{'projet': p, 'role': 'Administrateur système'} for p in projets]
    else:
        user_projets_data = [
            {
                'projet': up.projet,
                'role': up.get_role_display()
            }
            for up in user_projets
        ]

    context = {
        'user_projets': user_projets_data,
        'nb_projets': len(user_projets_data),
    }

    return render(request, 'accueil/liste_projets.html', context)


@login_required
def creer_projet(request):
    """
    Créer un nouveau projet et lancer le wizard de configuration
    """
    from datetime import date
    from decimal import Decimal
    from referentiels.models import EquipeGRDR

    if request.method == 'POST':
        # Récupérer l'équipe GRDR si sélectionnée
        equipe_grdr_id = request.POST.get('equipe_grdr')
        equipe_grdr = None
        if equipe_grdr_id:
            try:
                equipe_grdr = EquipeGRDR.objects.get(id=equipe_grdr_id)
            except EquipeGRDR.DoesNotExist:
                pass

        # Créer le projet
        projet = Projet.objects.create(
            code_projet=request.POST.get('code_projet'),
            libelle=request.POST.get('libelle'),
            description=request.POST.get('description', ''),
            pays=request.POST.get('pays', 'Sénégal'),
            equipe_grdr=equipe_grdr,
            bailleurs=request.POST.get('bailleurs', ''),
            zone_intervention=request.POST.get('zone_intervention', ''),
            date_debut=request.POST.get('date_debut'),
            date_fin=request.POST.get('date_fin'),
            budget=request.POST.get('budget') or None,
            devise=request.POST.get('devise', 'EUR'),
            statut='PLANIFIE',
            actif=True,
        )

        # Lier l'utilisateur au projet comme admin
        UserProjet.objects.create(
            user=request.user,
            projet=projet,
            role='ADMIN_PROJET',
            actif=True
        )

        # Stocker dans la session
        request.session['projet_id'] = projet.id
        request.session['projet_code'] = projet.code_projet
        request.session['projet_libelle'] = projet.libelle

        messages.success(request, f"Projet {projet.libelle} créé avec succès.")

        # Rediriger vers le wizard de configuration
        return redirect('creer_thematiques')

    # GET : afficher le formulaire avec les équipes GRDR
    equipes_grdr = EquipeGRDR.objects.filter(actif=True).order_by('type_equipe', 'pays', 'nom')

    context = {
        'equipes_grdr': equipes_grdr,
    }

    return render(request, 'accueil/creer_projet.html', context)


@login_required
def selectionner_projet(request, projet_id):
    """
    Sélectionner un projet et stocker dans la session
    Vérifie que l'utilisateur a accès au projet
    """
    projet = get_object_or_404(Projet, id=projet_id, actif=True)

    # Vérifier que l'utilisateur a accès à ce projet
    if not request.user.is_superuser:
        user_projet = UserProjet.objects.filter(
            user=request.user,
            projet=projet,
            actif=True
        ).first()

        if not user_projet:
            messages.error(request, "Vous n'avez pas accès à ce projet.")
            return redirect('liste_projets')

    # Stocker le projet sélectionné dans la session
    request.session['projet_id'] = projet.id
    request.session['projet_code'] = projet.code_projet
    request.session['projet_libelle'] = projet.libelle

    # Rediriger vers le dashboard du projet (sans message)
    return redirect('dashboard_home')


@login_required
def supprimer_projet(request, projet_id):
    """
    Supprimer un projet (réservé aux superusers)
    ATTENTION : Supprime en cascade toutes les données associées
    """
    # Vérifier que l'utilisateur est superuser
    if not request.user.is_superuser:
        messages.error(request, "Vous n'avez pas les droits pour supprimer un projet.")
        return redirect('liste_projets')

    projet = get_object_or_404(Projet, id=projet_id)

    if request.method == 'POST':
        projet_libelle = projet.libelle

        # Supprimer de la session si c'est le projet actif
        if request.session.get('projet_id') == projet_id:
            request.session.pop('projet_id', None)
            request.session.pop('projet_code', None)
            request.session.pop('projet_libelle', None)

        # Supprimer le projet (CASCADE supprimera toutes les données liées)
        projet.delete()

        messages.success(request, f"Le projet '{projet_libelle}' et toutes ses données ont été supprimés avec succès.")
        return redirect('liste_projets')

    # Si GET, rediriger vers la liste (la confirmation se fait via le modal)
    return redirect('liste_projets')
