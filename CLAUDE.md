# CLAUDE.md - Configuration de Travail

## 🤖 Contexte du Projet

**JAMM LEYDI** est une plateforme de suivi, pilotage et capitalisation pour un projet de prévention des conflits liés au changement climatique dans l'arrondissement de Kéniéba (Sénégal).

### Informations Clés
- **Client** : GRDR (Migration Citoyenneté Développement)
- **Bailleur** : Union Européenne
- **Zone d'intervention** : 4 communes (Gathiary, Toumboura, Médina Foulbé, Sadatou)
- **Objectif** : 14 700 bénéficiaires ciblés
- **Durée** : Projet en cours jusqu'en 2026

## 🏗️ Architecture Technique (Version 2.0)

### Stack Actuelle
- **Backend** : Django 5.2.7 (Python)
- **Base de données** : PostgreSQL 16 + PostGIS 3.4
- **Frontend** : Bootstrap 5 + Chart.js + Templates Django
- **Cartographie** : Leaflet.js (à intégrer)
- **Authentification** : Django Auth personnalisé (core.User)

### Structure des Applications
```
jamm_leydi/          # Configuration principale
├── core/            # Gestion multi-projets & utilisateurs (User, Projet, UserProjet)
├── referentiels/    # Données mutualisées (Commune, Types, ProjetCommune)
├── suivi/           # Cœur métier (Thematique, Indicateur, Intervention, ValeurIndicateur)
├── geo/             # Entités géolocalisées (Infrastructure, Acteur)
├── securite/        # Monitoring sécurité (TypeInsecurite, SecurityReport)
├── dashboard/       # Interface d'administration (back-office)
└── public/          # Interface publique (communication)
```

## 📊 Modèles de Données Principaux

### Architecture Multi-Projets (core)
1. **User** (AbstractUser personnalisé) : Utilisateurs avec téléphone et organisation
2. **Projet** : Projets de développement (code, dates, budget, bailleurs, zone_intervention)
3. **UserProjet** : Relation Many-to-Many avec rôles (ADMIN_PROJET, CONTRIBUTEUR, LECTEUR)

**Isolation** : Chaque utilisateur ne voit que ses projets assignés.

### Référentiels Mutualisés (referentiels)
1. **Commune** : Référentiel national des communes (nom, code_commune, département, région)
2. **CommuneGeom** : Géométries MULTIPOLYGON avec centroïde auto-calculé
3. **ChefLieu** : Points POINT des chefs-lieux
4. **ProjetCommune** : Liaison Many-to-Many Projet ↔ Commune
5. **TypeIntervention** (6) : Rencontres, Agro-sylvo-pastorales, Économiques, Hydrauliques, Cantines, Santé
6. **TypeInfrastructure** : Forages, Écoles, Maraîchages, Cantines, Postes de santé
7. **TypeActeur** : Groupements féminins, Associations d'éleveurs, Coopératives

### Suivi des Indicateurs (suivi)
1. **Thematique** : R1, R2, R3 (résultats du cadre logique par projet)
2. **Indicateur** : Indicateurs avec code, unité_mesure, type_calcul (SOMME/MOYENNE/DENOMBREMENT/MANUEL)
3. **CibleIndicateur** : Cibles par indicateur, déclinables par commune et année
4. **Intervention** : Activités (immatériel) + Réalisations (matériel)
   - Champ `nature` : ACTIVITE ou REALISATION
   - Géolocalisation : geom (POINT)
   - **Workflow simplifié** : PROGRAMME → TERMINE ou ANNULEE
   - Relations : Many-to-Many avec Acteur et Infrastructure
   - Champ `notes` pour commentaires
5. **ValeurIndicateur** : Saisie trimestrielle des valeurs
   - Source : SAISIE_MANUELLE, CALCUL_AUTO, IMPORT_EXTERNE
   - Statut : BROUILLON, VALIDE, PUBLIE

