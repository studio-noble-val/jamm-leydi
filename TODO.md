# TODO - JAMM LEYDI

> Backlog priorisé du projet. Mis à jour après chaque session de travail.

## Légende
- `[ ]` À faire
- `[x]` Terminé
- `[~]` En cours
- **P0** = Urgent/Bloquant | **P1** = Important | **P2** = Nice-to-have

---

## En cours

*Aucune tâche en cours actuellement*

---

## Backlog

### P0 - Urgent

*Aucune tâche urgente*

### P1 - Important

- [ ] **Interface carto - UI Indicateurs KPI** : Retravailler l'UI des indicateurs R1/R2/R3 (actuellement supprimés de la toolbar)
- [ ] **Intégration KoboToolbox** : API REST pour import automatique des données terrain (Carnet Numérique de Terrain)
- [ ] **Module webstories** : Pages de capitalisation pour communication
- [ ] **Export PDC** : Génération des Plans de Développement Communaux

### P2 - Nice-to-have

- [ ] **API REST** : Pour applications mobiles futures
- [ ] **Optimisation performance** : Cache pour graphiques dashboard
- [ ] **Tests automatisés** : Tests fonctionnels et géospatiaux

---

## Terminé

### Session 2025-11-26 (Partie 2) - Interface SIG Gaming Style (COMPLÈTE ✅)
- [x] **Refonte UI complète** : Style gaming Anno 1800 avec barre d'outils top
- [x] **Barre d'outils gaming** : Header 70px avec fond sombre, bordures orange, sections gauche/centre/droite
- [x] **Bouton retour** : Intégré dans toolbar avec style rouge distinct + séparateur vertical
- [x] **3 boutons toggle** : Fond de carte, Géocommun, Données projet (orange GRDR)
- [x] **Titre projet centré** : Bloc teal au centre absolu de l'écran
- [x] **3 indicateurs KPI** : Mini donuts SVG pour R1 (75%), R2 (50%), R3 (40%)
- [x] **Panneaux latéraux gaming** : Fond sombre semi-transparent, bordures orange, glassmorphism
- [x] **Drag & Drop panneaux** : Déplacement fluide par le header avec contraintes fenêtre
- [x] **Icône X fermeture** : Bouton rouge en haut à droite des headers aligné avec le titre
- [x] **Suppression glows** : Retrait effets luminescents extérieurs pour style plus sobre
- [x] **Contrôles MapLibre** : Positionnés à 90px du haut, style natif conservé
- [x] **Charte GRDR** : Orange #E86D2C, Teal #2A8B8B, police Quicksand

### Session 2025-11-26 (Partie 1) - Sélection géographique multi-niveaux (COMPLÈTE ✅)
- [x] **Modèles SIG** : Création Admin4 (Régions), Admin5 (Départements), Admin7 (Arrondissements), Admin8 (Communes)
- [x] **Modèle Projet** : Ajout 5 champs Many-to-Many (zone_pays, zone_regions, zone_departements, zone_arrondissements, zone_communes)
- [x] **Migrations progressives** : 3 migrations (0008 ajout M2M, 0009 migration données, 0010 nettoyage anciens champs)
- [x] **API géographique** : 4 endpoints REST avec filtrage spatial PostGIS (ST_Intersects)
- [x] **Interface utilisateur** : Template avec 5 selects en cascade + JavaScript (~200 lignes)
- [x] **Vue POST handler** : Gestion complète des zones ManyToMany
- [x] **Nettoyage formulaire** : Suppression champs redondants (pays ForeignKey, zone_intervention TextField)
- [x] **Fix table CellulesGRDR** : Correction db_table avec guillemets pour trait d'union
- [x] **Tests fonctionnels** : Validation accès table cellules-grdr (2 cellules : Bakel, Dakar)

### Session 2025-11-25 (Partie 1) - Intégration SIG & Auto-génération code projet
- [x] **Code projet auto-généré** : Format PROJ-{id} via méthode save()
- [x] **Modèles SIG Admin2 et CellulesGRDR** : Intégration tables externes avec managed=False
- [x] **Migration progressive** : Conversion pays CharField → ForeignKey Admin2 sans perte de données
- [x] **Formulaire création projet** : Suppression champ code_projet, ajout sélecteurs pays/cellule GRDR
- [x] **Documentation SIG** : Guide complet d'intégration (docs/INTEGRATION_SIG.md)
- [x] **Mise à jour CLAUDE.md** : Documentation architecture SIG et bonnes pratiques

### Session 2025-11-20 - Charte graphique GRDR
- [x] **Page de connexion (landing.html)** : Nouveau design avec logo GRDR 2025, polices Quicksand/Caveat, couleurs orange/teal/ocre
- [x] **Page sélection projets (/projets/)** : Application charte GRDR, navbar avec logo, avatar gradient, cards stylisées
- [x] **Dashboard (/dashboard/)** : Application charte GRDR, sidebar gradient sombre, boutons orange, KPI cards, headers teal
- [x] **Extraction CSS** : Création de `landing.css`, `projets.css`, `dashboard.css` pour remplacer CSS inline
- [x] **Nettoyage templates** : Suppression CSS dupliqué dans `home.html`
- [x] **Cohérence visuelle** : Uniformisation couleurs, polices, effets hover sur toute l'application

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

*Dernière mise à jour : 2025-11-26 (Session 2)*
