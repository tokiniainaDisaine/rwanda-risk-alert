/**
 * Rwanda Climate Alerts - Frontend JavaScript
 * 
 * This script handles all client-side interactions for the Rwanda Climate Alerts dashboard.
 * It manages map initialization, layer toggling, plot updates, and monthly statistics retrieval.
 * 
 * Features:
 * - Interactive Leaflet map with risk layer overlays
 * - Dynamic time series plot generation
 * - Real-time monthly climate statistics
 * - Responsive UI updates based on user selections
 * 
 * Dependencies:
 * - Leaflet.js for interactive maps
 * - Bootstrap for UI components
 * 
 * @author Rwanda Climate Alerts Team
 * @version 1.0.0
 */

// ============================================================================
// Map Initialization
// ============================================================================

/**
 * Initialize Leaflet map centered on Rwanda
 * Coordinates: -1.94°N, 30.06°E (approximately Kigali)
 * Zoom level: 8 (country-wide view)
 */
const map = L.map('map').setView([-1.94, 30.06], 8);

/**
 * Add OpenStreetMap as the base tile layer
 */
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

/**
 * Storage for active map layers (risk overlays)
 * @type {Object.<string, L.TileLayer>}
 */
const activeLayers = {};

// ============================================================================
// Map Layer Management
// ============================================================================

/**
 * Update map layers based on checkbox selections.
 * 
 * This function:
 * 1. Reads checkbox states to determine selected layers
 * 2. Fetches tile URLs from the Flask API
 * 3. Removes old layers from the map
 * 4. Adds new layers in the correct order (bottom to top)
 * 
 * Layer ordering: landslide → drought → flood → districts
 */
function updateMapLayers() {
    const checkboxes = document.querySelectorAll('#layer-checklist input[type=\"checkbox\"]');
    const selectedLayers = [];
    
    // Collect selected layer names
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            selectedLayers.push(checkbox.value);
        }
    });
    
    // Fetch layer URLs from Flask API
    fetch('/api/layers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ layers: selectedLayers })
    })
    .then(response => response.json())
    .then(data => {
        // Remove all existing layers from map
        Object.values(activeLayers).forEach(layer => {
            map.removeLayer(layer);
        });
        
        // Clear active layers object
        for (let key in activeLayers) {
            delete activeLayers[key];
        }
        
        // Add new layers in the order returned by API
        data.layers.forEach(layerInfo => {
            const tileLayer = L.tileLayer(layerInfo.url, {
                opacity: 0.8  // Semi-transparent overlays
            });
            tileLayer.addTo(map);
            activeLayers[layerInfo.name] = tileLayer;
        });
    })
    .catch(error => {
        console.error('Error fetching layers:', error);
    });
}

// ============================================================================
// Time Series Plot Updates
// ============================================================================

/**
 * Update the time series plot based on selected district and dataset.
 * 
 * This function:
 * 1. Retrieves selected district and dataset from dropdowns
 * 2. Fetches plot image from Flask API
 * 3. Updates the plot image element with base64-encoded PNG
 * 
 * The plot shows both raw data points and daily averages for the selected
 * climate variable over the period Oct 2024 - Oct 2025.
 */
function updatePlot() {
    const district = document.getElementById('district-dropdown').value;
    const dataset = document.getElementById('dataset-dropdown').value;
    
    // Show loading state
    const plotImg = document.getElementById('risk-plot');
    plotImg.alt = 'Loading plot...';
    
    // Fetch plot from Flask API (returns base64-encoded image)
    fetch(`/api/plot?district=${encodeURIComponent(district)}&dataset=${encodeURIComponent(dataset)}`)
    .then(response => response.json())
    .then(data => {
        plotImg.src = data.image;
        plotImg.alt = `${dataset} plot for ${district}`;
    })
    .catch(error => {
        console.error('Error fetching plot:', error);
        plotImg.alt = 'Error loading plot';
    });
}

// ============================================================================
// Monthly Statistics Updates
// ============================================================================

/**
 * Update monthly climate statistics for the selected district.
 * 
 * This function:
 * 1. Retrieves selected district from dropdown
 * 2. Fetches mean values for October 2025 from Flask API
 * 3. Updates the info cards with:
 *    - Mean precipitation (mm)
 *    - Mean temperature (°C)
 *    - Mean soil moisture (%)
 *    - Mean NDVI (vegetation health index)
 */
function updateMonthly() {
    const info_district = document.getElementById('district-dropdown-info').value;
    const chirps = document.getElementById('chirps');
    const temp = document.getElementById('temp');
    const soil_moist = document.getElementById('soil_moist');
    const ndvi = document.getElementById('ndvi');

    // Fetch monthly averages from Flask API
    fetch(`/api/info?info_district=${encodeURIComponent(info_district)}`)
    .then(response => response.json())
    .then(data => {
        // Update info card values with units
        chirps.textContent = `${data.chirps} mm`;
        temp.textContent = `${data.era5_temp} °C`;
        soil_moist.textContent = `${data.soil_moist} %`;
        ndvi.textContent = `${data.ndvi}`;
    })
    .catch(error => {
        console.error('Error fetching the mean:', error);
    });
}

// ============================================================================
// Event Listeners
// ============================================================================

/**
 * Attach event listeners to layer checkboxes
 * Triggers map layer updates when any checkbox state changes
 */
document.querySelectorAll('#layer-checklist input[type=\"checkbox\"]').forEach(checkbox => {
    checkbox.addEventListener('change', updateMapLayers);
});

/**
 * Attach event listeners to plot control dropdowns
 * Triggers plot updates when district or dataset selection changes
 */
document.getElementById('district-dropdown').addEventListener('change', updatePlot);
document.getElementById('dataset-dropdown').addEventListener('change', updatePlot);

/**
 * Attach event listener to monthly info district dropdown
 * Triggers statistics update when district selection changes
 */
document.getElementById('district-dropdown-info').addEventListener('change', updateMonthly);

// ============================================================================
// Initial Page Load
// ============================================================================

/**
 * Initialize the dashboard on page load:
 * 1. Load default map layers (districts only)
 * 2. Generate initial plot (first district, CHIRPS dataset)
 * 3. Load monthly statistics (first district)
 */
updateMapLayers();
updatePlot();
updateMonthly();
