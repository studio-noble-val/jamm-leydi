# 🗺️ Guide d'Intégration SIG - JAMM LEYDI

## Vue d'ensemble

Ce document explique comment intégrer des tables géographiques externes (OpenStreetMap, référentiels nationaux, etc.) dans le projet Django JAMM LEYDI.

## 📐 Principe d'Architecture

### Tables `managed=False`

Toutes les tables géographiques provenant de sources externes doivent être déclarées avec `managed=False` dans Django. Cela signifie que :

- ✅ Django peut **lire** les données
- ✅ Django peut **faire des requêtes** (SELECT, JOIN, etc.)
- ❌ Django ne **crée pas** la table lors des migrations
- ❌ Django ne **modifie pas** la structure de la table
- ❌ Django ne **supprime pas** la table

### Schéma `geo`

Par convention, toutes les tables SIG externes sont placées dans le schéma PostgreSQL `geo` :

```sql
CREATE SCHEMA IF NOT EXISTS geo;
```

## 🛠️ Étapes d'Intégration

### 1. Créer la table PostgreSQL/PostGIS

**Option A : Import depuis fichier (Shapefile, GeoJSON, etc.)**

```bash
# Avec ogr2ogr (GDAL)
ogr2ogr -f "PostgreSQL" \
  PG:"host=localhost dbname=jamm_leydi user=postgres password=***" \
  data.shp \
  -nln geo.ma_table \
  -lco GEOMETRY_NAME=geom \
  -lco SCHEMA=geo

# Avec shp2pgsql (PostGIS)
shp2pgsql -s 4326 -I data.shp geo.ma_table | psql -d jamm_leydi
```

**Option B : Création manuelle**

```sql
CREATE TABLE geo.ma_table (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    geom GEOMETRY(Point, 4326)
);

CREATE INDEX idx_ma_table_geom ON geo.ma_table USING GIST(geom);
```

### 2. Créer le modèle Django

**Fichier : `geo/models.py`**

```python
from django.contrib.gis.db import models as gis_models
from django.db import models


class MaTable(gis_models.Model):
    """
    Description de la table
    Table miroir de geo.ma_table
    """
    nom = models.CharField(max_length=255, help_text="Description")
    geom = gis_models.PointField(srid=4326, null=True, blank=True)

    class Meta:
        db_table = '"geo"."ma_table"'  # ⚠️ Guillemets obligatoires !
        managed = False  # ⚠️ Table gérée hors Django
        verbose_name = "Ma Table"
        verbose_name_plural = "Mes Tables"

    def __str__(self):
        return self.nom
```

### 3. Déclarer dans l'admin Django (optionnel)

**Fichier : `geo/admin.py`**

```python
from django.contrib.gis import admin as gis_admin
from django.contrib import admin
from .models import MaTable


@admin.register(MaTable)
class MaTableAdmin(gis_admin.GISModelAdmin):
    """Administration de Ma Table (lecture seule)"""
    list_display = ('id', 'nom')
    search_fields = ('nom',)
    readonly_fields = ('id', 'nom', 'geom')

    # Vue en lecture seule
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # Optionnel : empêcher les modifications
    def has_change_permission(self, request, obj=None):
        return False
```

### 4. Utiliser comme ForeignKey

**⚠️ IMPORTANT : Utiliser `db_constraint=False`**

```python
from django.db import models


class Projet(models.Model):
    """Exemple d'utilisation d'une table SIG externe"""

    ma_reference = models.ForeignKey(
        'geo.MaTable',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_constraint=False,  # ⚠️ Pas de contrainte FK en base
        related_name='projets',
        help_text="Référence vers ma table SIG"
    )
```

**Pourquoi `db_constraint=False` ?**

- Évite que Django crée une contrainte FOREIGN KEY en base
- Permet plus de flexibilité (la table externe peut être recréée sans casser les relations)
- Évite les erreurs si la table externe est dans un autre schéma ou base

### 5. Créer les migrations (si nécessaire)

```bash
python manage.py makemigrations
python manage.py migrate
```

⚠️ **Note** : Les migrations ne créeront PAS la table externe (car `managed=False`), mais elles créeront les champs ForeignKey dans les tables qui y font référence.

