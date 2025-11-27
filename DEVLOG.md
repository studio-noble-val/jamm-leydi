# DEVLOG - JAMM LEYDI

> Journal de développement chronologique. Utilisé pour le reporting client et le suivi des itérations.

---

## 📅 2025-11-26 (Session 2) : Interface SIG Gaming Style Anno 1800 🎮

### 🎯 Objectifs
1. ✅ Refondre complètement l'interface cartographique avec un style gaming
2. ✅ Implémenter une barre d'outils top style Anno 1800
3. ✅ Ajouter drag & drop pour les panneaux
4. ✅ Créer des indicateurs KPI visuels (R1/R2/R3)
5. ✅ Appliquer la charte graphique GRDR avec cohérence

### ✨ Réalisations

#### 1. Barre d'Outils Gaming (Top Toolbar)
**Fichier modifié** : `dashboard/templates/dashboard/carte_sig.html`

**Architecture de la toolbar** :
- **Section gauche** : Bouton retour (rouge) + séparateur + 3 boutons toggle (orange)
- **Section centre** : Titre du projet centré absolument avec transform
- **Section droite** : 3 indicateurs KPI en mini donuts

**Style gaming** :
- Fond sombre semi-transparent `rgba(26, 31, 46, 0.92)`
- Bordure orange GRDR `rgba(232, 109, 44, 0.3)`
- Glassmorphism avec `backdrop-filter: blur(12px)`
- Ombres multiples pour profondeur

**Boutons interactifs** :
- Hover : élévation + intensification couleur
- Active : gradient orange plein + scale icon
- Transitions fluides `cubic-bezier(0.4, 0, 0.2, 1)`

#### 2. Indicateurs KPI Mini Donuts (R1/R2/R3)
**Technologie** : SVG circle avec `stroke-dasharray` et `stroke-dashoffset`

**Design** :
- R1 (75%) : Vert `#2ecc71`
- R2 (50%) : Orange `#f39c12`
- R3 (40%) : Rouge `#e74c3c`

**Structure** :
```html
<svg width="36" height="36">
    <circle class="bg" r="14" stroke="rgba(255,255,255,0.1)"></circle>
    <circle class="progress" r="14" stroke-dashoffset="calculé"></circle>
</svg>
```

**Calcul dynamique** : `offset = circumference - (percentage / 100 * circumference)`

#### 3. Panneaux Latéraux avec Drag & Drop
**3 panneaux disponibles** :
- Fond de carte (7 options + relief 3D)
- Géocommun (placeholder pour future session)
- Données projet (communes, interventions, infrastructures, acteurs)

**Système de drag** :
- Drag depuis le header (cursor: move)
- Contraintes fenêtre : `maxX`, `maxY`, `minY = 70px`
- Z-index dynamique (999 pendant drag)
- Classe `.dragging` désactive transitions

**Code JavaScript** (~70 lignes) :
```javascript
header.addEventListener('mousedown', (e) => {
    draggedPanel = panel;
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;
});

document.addEventListener('mousemove', (e) => {
    const constrainedX = Math.max(0, Math.min(x, maxX));
    const constrainedY = Math.max(70, Math.min(y, maxY));
    draggedPanel.style.left = constrainedX + 'px';
});
```

#### 4. Icône X de Fermeture des Panneaux
**Style** :
- Bouton rouge 24x24px aligné avec le titre
- Background `rgba(231, 76, 60, 0.15)`
- Font Awesome icon `.fa-times`
- Hover : scale 1.1 + intensification

**Fonction** :
```javascript
function closePanel(panelName, event) {
    event.stopPropagation(); // Évite le drag
    panel.classList.add('hidden');
    toggleBtn.classList.remove('active');
}
```

#### 5. Polish Final
**Ajustements UX** :
- ✅ Titre centré absolument (left: 50%, transform: translateX(-50%))
- ✅ Contrôles MapLibre natifs conservés (top: 90px)
- ✅ Suppression glows extérieurs pour style sobre
- ✅ Icône X alignée avec header du panneau