### Entités Géolocalisées (geo)
1. **Infrastructure** : Infrastructures avec geom (POINT)
   - Champs : nb_beneficiaires, statut, cout_construction, caracteristiques (JSON)
2. **Acteur** : Organisations/Groupements avec geom (POINT)
   - Composition : nb_adherents, nb_femmes, nb_hommes, nb_jeunes
   - Contact : responsable, telephone, email
   - Domaines d'activité en JSON

### Monitoring Sécurité (securite)
1. **TypeInsecurite** : Conflits fonciers, Vol de bétail, Tensions intercommunautaires
2. **SecurityReport** : Rapports géolocalisés (POINT)
   - Gravité : FAIBLE, MOYENNE, ELEVEE, CRITIQUE
   - Workflow de résolution avec traçabilité
   - Confidentialité pour données sensibles

### Workflow de Validation

**Pour les Interventions** (simplifié) :
```
PROGRAMME → TERMINE (contribue aux indicateurs) ou ANNULEE
```

**Pour les ValeurIndicateur** (complet) :
```
BROUILLON → VALIDE → PUBLIE
```

## 🔧 Commandes Importantes

### Développement
```bash
# Démarrer le serveur
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Initialiser les données de base (à adapter à la v2)
python init_data.py

# Créer des données de demo (à adapter à la v2)
python demo_data.py

# Accéder à la base PostgreSQL
python manage.py dbshell
```

### Accès aux Interfaces
- **Interface publique** : http://localhost:8000/public/
- **Dashboard admin** : http://localhost:8000/dashboard/ (login requis)
- **Admin Django** : http://localhost:8000/admin/

**Compte admin** : `admin` / `admin123`

## 🎯 Objectifs et Contraintes

### Fonctionnalités Clés Implémentées ✅
- Architecture multi-projets avec isolation des données
- Modèle géospatial complet (PostGIS)
- Interface d'administration avec dashboard interactif
- Suivi des indicateurs avec calcul automatique depuis les interventions
- **Formulaire personnalisé de création d'interventions** (dashboard)
- **Gestion simplifiée des statuts** (PROGRAMME/TERMINE/ANNULEE)
- **Page de détail par thématique** avec statistiques et interventions
- **Dashboard interactif** avec cards cliquables et activités récentes
- Interface publique responsive avec statistiques

### Prochaines Étapes (Roadmap)
1. **Adapter init_data.py et demo_data.py** : Générer les données pour la nouvelle structure
2. **Adapter les vues dashboard** : Utiliser les nouveaux modèles (déjà fait partiellement)
3. **Intégration KoboToolbox** : API REST pour import automatique
4. **Cartographie avancée** : Leaflet.js avec marqueurs interactifs
5. **Module webstories** : Pages de capitalisation
6. **Export PDC** : Plans de Développement Communaux
7. **API REST** : Pour applications mobiles

### Contraintes Techniques
- **Performance** : Optimisation pour 14 700 bénéficiaires
- **Géolocalisation** : Support PostGIS obligatoire (SRID 4326)
- **Sécurité** : Validation stricte des données terrain + isolation par projet
- **Multilingue** : Interface en français (projet sénégalais)

## 🗂️ Organisation des Fichiers

### Templates
```
dashboard/templates/dashboard/        # Interface admin
├── base.html                        # Layout principal avec sidebar
├── home.html                        # Tableau de bord avec graphiques et cards cliquables
├── indicateurs.html                 # Suivi des indicateurs
├── activites.html                   # Ancienne gestion des interventions (à remplacer)
├── liste_interventions.html         # Liste des interventions avec actions
├── creer_intervention.html          # Formulaire de création d'intervention
├── thematique_detail.html           # Détail d'une thématique
├── creer_thematiques.html           # Gestion des thématiques
├── configurer_indicateurs.html      # Configuration des indicateurs
└── menu_configuration.html          # Menu de configuration

public/templates/public/             # Interface publique
└── home.html                        # Page d'accueil publique
```