## 📊 Tables SIG Actuellement Intégrées

### 1. `geo."admin-2"` - Pays (OpenStreetMap)

**Source** : Données OSM niveau administratif 2

**Modèle Django** : `geo.models.Admin2`

**Utilisation** : Sélection du pays d'intervention pour les projets

**Exemple de requête** :
```python
from geo.models import Admin2

# Récupérer le Sénégal
senegal = Admin2.objects.get(name="Sénégal")

# Tous les pays d'Afrique de l'Ouest
pays_afrique = Admin2.objects.filter(name__in=[
    "Sénégal", "Mali", "Mauritanie", "Gambie", "Guinée-Bissau"
])
```

### 2. `geo."cellules_grdr"` - Cellules GRDR

**Source** : Données internes GRDR (antennes, bureaux)

**Modèle Django** : `geo.models.CellulesGRDR`

**Utilisation** : Rattachement géographique des projets aux cellules GRDR

**Exemple de requête** :
```python
from geo.models import CellulesGRDR

# Toutes les cellules
cellules = CellulesGRDR.objects.all()

# Cellules avec géométrie
cellules_geo = CellulesGRDR.objects.exclude(geom__isnull=True)
```

## 🚨 Problèmes Courants et Solutions

### Erreur : "relation does not exist"

**Cause** : La table n'existe pas en base ou le nom est incorrect

**Solutions** :
1. Vérifier que la table existe : `\dt geo.*` dans psql
2. Vérifier l'orthographe du `db_table`
3. Utiliser les guillemets : `db_table = '"geo"."nom_table"'`

### Erreur : "syntax error near `-`"

**Cause** : Le nom de table contient un tiret (comme `admin-2`)

**Solution** : Utiliser les guillemets doubles dans `db_table`

```python
# ❌ Incorrect
db_table = 'geo.admin-2'

# ✅ Correct
db_table = '"geo"."admin-2"'
```

### Erreur lors de la migration : "constraint violation"

**Cause** : Django essaie de créer une contrainte FK vers une table `managed=False`

**Solution** : Ajouter `db_constraint=False` à la ForeignKey

```python
pays = models.ForeignKey(
    'geo.Admin2',
    on_delete=models.SET_NULL,
    db_constraint=False  # ← Ajouter ceci
)
```

## 🔄 Workflow de Mise à Jour des Données

### Option 1 : Import complet (reconstruction)

```bash
# 1. Supprimer l'ancienne table
psql -d jamm_leydi -c "DROP TABLE IF EXISTS geo.ma_table CASCADE;"

# 2. Réimporter les nouvelles données
ogr2ogr -f "PostgreSQL" \
  PG:"host=localhost dbname=jamm_leydi" \
  nouvelles_donnees.shp \
  -nln geo.ma_table

# 3. Recréer les index
psql -d jamm_leydi -c "CREATE INDEX idx_ma_table_geom ON geo.ma_table USING GIST(geom);"
```

### Option 2 : Mise à jour incrémentale

```sql
-- Insérer de nouvelles données
INSERT INTO geo.ma_table (nom, geom)
VALUES ('Nouvelle entrée', ST_GeomFromText('POINT(-12.34 14.56)', 4326));

-- Mettre à jour des données existantes
UPDATE geo.ma_table
SET nom = 'Nom corrigé'
WHERE id = 5;
```

## 📚 Bonnes Pratiques

1. **Documentation** : Toujours documenter la source des données (date, origine, projection)
2. **Projection** : Utiliser SRID 4326 (WGS84) pour cohérence avec le projet
3. **Index spatiaux** : Créer des index GIST sur les colonnes géométriques
4. **Sauvegarde** : Exporter régulièrement les tables SIG avec `pg_dump`
5. **Validation** : Vérifier la validité des géométries avec `ST_IsValid(geom)`

## 🔗 Ressources Utiles

- [PostGIS Documentation](https://postgis.net/documentation/)
- [GDAL/OGR Documentation](https://gdal.org/)
- [GeoDjango Tutorial](https://docs.djangoproject.com/en/stable/ref/contrib/gis/tutorial/)
- [OpenStreetMap Data Extracts](https://download.geofabrik.de/)

---

*Dernière mise à jour : 2025-11-25*
