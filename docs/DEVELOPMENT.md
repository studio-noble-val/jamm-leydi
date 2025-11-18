# Guide de Développement - JAMM LEYDI

> Instructions pour les développeurs travaillant sur le projet

---

## Prérequis

### Logiciels Requis

| Logiciel | Version | Notes |
|----------|---------|-------|
| Python | 3.11+ | Avec pip |
| PostgreSQL | 16+ | Avec extension PostGIS 3.4 |
| QGIS | 3.40+ | Pour GDAL/GEOS (Windows uniquement) |
| Git | 2.x | Contrôle de version |

### Configuration Windows (GDAL/GEOS)

Sur Windows, les bibliothèques GDAL/GEOS sont fournies par QGIS :

1. Installer QGIS depuis [qgis.org](https://qgis.org)
2. Le script `run_server.bat` configure automatiquement les variables d'environnement

---

## Installation de l'Environnement de Développement

### 1. Cloner le Repository

```bash
git clone https://github.com/votre-org/jamm-leydi.git
cd jamm-leydi
```

### 2. Créer l'Environnement Virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Installer les Dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les Variables d'Environnement

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos paramètres locaux
# - SECRET_KEY
# - DB_PASSWORD
# - etc.
```

### 5. Configurer PostgreSQL/PostGIS

```sql
-- Se connecter à PostgreSQL
psql -U postgres

-- Créer la base de données
CREATE DATABASE jamm_leydi;
\c jamm_leydi
CREATE EXTENSION postgis;
\q
```

### 6. Appliquer les Migrations

```bash
python manage.py migrate
```

### 7. Initialiser les Données de Base

```bash
# Données de référence (communes, types)
python init_data.py

# Données de démonstration (optionnel)
python scripts/demo/demo_data_v3.py
```

### 8. Créer un Superutilisateur

```bash
python manage.py createsuperuser
```

### 9. Lancer le Serveur

```bash
# Windows (avec configuration GDAL)
run_server.bat

# Linux/Mac
python manage.py runserver
```

Accéder à : http://localhost:8000

---

## Structure du Projet

```
jamm-leydi/
├── .env                    # Variables d'environnement (ignoré par Git)
├── .env.example            # Template des variables
├── .gitignore              # Fichiers ignorés par Git
├── .claudemd               # Configuration Claude Code
├── manage.py               # CLI Django
├── requirements.txt        # Dépendances Python
├── run_server.bat          # Script de lancement Windows
│
├── jamm_leydi/             # Configuration Django
│   ├── settings.py         # Paramètres
│   ├── urls.py             # Routes principales
│   └── wsgi.py             # Point d'entrée WSGI
│
├── core/                   # App: Multi-projets & utilisateurs
├── referentiels/           # App: Données mutualisées
├── suivi/                  # App: Suivi indicateurs
├── geo/                    # App: Entités géolocalisées
├── securite/               # App: Monitoring sécurité
├── dashboard/              # App: Interface admin
├── public/                 # App: Interface publique
├── accueil/                # App: Landing page
│
├── static/                 # Fichiers statiques
├── media/                  # Uploads utilisateurs
├── docs/                   # Documentation
└── scripts/                # Scripts utilitaires
    ├── init/               # Initialisation
    ├── demo/               # Données de démonstration
    ├── testing/            # Tests manuels
    ├── debug/              # Débogage
    └── migrations/         # Scripts de migration
```

---

## Conventions de Code

### Python

- **Style** : PEP 8
- **Docstrings** : Format Google
- **Commentaires** : En français pour la logique métier
- **Type hints** : Recommandés pour les fonctions publiques

```python
def calculer_taux_avancement(indicateur: Indicateur) -> float:
    """
    Calcule le taux d'avancement d'un indicateur.

    Args:
        indicateur: L'indicateur à analyser

    Returns:
        Taux d'avancement entre 0 et 100
    """
    # Récupérer la cible totale
    cible_totale = indicateur.cibles.aggregate(
        total=Sum('valeur_cible')
    )['total'] or 0

    if cible_totale == 0:
        return 0.0

    # Calculer la valeur réalisée
    valeur_realisee = indicateur.interventions.filter(
        statut='TERMINE'
    ).aggregate(
        total=Sum('valeur_quantitative')
    )['total'] or 0

    return min(100.0, (valeur_realisee / cible_totale) * 100)
```

### Django

- **Modèles** : Noms singuliers en français (`Intervention`, `Indicateur`)
- **Vues** : Classes-based views (CBV) préférées
- **Templates** : Nommage `app/template_name.html`
- **URLs** : Nommage avec namespace (`dashboard:home`)

### Git

- **Branches** : `feature/nom-feature`, `fix/nom-bug`
- **Commits** : Messages descriptifs avec emoji

```
✨ Feat: Ajouter filtres par commune sur le dashboard
🐛 Fix: Corriger calcul taux d'avancement
📝 Docs: Mettre à jour guide d'installation
🎨 Style: Formater code avec Black
♻️ Refactor: Simplifier logique de validation
⚡ Perf: Optimiser requêtes dashboard
✅ Test: Ajouter tests pour modèle Intervention
🔧 Chore: Mettre à jour dépendances
```

---

## Workflow de Développement

### 1. Créer une Branche

```bash
git checkout -b feature/ma-fonctionnalite
```

### 2. Développer

- Écrire le code
- Ajouter les tests
- Mettre à jour la documentation si nécessaire

### 3. Tester

```bash
# Tests unitaires
python manage.py test

# Vérifier les migrations
python manage.py makemigrations --check

# Lancer le serveur et tester manuellement
run_server.bat
```

### 4. Commiter

```bash
git add .
git commit -m "✨ Feat: Description de la fonctionnalité"
```

### 5. Push et Pull Request

```bash
git push origin feature/ma-fonctionnalite
```

Créer une Pull Request sur GitHub.

---

## Base de Données

### Migrations

```bash
# Créer une migration après modification de modèle
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Voir le SQL généré
python manage.py sqlmigrate app_name 0001
```

### Accès PostgreSQL

```bash
# Via Django
python manage.py dbshell

# Via psql
psql -U postgres -d jamm_leydi
```

### Requêtes Spatiales (PostGIS)

```python
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

# Créer un point
point = Point(-12.5, 14.2, srid=4326)

# Interventions dans un rayon de 10km
Intervention.objects.filter(
    geom__distance_lte=(point, D(km=10))
)

# Interventions dans une commune (intersection)
commune = Commune.objects.get(nom='Gathiary')
Intervention.objects.filter(geom__within=commune.geom)
```

---

## Templates et Frontend

### Structure des Templates

```
app/
└── templates/
    └── app/
        ├── base.html           # Template de base
        ├── list.html           # Liste
        ├── detail.html         # Détail
        └── includes/
            └── _card.html      # Composants réutilisables
```

### Fichiers Statiques

```
static/
├── css/
│   └── custom.css
├── js/
│   └── dashboard.js
└── img/
    └── logo.png
```

### Collecte des Statiques

```bash
python manage.py collectstatic
```

---

## Débogage

### Django Debug Toolbar

Installé automatiquement en mode DEBUG :

```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### Logs

```python
import logging
logger = logging.getLogger(__name__)

def ma_fonction():
    logger.debug("Message de débogage")
    logger.info("Information")
    logger.warning("Avertissement")
    logger.error("Erreur")
```

### Shell Django

```bash
python manage.py shell

# Dans le shell
from core.models import Projet
from suivi.models import Intervention

projets = Projet.objects.all()
interventions = Intervention.objects.filter(statut='TERMINE')
```

---

## Tests

### Structure

```python
# tests/test_models.py
from django.test import TestCase
from core.models import Projet

class ProjetTestCase(TestCase):
    def setUp(self):
        self.projet = Projet.objects.create(
            code_projet='TEST-001',
            libelle='Projet Test',
            zone_intervention='Zone Test',
            bailleurs='Bailleur Test',
            date_debut='2024-01-01',
            date_fin='2025-12-31'
        )

    def test_projet_str(self):
        self.assertEqual(
            str(self.projet),
            'TEST-001 - Projet Test'
        )

    def test_projet_est_actif(self):
        self.assertTrue(self.projet.est_actif)
```

### Exécution

```bash
# Tous les tests
python manage.py test

# Tests d'une application
python manage.py test core

# Test spécifique
python manage.py test core.tests.ProjetTestCase.test_projet_str

# Avec verbosité
python manage.py test -v 2
```

---

## Outils Recommandés

### IDE

- **VS Code** avec extensions Python, Django
- **PyCharm Professional** (support Django intégré)

### Extensions VS Code

- Python
- Pylance
- Django
- GitLens
- Thunder Client (tests API)

### Linting et Formatage

```bash
# Installation
pip install black flake8 isort

# Formatage
black .

# Linting
flake8

# Tri des imports
isort .
```

---

## Problèmes Courants

### Erreur GDAL/GEOS (Windows)

```
Could not find the GDAL library
```

**Solution** : Utiliser `run_server.bat` qui configure les variables d'environnement, ou vérifier que QGIS est installé.

### Erreur de Migration

```
django.db.utils.ProgrammingError: relation "..." does not exist
```

**Solution** :
```bash
python manage.py migrate --fake-initial
```

### Erreur PostGIS

```
PostGIS extension not found
```

**Solution** :
```sql
\c jamm_leydi
CREATE EXTENSION postgis;
```

---

## Ressources

### Documentation

- [Django Docs](https://docs.djangoproject.com/)
- [Django GeoDjango](https://docs.djangoproject.com/en/5.0/ref/contrib/gis/)
- [PostGIS](https://postgis.net/documentation/)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)
- [Chart.js](https://www.chartjs.org/docs/)

### Tutoriels

- [Real Python Django](https://realpython.com/tutorials/django/)
- [Django Girls Tutorial](https://tutorial.djangogirls.org/)

---

*Guide de Développement - JAMM LEYDI v2.0*
*Dernière mise à jour : 2025-11-18*