### Scripts Utilitaires
- **init_data.py** : Données de base (Projet, Communes, Types, Thématiques, Indicateurs)
- **demo_data_v2.py** : Données avec 66% d'avancement uniforme (JAMM-LEYDI-V2)
- **demo_data_v3.py** : Données avec progression variable 75%/50%/40% (JAMM-LEYDI-V3) ⭐ **Recommandé**
- **debug_calcul.py** : Script de diagnostic des calculs de pourcentages

## ⚙️ Configuration

### Settings Importants
```python
# settings.py
AUTH_USER_MODEL = 'core.User'  # Modèle User personnalisé
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Dakar'

# Configuration GDAL/GEOS pour Windows (utilise QGIS)
if os.name == 'nt':
    OSGEO_PATH = r'C:\Program Files\QGIS 3.40.7\bin'
    GDAL_LIBRARY_PATH = os.path.join(OSGEO_PATH, 'gdal310.dll')
    GEOS_LIBRARY_PATH = os.path.join(OSGEO_PATH, 'geos_c.dll')
    os.environ['PATH'] = OSGEO_PATH + os.pathsep + os.environ['PATH']

# Base de données PostgreSQL/PostGIS
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'jamm_leydi',
        'USER': 'postgres',
        'PASSWORD': 'MvawpPky7_',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Variables d'Environnement (Production)
```bash
SECRET_KEY=clé-secrète-production
DATABASE_URL=postgres://user:pass@host/jamm_leydi
DEBUG=False
ALLOWED_HOSTS=domaine.com
```

## 🔍 Points d'Attention

### Sécurité
- Toutes les vues dashboard nécessitent une authentification (`@login_required`)
- Isolation par projet (filtre automatique sur UserProjet)
- Interface publique en accès libre pour la communication
- Upload de fichiers sécurisé pour les photos

### Performance
- Requêtes optimisées avec `select_related` et `prefetch_related`
- Index créés automatiquement sur les champs géographiques (PostGIS)
- Pagination recommandée pour les listes longues
- Cache à prévoir pour les graphiques du dashboard

### GeoDjango
- **SRID** : 4326 (WGS84) pour tous les champs géographiques
- **Types** : POINT pour localisations, MULTIPOLYGON pour contours
- **Calculs spatiaux** : Centroïde auto-calculé pour CommuneGeom
- **Cartographie** : Compatible OpenStreetMap et Leaflet.js

### UX/UI
- Design responsive mobile-first
- Navigation intuitive avec sidebar fixe
- Feedback visuel pour les actions (validation, etc.)

## 🤝 Collaboration

### Tests à Effectuer
1. **Fonctionnels** : Workflow complet de saisie → validation → publication
2. **Géospaciaux** : Requêtes spatiales (distance, intersection)
3. **Interface** : Test sur mobile/tablette/desktop
4. **Performance** : Temps de chargement avec données volumineuses
5. **Sécurité** : Tentatives d'accès non autorisé + isolation projets

### Code Style
- **Docstrings** en français pour les fonctions métier
- **Noms de variables** explicites (française ou anglais selon le contexte)
- **Templates** : Structure modulaire avec héritage Django
- **Modèles** : Utiliser `gis_models` pour les champs géographiques

## 📐 Choix Architecturaux Clés

### Fusion Activité/Réalisation
**Avant** : 2 tables séparées
**Après** : Table unique `Intervention` avec champ `nature` (ACTIVITE / REALISATION)

**Avantages** :
- Modèle simplifié
- Requêtes unifiées
- Workflow de validation commun

### Multi-Projets
Permet de gérer plusieurs projets GRDR sur la même plateforme avec isolation complète des données.

### Suivi Temporel Flexible
`ValeurIndicateur` avec `date_mesure` (pas de trimestre fixe) :
- Flexibilité pour saisies à n'importe quelle date
- Propriété `trimestre` calculée automatiquement
- Permet graphiques d'évolution sur mesure

## 📋 URLs Disponibles

### Dashboard (authentification requise)
```
/dashboard/                                      # Tableau de bord principal
/dashboard/indicateurs/                          # Suivi des indicateurs
/dashboard/activites/                            # Anciennes activités (à supprimer)

