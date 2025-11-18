# Architecture Technique - JAMM LEYDI

> Documentation détaillée de l'architecture du système

---

## Vue d'ensemble

JAMM LEYDI est une plateforme Django de suivi et pilotage de projets de développement, avec des fonctionnalités SIG avancées (PostGIS, MapLibre GL JS).

### Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Django | 5.2.7 |
| Langage | Python | 3.11+ |
| Base de données | PostgreSQL + PostGIS | 16 + 3.4 |
| Frontend | Bootstrap 5 | 5.x |
| Cartographie | MapLibre GL JS | 4.x |
| Graphiques | Chart.js | 4.x |
| Géospatial | GDAL/GEOS | via QGIS (Windows) |

---

## Structure des Applications

```
jamm-leydi/
├── jamm_leydi/        # Configuration Django (settings, urls, wsgi)
├── core/              # Multi-projets & utilisateurs
├── referentiels/      # Données mutualisées (communes, types)
├── suivi/             # Suivi des indicateurs et interventions
├── geo/               # Entités géolocalisées (infrastructures, acteurs)
├── securite/          # Monitoring sécurité
├── dashboard/         # Interface d'administration
├── public/            # Interface publique
├── accueil/           # Landing page
├── static/            # Fichiers statiques
├── media/             # Uploads utilisateurs
├── scripts/           # Scripts utilitaires
└── docs/              # Documentation
```

---

## Modèles de Données

### Application `core` - Gestion Multi-projets

Gère les utilisateurs et l'isolation des données par projet.

```
User (AbstractUser)
├── telephone
└── organisation

Projet
├── code_projet (unique)
├── libelle
├── zone_intervention
├── bailleurs
├── date_debut / date_fin
├── budget / devise
├── statut (EN_COURS, TERMINE, SUSPENDU, PLANIFIE)
└── equipe_grdr -> EquipeGRDR

UserProjet (table de liaison)
├── user -> User
├── projet -> Projet
└── role (ADMIN_PROJET, CONTRIBUTEUR, LECTEUR)
```

### Application `referentiels` - Données Mutualisées

Données partagées entre tous les projets.

```
Commune
├── nom
├── code
└── geom (MultiPolygon)

TypeIntervention
├── code
├── libelle
└── categorie

EquipeGRDR
├── nom
└── description
```

### Application `suivi` - Coeur Métier

Gestion des indicateurs et interventions.

```
Thematique
├── projet -> Projet
├── code (ex: R1, R2, R3)
├── libelle
└── ordre

Indicateur
├── projet -> Projet
├── thematique -> Thematique
├── code (ex: R1.1, R2.3)
├── libelle
├── unite_mesure
├── type_calcul (SOMME, MOYENNE, DENOMBREMENT, MANUEL)
└── ordre

CibleIndicateur
├── indicateur -> Indicateur
├── commune -> Commune (nullable = global)
├── valeur_cible
└── annee

Intervention (avec géométrie)
├── projet -> Projet
├── indicateur -> Indicateur
├── type_intervention -> TypeIntervention
├── commune -> Commune
├── nature (ACTIVITE, REALISATION)
├── libelle / description
├── valeur_quantitative
├── date_intervention
├── geom (Point)
├── statut (PROGRAMME, TERMINE, ANNULEE)
├── cree_par -> User
└── valide_par -> User

ValeurIndicateur
├── indicateur -> Indicateur
├── commune -> Commune (nullable = global)
├── valeur_realisee
├── date_mesure
├── source (SAISIE_MANUELLE, CALCUL_AUTO, IMPORT_EXTERNE)
└── statut (BROUILLON, VALIDE, PUBLIE)
```

### Application `geo` - Entités Géolocalisées

```
Infrastructure
├── nom
├── type_infrastructure
├── commune -> Commune
└── geom (Point)

Acteur
├── nom
├── type_acteur
├── commune -> Commune
└── geom (Point)
```

### Tables de Liaison

```
InterventionActeur
├── intervention -> Intervention
├── acteur -> Acteur
└── role

InterventionInfrastructure
├── intervention -> Intervention
├── infrastructure -> Infrastructure
└── commentaire
```

---

## Diagramme des Relations

```
                    ┌─────────────┐
                    │  EquipeGRDR │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Projet    │◄──────────┐
                    └──────┬──────┘           │
          ┌────────────────┼────────────┐     │
          │                │            │     │
   ┌──────▼──────┐  ┌──────▼──────┐    │     │
   │ Thematique  │  │  UserProjet │    │     │
   └──────┬──────┘  └─────────────┘    │     │
          │                            │     │
   ┌──────▼──────┐              ┌──────▼─────┴┐
   │ Indicateur  │◄─────────────┤ Intervention│
   └──────┬──────┘              └──────┬──────┘
          │                            │
   ┌──────▼──────────┐          ┌──────▼──────┐
   │ CibleIndicateur │          │   Commune   │
   └─────────────────┘          └─────────────┘

   ┌─────────────────┐
   │ ValeurIndicateur│
   └─────────────────┘
```