### 📁 Fichiers Modifiés
- `dashboard/templates/dashboard/carte_sig.html` : Refonte complète UI (~1280 lignes)

### 🎨 Charte Graphique Appliquée
- Orange GRDR : `#E86D2C`
- Teal GRDR : `#2A8B8B`
- Rouge actions : `#e74c3c`
- Police : Quicksand (400, 500, 600, 700)

### 📊 Métriques
- **Lignes CSS** : ~550 lignes de styles gaming
- **JavaScript** : ~120 lignes (panel management + drag & drop)
- **Fonctionnalités** : 8 interactions UX (toggle, drag, close, hover, etc.)

### 🚀 Prochaines Étapes
1. **P1** : Retravailler l'UI des indicateurs KPI (actuellement mini donuts basiques)
2. Intégration Sentinel/Copernicus (couches satellitaires)
3. Module Géocommun (données partagées)
4. KoboToolbox API (import données terrain)

---

## 📅 2025-11-26 (Session 1) : Sélection Géographique Multi-Niveaux en Cascade (FINALE)

### 🎯 Objectifs
1. ✅ Finaliser l'interface de sélection géographique en cascade
2. ✅ Implémenter les 4 endpoints API REST pour filtrage spatial
3. ✅ Créer le JavaScript de gestion des selects dynamiques
4. ✅ Corriger le nom de table CellulesGRDR
5. ✅ Nettoyer le formulaire de création de projet

### ✨ Réalisations

#### 1. API REST Géographique avec Filtrage Spatial PostGIS
**Fichier créé** : `accueil/api_views.py`

**4 endpoints implémentés** :
- `GET /api/geo/regions/?pays_ids=1,2,3` → Régions intersectant les pays sélectionnés
- `GET /api/geo/departements/?region_ids=...` → Départements par régions
- `GET /api/geo/arrondissements/?departement_ids=...` → Arrondissements par départements
- `GET /api/geo/communes/?arrondissement_ids=...` → Communes par arrondissements

**Technologie** : Requêtes spatiales PostGIS (`geom__intersects`)

**Résultat** : Filtrage dynamique basé sur les géométries réelles

#### 2. Interface Utilisateur en Cascade (~200 lignes JS)
**Template modifié** : `accueil/templates/accueil/creer_projet.html`

**Fonctionnalités JavaScript** :
- 5 selects multiples (pays → régions → départements → arrondissements → communes)
- Chargement AJAX via `fetch()` API
- Réinitialisation en cascade lors des changements
- Génération d'inputs cachés avant soumission du formulaire

**UX** :
- Désactivation progressive des niveaux non sélectionnés
- Messages contextuels ("Sélectionnez d'abord...")
- Gestion des erreurs de chargement

#### 3. Vue POST Handler Complète
**Fichier modifié** : `accueil/views.py`

