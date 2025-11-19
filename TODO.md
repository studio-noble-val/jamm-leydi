# TODO - JAMM LEYDI

> Backlog priorisé du projet. Mis à jour après chaque session de travail.

## Légende
- `[ ]` À faire
- `[x]` Terminé
- `[~]` En cours
- **P0** = Urgent/Bloquant | **P1** = Important | **P2** = Nice-to-have

---

## En cours

*Aucune tâche en cours*

### Session 2025-11-18
- [x] **Mode Globe MapLibre** : Activation de la projection globe sur la carte SIG
- [x] **Méthodologie de travail** : Mise en place TODO.md, DEVLOG.md, protocole de clôture
- [x] **Sélecteur de fonds de carte** : OSM, Satellite ESRI, Google Satellite/Hybrid, Topo, Dark, Light
- [x] **Terrain 3D** : Relief avec ombrage et atmosphère (AWS Terrain Tiles)

---

## Backlog

### P0 - Urgent

*Aucune tâche urgente*

### P1 - Important

- [ ] **Intégration Sentinel/Copernicus** : Ajouter couches Sentinel-2 (RGB, NDVI, False Color)
- [ ] **Intégration KoboToolbox** : API REST pour import automatique des données terrain
- [ ] **Module webstories** : Pages de capitalisation pour communication
- [ ] **Export PDC** : Génération des Plans de Développement Communaux

### P2 - Nice-to-have

- [ ] **API REST** : Pour applications mobiles futures
- [ ] **Optimisation performance** : Cache pour graphiques dashboard
- [ ] **Tests automatisés** : Tests fonctionnels et géospatiaux

---

## Terminé

### Session 2025-11-18
- [x] **Mode Globe MapLibre** : Activation de la projection globe sur la carte SIG
  - Mise à jour MapLibre v4.1.2 → v5.0.0
  - Ajout `map.setProjection({ type: 'globe' })`

### Sessions précédentes
- [x] Architecture multi-projets avec isolation des données
- [x] Modèle géospatial complet (PostGIS)
- [x] Dashboard interactif avec cards cliquables
- [x] Formulaire de création d'interventions
- [x] Page détail par thématique
- [x] Interface publique responsive
- [x] Données démo V3 avec progressions variables

---

*Dernière mise à jour : 2025-11-18*