# Interventions
/dashboard/interventions/                        # Liste des interventions
/dashboard/interventions/creer/                  # Créer une intervention
/dashboard/interventions/<id>/changer-statut/    # Changer le statut (AJAX)

# Thématiques
/dashboard/thematique/<id>/                      # Détail d'une thématique

# Configuration
/dashboard/configuration/                        # Menu de configuration
/dashboard/configuration/thematiques/            # Gérer les thématiques
/dashboard/configuration/indicateurs/            # Gérer les indicateurs
/dashboard/configuration/parametres/             # Paramètres finaux

# Authentification
/dashboard/logout/                               # Déconnexion
```

### Admin Django
```
/admin/                                          # Interface d'administration Django
```

### Public (accès libre)
```
/public/                                         # Page d'accueil publique
```

## 🔄 Calcul des Indicateurs

**Logique de calcul** :
- Les **interventions terminées** (statut `TERMINE`) contribuent automatiquement aux indicateurs
- Le dashboard calcule les pourcentages en temps réel : `total_realise / total_cible`
- `total_realise` = Somme des `valeur_quantitative` des interventions terminées
- `total_cible` = Somme des `CibleIndicateur` (globales, année 2025)

**Important** : Les interventions avec statut `PROGRAMME` ou `ANNULEE` ne comptent PAS dans les réalisations.

## 📈 Données de Démonstration

### Projets Disponibles

| Projet | Description | Utilisation |
|--------|-------------|-------------|
| **JAMM-LEYDI-V3** ⭐ | Progression variable (R1: 75%, R2: 50%, R3: 40%) | Dashboard réaliste avec 82 interventions (42 terminées, 40 programmées) |
| **JAMM-LEYDI-V2** | Avancement uniforme 66% | Tests de cohérence des calculs |

### Génération des Données

```bash
# Données recommandées pour démo
echo "oui" | venv/Scripts/python.exe demo_data_v3.py

# Diagnostic des calculs
venv/Scripts/python.exe debug_calcul.py

# Données avec avancement uniforme (optionnel)
echo "oui" | venv/Scripts/python.exe demo_data_v2.py
```

### Structure des Données V3
- **3 thématiques** : R1, R2, R3 avec progressions différentes
- **9 indicateurs** : Avec cibles réalistes par commune
- **82 interventions** :
  - 42 TERMINE (comptent dans les KPI)
  - 40 PROGRAMME (planifiées, ne comptent pas encore)
- **Communes** : Gathiary, Toumboura, Médina Foulbé, Sadatou

---

*Dernière mise à jour : 2025-11-18*

---

## 🔄 Protocole de Clôture de Session

Quand l'utilisateur dit **"clôture proprement cette session"**, effectuer :

1. **TODO.md** : Mettre à jour
   - Cocher `[x]` les tâches terminées
   - Ajouter les nouvelles tâches identifiées
   - Réorganiser les priorités si nécessaire

2. **DEVLOG.md** : Ajouter une entrée
   - Date et titre de session
   - Objectifs / Réalisations / Fichiers modifiés / Prochaines étapes

3. **CLAUDE.md** : Mettre à jour si nécessaire
   - Nouvelles URLs, commandes, ou informations techniques
   - Date de dernière mise à jour

### Format de rapport client

Le DEVLOG permet de générer un rapport pour le client avec :
- Avancement par session
- Fonctionnalités livrées
- Prochaines étapes claires

### Bonnes pratiques

- **Objectifs réalistes** : Découper en tâches de 1-2h max
- **Itérations courtes** : Livrer régulièrement des fonctionnalités testables
- **Documentation** : Tout changement significatif doit être tracé