**Changements** :
- Suppression des références aux anciens champs `pays` (ForeignKey) et `zone_intervention` (TextField)
- Récupération des IDs via `request.POST.getlist('zone_*')`
- Utilisation de `.set()` pour les relations ManyToMany
- Gestion gracieuse de la table CellulesGRDR (try/except avec `list()` pour forcer l'évaluation)

**Résultat** : Création de projet avec zones multi-niveaux opérationnelle

#### 4. Fix Critique : Nom de Table CellulesGRDR
**Problème découvert** : Table nommée `geo."cellules-grdr"` (avec trait d'union) mais modèle Django pointait vers `geo.cellules_grdr`

**Solution** :
- Modèle : `db_table = '"geo"."cellules-grdr"'` (guillemets requis)
- Migration 0004 : Correction du `AlterModelTable`

**Test** : 2 cellules accessibles (Bakel, Dakar) ✅

#### 5. Nettoyage Formulaire
**Suppressions** :
- ❌ Champ "Pays d'intervention" (simple select → redondant avec multi-niveaux)
- ❌ Champ "Zone d'intervention" (texte libre → remplacé par sélection structurée)

**Conservation** :
- ✅ Cellule GRDR (affichée conditionnellement si données disponibles)

**Résultat** : Interface épurée et focalisée

### 📊 Migrations Appliquées
1. **0008_add_zone_multi_levels.py** : Ajout 5 champs ManyToMany
2. **0009_migrate_zone_data.py** : Migration données pays → zone_pays
3. **0010_cleanup_old_fields.py** : Suppression anciens champs

**Bilan** : 0 perte de données, 3/3 projets migrés avec succès

### 📦 Fichiers Modifiés
- `core/models.py` : Modèle Projet (5 M2M, propriété `zone_intervention_description`)
- `geo/models.py` : Admin4, Admin5, Admin7, Admin8, CellulesGRDR (fix db_table)
- `geo/migrations/0004_*.py` : Correction table cellules-grdr
- `accueil/views.py` : POST handler zones M2M, GET avec try/except cellules
- `accueil/api_views.py` : **NOUVEAU** - 4 endpoints REST
- `accueil/urls.py` : Routes API géographique
- `accueil/templates/accueil/creer_projet.html` : Interface cascade + JavaScript

### 🐛 Problèmes Résolus
1. ✅ TemplateSyntaxError (bloc non fermé) → Ajout `{% endblock %}`
2. ✅ Table `geo.cellules_grdr` introuvable → Correction nom avec trait d'union
3. ✅ QuerySet lazy evaluation → Forcer avec `list()` dans try/except
4. ✅ TypeError unexpected kwargs → Suppression `pays` et `zone_intervention` du create()

### 🎯 Prochaines Étapes
- Tests end-to-end de création de projet avec sélection géographique complète
- Affichage de la zone d'intervention dans les vues de détail projet
- Possibilité d'éditer les zones d'un projet existant

### 📝 Notes Techniques
**Pattern PostgreSQL pour tables avec caractères spéciaux** :
- Sans caractères spéciaux : `db_table = 'schema.table'`
- Avec trait d'union/espaces : `db_table = '"schema"."table-name"'`

**Pattern Lazy QuerySet + Exception Handling** :
```python
try:
    # Forcer évaluation immédiate
    data = list(Model.objects.all())
except Exception:
    data = []
```

---

## 📅 2025-11-25 : Intégration SIG Multi-Niveaux & Auto-génération Code Projet

### 🎯 Objectifs
1. ✅ Intégrer les tables SIG OpenStreetMap (Admin2, Admin4, Admin5, Admin7, Admin8)
2. ✅ Auto-génération du code projet (PROJ-{id})
3. ✅ Remplacer le champ pays (CharField) par une ForeignKey vers Admin2
4. 🚧 Implémenter la sélection géographique multi-niveaux en cascade

### ✨ Réalisations

#### 1. Auto-génération Code Projet
**Problème** : Code projet saisi manuellement, risque de doublons
**Solution** : Génération automatique au format `PROJ-{id}` via méthode `save()`

**Impact** : Formulaire simplifié, unicité garantie

#### 2. Intégration Tables SIG Externes
**Nouveaux modèles** (tous avec `managed=False`) :
- `Admin2` : Pays (geo."admin-2")
- `Admin4` : Régions (geo."admin-4")
- `Admin5` : Départements (geo."admin-5")
- `Admin7` : Arrondissements (geo."admin-7")
- `Admin8` : Communes (geo."admin-8")
- `CellulesGRDR` : Antennes GRDR (geo.cellules_grdr)

**Points clés** :
- Utilisation de `db_table = '"geo"."admin-X"'` (guillemets obligatoires)
- `db_constraint=False` sur les ForeignKeys
- Admin Django en lecture seule

#### 3. Migration Progressive Sans Perte de Données
**Challenge** : 3 projets existants avec `pays = "Sénégal"` (VARCHAR)
**Solution** : Migration en 3 étapes sans perte de données

**Résultat** : 3/3 projets préservés (100%)

#### 4. Architecture Zone d'Intervention Multi-Niveaux
**Nouveau modèle** : 5 champs Many-to-Many dans `Projet` pour sélection flexible par niveau géographique

**Avantages** :
- Sélection flexible (arrêt à n'importe quel niveau)
- Multi-sélection (plusieurs communes, départements, etc.)
- Propriété `zone_intervention_description` pour affichage textuel

#### 5. API Géographique en Cascade
**4 endpoints créés** avec filtrage spatial PostGIS (`ST_Intersects()`) :
- `/api/geo/regions/?pays_ids=1,2`
- `/api/geo/departements/?region_ids=...`
- `/api/geo/arrondissements/?departement_ids=...`
- `/api/geo/communes/?arrondissement_ids=...`

#### 6. Documentation Complète
- [docs/INTEGRATION_SIG.md](docs/INTEGRATION_SIG.md) : Guide complet (15 sections)
- [CLAUDE.md](CLAUDE.md) : Architecture SIG documentée

### 📁 Fichiers Modifiés

**Modèles** : core/models.py, geo/models.py (+6 modèles)
**Vues & API** : accueil/views.py, accueil/api_views.py (NOUVEAU), accueil/urls.py
**Templates** : accueil/templates/accueil/creer_projet.html
**Admin** : geo/admin.py
**Migrations** : 4 migrations progressives
**Docs** : docs/INTEGRATION_SIG.md (NOUVEAU), CLAUDE.md, TODO.md

### 🚧 Prochaines Étapes (P0)

1. **Template JavaScript** : Interface sélection en cascade
2. **Vue creer_projet** : Logique sauvegarde Many-to-Many
3. **Migrations** : Application finale et tests
4. **Tests Fonctionnels** : Validation parcours complet

### 📊 Statistiques

- **Modèles créés** : 6
- **Champs Projet** : 5 Many-to-Many
- **Endpoints API** : 4
- **Migrations** : 4
- **Code** : ~400 lignes
- **Documentation** : ~500 lignes
- **Projets préservés** : 3/3 (100%)

---

## 2025-11-20 - Charte graphique GRDR 2025

### Objectifs
- Appliquer la nouvelle charte graphique GRDR 2025 à toute l'application
- Uniformiser les couleurs (orange #E86D2C, teal #2A8B8B, ocre #C6893C)
- Intégrer le nouveau logo GRDR 2025
- Adopter les polices Quicksand (sans-serif) et Caveat (calligraphique)

### Réalisations

**Page de connexion (landing.html)**
- Nouveau design avec logo GRDR 2025 (200px)
- Hiérarchie : "Système d'Information Géographique" (Caveat, teal) + "GeoGrdr" (Quicksand, subtitle)
- Simplification responsive : suppression des media queries complexes, tailles fixes pour desktop
- Gradient orange pour le bouton de connexion

**Page sélection projets (/projets/)**
- Application charte GRDR : navbar avec logo, couleurs teal/orange
- Cards projets avec headers en gradient teal
- Avatar utilisateur avec gradient orange/ocre
- Boutons primaires avec gradient orange

**Dashboard (/dashboard/)**
- Sidebar avec gradient sombre (1a2332 → 0f1621)
- Navbar avec logo GRDR et projet title en teal
- KPI cards avec bordures teal et hover effet orange
- Headers de cards en gradient teal
- Boutons et progress bars en orange
- Badges colorés selon la charte

**Refactoring CSS**
- Extraction du CSS inline vers fichiers statiques :
  - `static/css/landing.css` (nouvelle création)
  - `static/css/projets.css` (nouvelle création)
  - `static/css/dashboard.css` (nouvelle création)
- Nettoyage des templates : suppression des blocks `<style>` dans landing.html, home.html
- Variables CSS `:root` pour les couleurs GRDR dans chaque fichier

### Fichiers modifiés

**Nouveaux fichiers**
- `static/logo-grdr-2025.jpg`
- `static/css/landing.css`
- `static/css/projets.css`
- `static/css/dashboard.css`

**Templates modifiés**
- `accueil/templates/accueil/landing.html` : ajout fonts + lien CSS, suppression inline CSS
- `accueil/templates/accueil/base_projets.html` : ajout logo + fonts + lien CSS
- `accueil/templates/accueil/liste_projets.html` : suppression inline CSS
- `accueil/templates/accueil/creer_projet.html` : mise à jour titre
- `dashboard/templates/dashboard/base.html` : ajout logo + fonts + lien CSS
- `dashboard/templates/dashboard/home.html` : suppression inline CSS (lignes 272-357)

### Cohérence visuelle obtenue
- ✅ Logo GRDR 2025 sur toutes les pages (landing, projets, dashboard)
- ✅ Couleurs uniformisées : orange (CTA), teal (titres, headers), ocre (accents)
- ✅ Polices cohérentes : Quicksand (corps), Caveat (titres calligraphiques)
- ✅ Gradients appliqués : boutons, headers, avatars
- ✅ Effets hover harmonisés : translateY(-2px), box-shadow, transform
- ✅ CSS organisé : séparation des préoccupations (3 fichiers thématiques)

### Prochaines étapes
- **Interface carto** : Appliquer la charte GRDR à `carte_sig.html`
- **Panneaux rétractables** : Ajouter toggles pour réduire/fermer les panels de la carte
- **Refactoring CSS carte** : Extraire le CSS inline vers `static/css/carte.css`
- **Intégration Sentinel/Copernicus** : Ajouter couches satellite (RGB, NDVI, False Color)
- **Intégration KoboToolbox** : API REST pour import données terrain

---

## 2025-11-18 - Globe 3D et fonds de carte multiples

### Objectifs
- Afficher la carte en mode globe 3D
- Ajouter plusieurs fonds de carte
- Intégrer le relief 3D avec ombrage

### Réalisations

**Mode Globe**
- Mise à jour MapLibre GL JS v4.1.2 → v5.0.0
- Activation projection globe avec `map.setProjection({ type: 'globe' })`

**Fonds de carte (7 options)**
- OpenStreetMap (standard)
- Satellite ESRI
- Google Satellite (haute résolution)
- Google Hybrid (satellite + labels)
- OpenTopoMap (topographique)
- CartoDB Dark Matter (sombre)
- CartoDB Positron (clair)

**Terrain 3D**
- Relief avec exagération 1.5x (AWS Terrain Tiles)
- Ombrage hillshade pour les ombres portées
- Couche atmosphérique (sky) pour rendu réaliste
- Toggle on/off pour activer/désactiver

### Fichiers modifiés
- `dashboard/templates/dashboard/carte_sig.html`
  - CSS : styles basemap-selector (lignes 370-407)
  - HTML : panneau sélecteur de fonds (lignes 463-506)
  - JS : basemaps object et terrain toggle (lignes 873-1008)

### Méthodologie mise en place
- Création de `TODO.md` pour le backlog priorisé
- Création de `DEVLOG.md` pour le reporting client
- Renommage `.claudemd` → `CLAUDE.md`
- Ajout du protocole de clôture de session

### Prochaines étapes
- Intégration Sentinel/Copernicus (nécessite compte Sentinel Hub)
- Note : tuiles Google en "zone grise" - considérer alternatives pour production

---

## 2025-11-12 - Dashboard avec jauges et données démo V3

### Objectifs
- Dashboard réaliste avec progressions variables par thématique

### Réalisations
- Script `demo_data_v3.py` avec 82 interventions
- Progressions différenciées : R1 (75%), R2 (50%), R3 (40%)
- Jauges visuelles sur le dashboard

### Fichiers modifiés
- `demo_data_v3.py`
- Templates dashboard

---

## Sessions antérieures

*Historique condensé des travaux précédents*

- **Architecture V2** : Refonte multi-projets, fusion Activité/Réalisation
- **GeoDjango** : Intégration PostGIS, modèles géolocalisés
- **Dashboard** : Interface glassmorphism, cards cliquables, graphiques Chart.js
- **Carte SIG** : Interface MapLibre avec couches interactives

---

*Format d'entrée :*
```markdown
## YYYY-MM-DD - Titre de session

### Objectifs
- Ce qui était prévu

### Réalisations
- Ce qui a été fait

### Fichiers modifiés
- Liste des fichiers

### Prochaines étapes
- Ce qui reste à faire
```
