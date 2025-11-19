# DEVLOG - JAMM LEYDI

> Journal de développement chronologique. Utilisé pour le reporting client et le suivi des itérations.

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
