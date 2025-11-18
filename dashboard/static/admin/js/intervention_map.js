/**
 * Personnalisation du widget OpenLayers pour les interventions
 * Améliore le comportement de la carte : drag-and-drop et centrage automatique
 */

(function() {
    'use strict';

    // Attendre que la page et OpenLayers soient chargés
    document.addEventListener('DOMContentLoaded', function() {
        // Petite pause pour laisser Django admin initialiser la carte
        setTimeout(function() {
            customizeInterventionMap();
        }, 500);
    });

    function customizeInterventionMap() {
        // Trouver le widget de carte (recherche par classe OpenLayers)
        const mapDiv = document.querySelector('.olMap');
        if (!mapDiv) {
            console.log('Widget de carte non trouvé');
            return;
        }

        // Récupérer l'instance OpenLayers map
        const mapId = mapDiv.id;
        if (!window[mapId]) {
            console.log('Instance de carte non trouvée');
            return;
        }

        const map = window[mapId];

        // 1. Désactiver le mode "click-and-follow" par défaut
        // Chercher le contrôle DrawFeature et le désactiver temporairement
        for (let i = 0; i < map.controls.length; i++) {
            const control = map.controls[i];
            if (control.CLASS_NAME === 'OpenLayers.Control.DrawFeature') {
                // Modifier le handler pour utiliser click simple au lieu de mousemove
                if (control.handler) {
                    control.handler.freehand = false;
                    control.handler.stopDown = true;
                }
            }
        }

        // 2. Si un point existe déjà, centrer la carte dessus
        const vectorLayer = map.getLayersByClass('OpenLayers.Layer.Vector')[0];
        if (vectorLayer && vectorLayer.features.length > 0) {
            const feature = vectorLayer.features[0];
            if (feature.geometry) {
                // Centrer la carte sur le point existant
                const bounds = feature.geometry.getBounds();
                map.setCenter(bounds.getCenterLonLat(), 12);

                // Ajouter une aide visuelle
                console.log('Carte centrée sur le point existant');
            }
        }

        // 3. Ajouter des instructions visuelles
        addMapInstructions(mapDiv);
    }

    function addMapInstructions(mapDiv) {
        // Vérifier si les instructions n'existent pas déjà
        if (document.querySelector('.map-instructions')) {
            return;
        }

        // Créer un panneau d'instructions
        const instructions = document.createElement('div');
        instructions.className = 'map-instructions';
        instructions.innerHTML = `
            <div style="background: #fff; padding: 10px; margin: 10px 0; border-left: 4px solid #417690;">
                <strong>Instructions :</strong>
                <ul style="margin: 5px 0 0 20px; font-size: 13px;">
                    <li>Cliquez une fois sur la carte pour placer le point</li>
                    <li>Pour modifier : cliquez sur le point et déplacez-le</li>
                    <li>Pour supprimer : sélectionnez le point et appuyez sur Suppr</li>
                </ul>
            </div>
        `;

        // Insérer avant la carte
        mapDiv.parentNode.insertBefore(instructions, mapDiv);
    }
})();