---

## Isolation des Données par Projet

### Principe

Chaque projet a ses propres :
- Thématiques
- Indicateurs
- Cibles
- Interventions
- Utilisateurs (via UserProjet)

Les données mutualisées (Commune, TypeIntervention) sont partagées.

### Implémentation

1. **Foreign Keys** : Tous les modèles métier ont une FK vers `Projet`
2. **Filtrage automatique** : Les vues filtrent par projet actif
3. **Validation** : `clean()` vérifie la cohérence projet/thématique/indicateur

```python
# Exemple : Récupérer les interventions d'un projet
projet = Projet.objects.get(code_projet='JAMM-LEYDI-2024')
interventions = Intervention.objects.filter(projet=projet)

# Avec les indicateurs du projet
indicateurs = projet.indicateurs.all()
```

---

## Composants Frontend

### MapLibre GL JS (Cartographie 3D)

Interface cartographique avec :
- Vue isométrique 3D
- 4 couches : Communes, Interventions, Infrastructures, Acteurs
- Popups interactifs avec statistiques
- Design glassmorphism

**Fichier** : `dashboard/templates/dashboard/carte.html`

### Chart.js (Graphiques)

Visualisation des données :
- Barres horizontales pour les indicateurs
- Doughnut pour les répartitions
- Lignes pour l'évolution temporelle

**Fichiers** : `dashboard/templates/dashboard/` (*.html)

### Bootstrap 5 (UI)

- Cards cliquables par thématique
- Tables responsives
- Formulaires stylisés
- Modals pour les détails

---

## Sécurité

### Authentification

- Django Auth avec modèle User personnalisé
- Rôles par projet (ADMIN_PROJET, CONTRIBUTEUR, LECTEUR)
- Middleware pour isolation des données

### Protection des Secrets

- Variables sensibles dans `.env` (python-decouple)
- `.gitignore` pour exclure les fichiers sensibles
- SECRET_KEY et DB_PASSWORD hors du code

### Configuration Production

```python
# settings.py (en production)
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## Fonctionnalités SIG

### PostGIS

- Extension PostgreSQL pour données géospatiales
- Types : Point (interventions), MultiPolygon (communes)
- SRID 4326 (WGS84)

### GDAL/GEOS

- Requis pour Django GeoDjango
- Windows : via QGIS
- Linux : packages système (`libgdal-dev`, `libgeos-dev`)

### Configuration Windows

```python
# settings.py
OSGEO_PATH = r'C:\Program Files\QGIS 3.40.7\bin'
GDAL_LIBRARY_PATH = os.path.join(OSGEO_PATH, 'gdal310.dll')
GEOS_LIBRARY_PATH = os.path.join(OSGEO_PATH, 'geos_c.dll')
```

---

## API Endpoints

### Dashboard (authentifié)

| URL | Description |
|-----|-------------|
| `/dashboard/` | Tableau de bord principal |
| `/dashboard/carte/` | Cartographie SIG 3D |
| `/dashboard/interventions/` | Liste des interventions |
| `/dashboard/configuration/` | Configuration projet |

### Public (libre)

| URL | Description |
|-----|-------------|
| `/` | Page d'accueil |
| `/public/` | Interface publique |

### Admin Django

| URL | Description |
|-----|-------------|
| `/admin/` | Administration Django |

---

## Flux de Données

### Création d'une Intervention

1. Utilisateur accède à `/dashboard/interventions/nouveau/`
2. Sélectionne projet, indicateur, commune
3. Remplit les détails (libellé, date, géolocalisation)
4. Validation côté serveur (`clean()`)
5. Sauvegarde en BDD avec traçabilité

### Calcul des KPI

1. Requête sur `Intervention` filtrée par projet
2. Agrégation par indicateur (SOMME, MOYENNE, etc.)
3. Comparaison avec `CibleIndicateur`
4. Calcul du taux d'avancement
5. Affichage dans les cards du dashboard

---

## Performance

### Index de Base de Données

```python
# suivi/models.py
class Intervention:
    class Meta:
        indexes = [
            models.Index(fields=['projet', 'indicateur', 'commune', 'date_intervention']),
            models.Index(fields=['projet', 'statut']),
        ]
```

### Optimisations

- `select_related()` pour les FK
- `prefetch_related()` pour les M2M
- Pagination des listes
- Cache des statistiques (à implémenter)

---

## Tests

### Structure Recommandée

```
tests/
├── test_models.py      # Tests des modèles
├── test_views.py       # Tests des vues
├── test_api.py         # Tests API
└── test_calculs.py     # Tests logique métier
```

### Exécution

```bash
python manage.py test
```

---

## Évolutions Futures

1. **API REST** : Django REST Framework pour intégration externe
2. **Import Kobo** : Synchronisation avec Kobo Toolbox
3. **Export PDF** : Rapports automatisés
4. **Multi-langue** : i18n Django
5. **Cache Redis** : Performance des dashboards

---

*Documentation Architecture - JAMM LEYDI v2.0*
*Dernière mise à jour : 2025-11-18*
