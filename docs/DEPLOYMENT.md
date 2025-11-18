# Guide de Déploiement - JAMM LEYDI

## Prérequis Serveur

### Système d'exploitation
- Ubuntu 22.04 LTS ou Debian 11+ recommandé
- Minimum 2GB RAM, 20GB disque

### Logiciels requis

#### 1. PostgreSQL avec PostGIS
```bash
# Installation PostgreSQL 16 + PostGIS 3.4
sudo apt update
sudo apt install postgresql-16 postgresql-16-postgis-3.4
sudo apt install postgresql-server-dev-16

# Démarrer le service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 2. GDAL/GEOS/PROJ (pour GeoDjango)
```bash
# Installation des bibliothèques géospatiales
sudo apt install gdal-bin libgdal-dev
sudo apt install libgeos-dev
sudo apt install proj-bin libproj-dev

# Vérifier les versions
gdalinfo --version  # Doit être >= 3.0
```

#### 3. Python 3.12
```bash
sudo apt install python3.12 python3.12-venv python3.12-dev
sudo apt install python3-pip
```

## Configuration de la Base de Données

### Créer la base PostgreSQL avec PostGIS
```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Dans psql :
CREATE DATABASE jamm_leydi;
CREATE USER jamm_user WITH PASSWORD 'votre_mot_de_passe_securise';

# Activer PostGIS
\c jamm_leydi
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

# Donner les permissions
GRANT ALL PRIVILEGES ON DATABASE jamm_leydi TO jamm_user;
GRANT ALL ON SCHEMA public TO jamm_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO jamm_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO jamm_user;

\q
```

## Déploiement de l'Application

### 1. Cloner le repository
```bash
cd /var/www/
sudo git clone https://github.com/studio-noble-val/jamm-leydi-claude.git
sudo chown -R www-data:www-data jamm-leydi-claude
cd jamm-leydi-claude
```

### 2. Créer l'environnement virtuel
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### 3. Installer les dépendances
```bash
# Les bibliothèques GDAL/GEOS sont déjà installées au niveau système
# Python les détectera automatiquement
pip install -r requirements.txt
```

### 4. Variables d'environnement de production

Créer un fichier `.env` :
```bash
nano .env
```

Contenu :
```env
# Django
SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# Base de données
DATABASE_URL=postgis://jamm_user:votre_mot_de_passe_securise@localhost:5432/jamm_leydi

