# 🌍 JAMM LEYDI

> Plateforme de suivi, pilotage et capitalisation pour projets de prévention des conflits liés au changement climatique

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.4-orange.svg)](https://postgis.net/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()

---

## 📋 Table des matières

- [À propos](#à-propos)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Documentation](#documentation)
- [Contribution](#contribution)

---

## 🎯 À propos

**JAMM LEYDI** (Paix dans le Territoire en Pulaar) est une plateforme web de suivi et pilotage développée pour le projet de prévention des conflits liés au changement climatique dans l'arrondissement de Kéniéba (Sénégal).

### Contexte du projet

- **Client** : GRDR (Migration Citoyenneté Développement)
- **Bailleur** : Union Européenne
- **Zone** : 4 communes (Gathiary, Toumboura, Médina Foulbé, Sadatou)
- **Objectif** : 14 700 bénéficiaires ciblés
- **Durée** : En cours jusqu'en 2026

---

## ✨ Fonctionnalités

### 🗺️ Cartographie SIG 3D
- Interface innovante type "command center" avec MapLibre GL JS
- Vue isométrique 3D avec rotation libre de la caméra
- 4 couches géospatiales interactives (communes, interventions, infrastructures, acteurs)
- Popups détaillés avec statistiques temps réel
- Design glassmorphism élégant et moderne

### 📊 Tableau de bord interactif
- Dashboard avec cards cliquables par thématique
- Graphiques Chart.js pour visualisation des données
- Suivi des indicateurs en temps réel
- Calcul automatique des taux d'avancement

### 🎯 Gestion des interventions
- Workflow simplifié (PROGRAMME → TERMINE / ANNULEE)
- Formulaire personnalisé de création
- Géolocalisation des activités (Point)
- Relations Many-to-Many avec acteurs et infrastructures

### 👥 Multi-projets & Multi-utilisateurs
- Gestion de plusieurs projets GRDR sur la même plateforme
- Isolation complète des données par projet
- Système de rôles (Admin projet, Contributeur, Lecteur)

### 🌐 Interface publique
- Page d'accueil responsive pour communication externe
- Statistiques publiques du projet
- Design modern et accessible

---

## 🏗️ Architecture

### Stack technique

```
Backend:  Django 5.2.7 (Python)
Database: PostgreSQL 16 + PostGIS 3.4
Frontend: Bootstrap 5 + Chart.js + MapLibre GL JS
Auth:     Django Auth personnalisé
```

### Structure des applications

```
jamm-leydi/
├── core/          # Multi-projets & utilisateurs
├── referentiels/  # Données mutualisées (Commune, Types)
├── suivi/         # Suivi des indicateurs et interventions
├── geo/           # Entités géolocalisées (Infrastructure, Acteur)
├── securite/      # Monitoring sécurité
├── dashboard/     # Interface d'administration
├── public/        # Interface publique
└── accueil/       # Landing page
```

Pour plus de détails, consultez [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🚀 Installation

### Prérequis

- Python 3.11+
- PostgreSQL 16 avec extension PostGIS 3.4
- QGIS 3.40+ (pour GDAL/GEOS sous Windows)

### 1. Cloner le repository

```bash
git clone https://github.com/votre-org/jamm-leydi.git
cd jamm-leydi
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration PostgreSQL

```bash
# Créer la base de données
psql -U postgres
CREATE DATABASE jamm_leydi;
CREATE EXTENSION postgis;
\q
```

### 5. Variables d'environnement

Copier `.env.example` vers `.env` et configurer :

```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

### 6. Migrations

```bash
python manage.py migrate
```

### 7. Initialiser les données

```bash
# Données de base (communes, types, etc.)
python init_data.py

# Données de démonstration (optionnel)
python scripts/demo/demo_data_v3.py
```

### 8. Créer un superuser

```bash
python manage.py createsuperuser
```

### 9. Lancer le serveur

```bash
python manage.py runserver
```

Accéder à : http://localhost:8000

---

## ⚙️ Configuration

### Variables d'environnement (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Clé secrète Django | **REQUIRED** |
| `DEBUG` | Mode debug | `True` |
| `ALLOWED_HOSTS` | Hosts autorisés | `localhost,127.0.0.1` |
| `DB_NAME` | Nom de la BDD | `jamm_leydi` |
| `DB_USER` | Utilisateur PostgreSQL | `postgres` |
| `DB_PASSWORD` | Mot de passe BDD | **REQUIRED** |
| `DB_HOST` | Host PostgreSQL | `localhost` |
| `DB_PORT` | Port PostgreSQL | `5432` |

### Configuration GDAL (Windows)

Si vous utilisez QGIS :

```env
GDAL_LIBRARY_PATH=C:\Program Files\QGIS 3.40.7\bin\gdal310.dll
GEOS_LIBRARY_PATH=C:\Program Files\QGIS 3.40.7\bin\geos_c.dll
```

---

## 📖 Utilisation

### Accès aux interfaces

| Interface | URL | Authentification |
|-----------|-----|------------------|
| Dashboard admin | `/dashboard/` | Requise |
| Cartographie SIG | `/dashboard/carte/` | Requise |
| Admin Django | `/admin/` | Requise (superuser) |
| Interface publique | `/public/` | Libre |

### Compte de démonstration

```
Username: admin
Password: admin123
```

### Workflow de base

1. **Configuration initiale** (`/dashboard/configuration/`)
   - Créer les thématiques (R1, R2, R3)
   - Configurer les indicateurs avec cibles
   - Définir les paramètres du projet

2. **Saisie des interventions** (`/dashboard/interventions/`)
   - Créer une intervention
   - Associer à un indicateur
   - Géolocaliser (optionnel)
   - Définir le statut

3. **Suivi** (`/dashboard/`)
   - Visualiser les KPI en temps réel
   - Consulter le dashboard par thématique
   - Analyser les cartes SIG

---

## 📚 Documentation

- [Architecture technique](docs/ARCHITECTURE.md)
- [Guide de déploiement](docs/DEPLOYMENT.md)
- [Guide de développement](docs/DEVELOPMENT.md)
- [Configuration Claude](.claudemd)

---

## 🤝 Contribution

Ce projet est développé pour le GRDR. Pour toute contribution :

1. Créer une branche feature : `git checkout -b feature/nouvelle-fonctionnalite`
2. Commiter les changements : `git commit -m "✨ Feat: Description"`
3. Push vers la branche : `git push origin feature/nouvelle-fonctionnalite`
4. Créer une Pull Request

### Conventions de commit

```
✨ Feat: Nouvelle fonctionnalité
🐛 Fix: Correction de bug
📝 Docs: Documentation
🎨 Style: Formatage, style
♻️ Refactor: Refactorisation
⚡ Perf: Performance
✅ Test: Tests
🔧 Chore: Configuration
```

---

## 📄 License

Proprietary - GRDR © 2025

---

## 👥 Équipe

- **Client** : GRDR Migration Citoyenneté Développement
- **Développement** : [Votre équipe]
- **Support** : contact@grdr.org

---

## 🙏 Remerciements

- Union Européenne (financement)
- Communes de Kéniéba
- Partenaires locaux

---

**Fait avec ❤️ pour la paix et le développement durable au Sénégal**
