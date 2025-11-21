// Initialize map
const map = L.map('map').setView([-1.94, 30.06], 8);

// Add OpenStreetMap base layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Store active layers
const activeLayers = {};

// Function to update map layers based on checkbox selection
function updateMapLayers() {
    const checkboxes = document.querySelectorAll('#layer-checklist input[type="checkbox"]');
    const selectedLayers = [];
    
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
        // Remove all existing layers
        Object.values(activeLayers).forEach(layer => {
            map.removeLayer(layer);
        });
        
        // Clear active layers object
        for (let key in activeLayers) {
            delete activeLayers[key];
        }
        
        // Add new layers in the order they were returned
        data.layers.forEach(layerInfo => {
            const tileLayer = L.tileLayer(layerInfo.url, {
                opacity: 0.8
            });
            tileLayer.addTo(map);
            activeLayers[layerInfo.name] = tileLayer;
        });
    })
    .catch(error => {
        console.error('Error fetching layers:', error);
    });
}

// Function to update plot
function updatePlot() {
    const district = document.getElementById('district-dropdown').value;
    const dataset = document.getElementById('dataset-dropdown').value;
    
    // Show loading state
    const plotImg = document.getElementById('risk-plot');
    plotImg.alt = 'Loading plot...';
    
    // Fetch plot from Flask API
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

// Function to update monthly data
function updateMonthly() {
    const info_district = document.getElementById('district-dropdown-info').value;
    const chirps = document.getElementById('chirps');
    const temp = document.getElementById('temp');
    const soil_moist = document.getElementById('soil_moist');
    const ndvi = document.getElementById('ndvi');

    // Fetch plot from Flask API
    fetch(`/api/info?info_district=${encodeURIComponent(info_district)}`)
    .then(response => response.json())
    .then(data => {
        chirps.textContent = `${data.chirps} mm`;
        temp.textContent = `${data.era5_temp} °C`;
        soil_moist.textContent = `${data.soil_moist} %`;
        ndvi.textContent = `${data.ndvi}`;
    })
    .catch(error => {
        console.error('Error fetching the mean:', error);
    });
}

// Event listeners
document.querySelectorAll('#layer-checklist input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', updateMapLayers);
});

document.getElementById('district-dropdown').addEventListener('change', updatePlot);
document.getElementById('dataset-dropdown').addEventListener('change', updatePlot);

document.getElementById('district-dropdown-info').addEventListener('change', updateMonthly);

// Initial load
updateMapLayers();
updatePlot();

updateMonthly();