# GDAL/GEOS (généralement détecté automatiquement sur Linux)
# Si besoin de spécifier :
# GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
# GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so
```

### 5. Configuration Django pour production

Modifier `jamm_leydi/settings.py` pour charger les variables d'environnement :

```python
import os
from pathlib import Path
import dj_database_url

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Base de données
DATABASES = {
    'default': dj_database_url.config(
        default='postgis://localhost/jamm_leydi',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Sur Linux, GDAL/GEOS sont généralement détectés automatiquement
# Pas besoin de configuration spéciale comme sur Windows
if os.name != 'nt':
    # Linux - détection automatique
    pass
else:
    # Windows - configuration QGIS (développement uniquement)
    OSGEO_PATH = r'C:\Program Files\QGIS 3.40.7\bin'
    GDAL_LIBRARY_PATH = os.path.join(OSGEO_PATH, 'gdal310.dll')
    GEOS_LIBRARY_PATH = os.path.join(OSGEO_PATH, 'geos_c.dll')
    os.environ['PATH'] = OSGEO_PATH + os.pathsep + os.environ['PATH']

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

### 6. Migrations et collecte des fichiers statiques
```bash
# Appliquer les migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Créer un superutilisateur
python manage.py createsuperuser
```

## Serveur Web (Gunicorn + Nginx)

### 1. Installer Gunicorn
```bash
pip install gunicorn
```

### 2. Créer un service systemd

```bash
sudo nano /etc/systemd/system/jamm-leydi.service
```

Contenu :
```ini
[Unit]
Description=JAMM LEYDI Django Application
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/jamm-leydi-claude
Environment="PATH=/var/www/jamm-leydi-claude/venv/bin"
ExecStart=/var/www/jamm-leydi-claude/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/jamm-leydi-claude/jamm-leydi.sock \
    --timeout 60 \
    --access-logfile /var/log/jamm-leydi/access.log \
    --error-logfile /var/log/jamm-leydi/error.log \
    jamm_leydi.wsgi:application

[Install]
WantedBy=multi-user.target
```

Créer le répertoire de logs :
```bash
sudo mkdir -p /var/log/jamm-leydi
sudo chown www-data:www-data /var/log/jamm-leydi
```

Activer et démarrer :
```bash
sudo systemctl daemon-reload
sudo systemctl start jamm-leydi
sudo systemctl enable jamm-leydi
sudo systemctl status jamm-leydi
```

### 3. Configurer Nginx

```bash
sudo nano /etc/nginx/sites-available/jamm-leydi
```

Contenu :
```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/jamm-leydi-claude/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/jamm-leydi-claude/media/;
        expires 7d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/jamm-leydi-claude/jamm-leydi.sock;
        proxy_read_timeout 60s;
    }
}
```

Activer le site :
```bash
sudo ln -s /etc/nginx/sites-available/jamm-leydi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. SSL avec Let's Encrypt (recommandé)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
```

## Dépendances à ajouter dans requirements.txt

Créer/mettre à jour `requirements.txt` :
```bash
pip freeze > requirements.txt
```

Ajouter si nécessaire :
```
dj-database-url>=2.0.0
python-decouple>=3.8
gunicorn>=21.0.0
```

## Vérifications Post-Déploiement

### 1. Test de la base PostGIS
```bash
python manage.py shell
```

Dans le shell Python :
```python
from django.contrib.gis.geos import Point
from django.contrib.gis.gdal import HAS_GDAL
print(f"GDAL disponible: {HAS_GDAL}")

# Test de création d'un point
p = Point(-12.5, 14.2, srid=4326)
print(f"Point créé: {p}")
```

### 2. Test de l'admin
- Accéder à https://votre-domaine.com/admin/
- Créer/modifier une intervention
- Vérifier que la carte OpenLayers fonctionne

### 3. Monitoring
```bash
# Logs applicatifs
tail -f /var/log/jamm-leydi/error.log

# Logs Nginx
tail -f /var/log/nginx/error.log

# Logs PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

## Maintenance

### Mise à jour de l'application
```bash
cd /var/www/jamm-leydi-claude
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart jamm-leydi
```

### Backup de la base de données
```bash
# Créer un backup
sudo -u postgres pg_dump jamm_leydi > backup_$(date +%Y%m%d_%H%M%S).sql

# Avec PostGIS (format custom)
sudo -u postgres pg_dump -Fc jamm_leydi > backup_$(date +%Y%m%d_%H%M%S).dump
```

### Restauration
```bash
# Depuis un fichier SQL
sudo -u postgres psql jamm_leydi < backup.sql

# Depuis un fichier dump
sudo -u postgres pg_restore -d jamm_leydi backup.dump
```

## Hébergeurs Recommandés

### Option 1 : VPS Classique
- **DigitalOcean** (Droplet Ubuntu) - 12$/mois
- **OVH VPS** - à partir de 7€/mois
- **Scaleway** - à partir de 7€/mois

Avantages : Contrôle total, installation GDAL facile

### Option 2 : PaaS (Platform as a Service)
- **Heroku** avec buildpack GeoDjango
- **Railway.app** avec support PostGIS
- **Render.com** avec support GeoDjango

Avantages : Déploiement simplifié, scaling automatique

### Option 3 : Hébergement local Sénégal
- **Orange Cloud for Business Sénégal**
- **Sonatel Cloud**

Avantages : Données hébergées localement, latence réduite

## Particularités GeoDjango sur Serveur

### Sur Ubuntu/Debian (recommandé)
✅ Installation simple avec `apt`
✅ GDAL/GEOS détectés automatiquement
✅ Pas de configuration PATH nécessaire
✅ Pas de conflit PostgreSQL/QGIS

### Important
- **Pas besoin de QGIS sur le serveur** (contrairement au développement Windows)
- Les bibliothèques système (`libgdal`, `libgeos`) suffisent
- Django GeoDjango détecte automatiquement les chemins sur Linux

---

*Guide de déploiement - JAMM LEYDI v2.0*
*Dernière mise à jour : 2025-11-11*
