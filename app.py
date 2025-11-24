"""Rwanda Climate Alerts - Flask Web Application

This Flask application provides a web-based dashboard for visualizing climate and disaster risk data
for Rwanda. It integrates with Google Earth Engine to fetch and analyze environmental datasets.

Features:
    - Interactive map displaying flood, drought, and landslide risk layers
    - Time series plots for rainfall, temperature, soil moisture, and vegetation health (NDVI)
    - Monthly statistics for selected districts
    - District-level data visualization

API Endpoints:
    - GET /: Main dashboard page
    - GET /api/plot: Generate time series plots for selected district and dataset
    - GET /api/info: Get monthly statistics for a selected district
    - POST /api/layers: Get map layer tile URLs based on selected layers

Dependencies:
    - Flask: Web framework
    - Google Earth Engine: Satellite data access
    - Matplotlib: Plot generation
    - Pandas: Data manipulation
    - Leaflet (frontend): Interactive maps
"""

import matplotlib
matplotlib.use('agg')  # Use non-interactive backend for server-side plotting
import numpy as np
import io, base64

from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt

from config import EE_PROJECT
from src.risk_map import get_image_url
from src.plot import *
from src.fetch_datasets import fetch_all

# Initialize Google Earth Engine
import os
import ee
email = "alu-summative-account@rwanda-climate-alerts.iam.gserviceaccount.com"
# path = os.getenv("EE_KEY_PATH")
path = "D:\\PC DISAINE\\toky\\ALU\\term_3\\keys\\rwanda-climate-alerts-c17300261abd.json"
credentials = ee.ServiceAccountCredentials(email, path)
ee.Initialize(credentials)

# Alternative authentication (commented out)
# try:
#     ee.Authenticate()
# except Exception as e:
#     print(f"Error authenticating Earth Engine: {e}. Please ensure you have Earth Engine access.")
#
# try:
#     ee.Initialize(project=EE_PROJECT)
# except Exception as e:
#     print(f"Error initializing Earth Engine: {e}. Please ensure you are authenticated.")


# ---- Load data ----
district_df = pd.read_csv("data/district_boundaries/csv/District_Boundaries.csv")
district_list = np.sort(district_df["district"].unique())
chirps, era5_temp, soil_moist, ndvi, dem, slope = fetch_all()
dataset_list = tuple(dataset_dict.keys())

# ---- Create Flask app ----
app = Flask(__name__)

@app.route('/')
def index():
    """
    Render the main dashboard page.
    
    Returns:
        HTML: Rendered index.html template with district list
    """
    return render_template('index.html', districts=district_list)


@app.route('/api/plot')
def get_plot():
    """
    API endpoint to generate and return time series plot as base64-encoded image.
    
    This endpoint generates a time series plot for a selected district and dataset,
    showing both raw data points and daily averages for the period from Oct 2024 to Oct 2025.
    
    Query Parameters:
        district (str): Name of the district (default: first district in alphabetical order)
        dataset (str): Dataset type - 'chirps', 'era5_temp', 'soil_moist', or 'ndvi' (default: 'chirps')
    
    Returns:
        JSON: Dictionary containing:
            - image (str): Base64-encoded PNG image with data URI prefix
    
    Example:
        GET /api/plot?district=Kigali&dataset=chirps
    """
    selected_district = request.args.get('district', district_list[0])
    selected_dataset = request.args.get('dataset', 'chirps')
    
    # Generate time series data
    district_time_series = get_time_series(
                            dataset_dict[selected_dataset]["dataset"],
                            selected_district,
                            "2024-10-01",
                            "2025-10-31",
                            1000)

    df = ee_array_to_df(district_time_series, dataset_dict[selected_dataset]["list of bands"])
    daily_average_df = get_daily_average(df, dataset_dict[selected_dataset])

    # Plot with matplotlib
    fig, ax = plt.subplots(figsize=(14, 6))
    dataset_info = get_dataset_info(selected_district, selected_dataset, dataset_dict)

    plot_dataset_test(df, selected_dataset, ax, dataset_info)
    plot_dataset_test(daily_average_df, selected_dataset, ax)

    plt.tight_layout()

    # Convert to base64 for display
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    
    return jsonify({
        'image': "data:image/png;base64," + encoded
    })


@app.route('/api/info')
def get_info():
    """
    API endpoint to calculate monthly average climate statistics for a selected district.
    
    This endpoint computes mean values for multiple climate variables over October 2025
    for the specified district. All data is fetched from Google Earth Engine.
    
    Query Parameters:
        info_district (str): Name of the district (default: first district in alphabetical order)
    
    Returns:
        JSON: Dictionary containing monthly averages:
            - chirps (float): Mean precipitation in mm (rounded to 2 decimal places)
            - era5_temp (float): Mean temperature in Celsius (rounded to 2 decimal places)
            - soil_moist (float): Mean volumetric soil moisture as percentage (rounded to 2 decimal places)
            - ndvi (float): Mean Normalized Difference Vegetation Index (rounded to 2 decimal places)
    
    Example:
        GET /api/info?info_district=Kigali
    """
    selected_district = request.args.get('info_district', district_list[0])

    # Generate time series data for CHIRPS (rainfall)
    chirps_time_series = get_time_series(
                            dataset_dict["chirps"]["dataset"],
                            selected_district,
                            "2025-10-01",
                            "2025-10-31")
    chirps_df = ee_array_to_df(chirps_time_series, dataset_dict["chirps"]["list of bands"])
    raw_mean_chirps = chirps_df["precipitation"].mean()
    mean_chirps = np.round(raw_mean_chirps, 2)

    # Generate time series data for ERA5 temperature
    era5_temp_time_series = get_time_series(
                            dataset_dict["era5_temp"]["dataset"],
                            selected_district,
                            "2025-10-01",
                            "2025-10-31")
    era5_temp_df = ee_array_to_df(era5_temp_time_series, dataset_dict["era5_temp"]["list of bands"])
    era5_temp_df["temperature_2m"] = era5_temp_df["temperature_2m"].apply(t_kelvin_to_celsius)
    raw_mean_era5_temp = era5_temp_df["temperature_2m"].mean()
    mean_era5_temp = np.round(raw_mean_era5_temp, 2)

    # Generate time series data for soil moisture
    soil_moist_time_series = get_time_series(
                            dataset_dict["soil_moist"]["dataset"],
                            selected_district,
                            "2025-10-01",
                            "2025-10-31")
    soil_moist_df = ee_array_to_df(soil_moist_time_series, dataset_dict["soil_moist"]["list of bands"])
    raw_mean_soil_moist = soil_moist_df["volumetric_soil_water_layer_1"].mean() * 100
    mean_soil_moist = np.round(raw_mean_soil_moist, 2)

    # Generate time series data for NDVI
    ndvi_time_series = get_time_series(
                            dataset_dict["ndvi"]["dataset"],
                            selected_district,
                            "2025-10-01",
                            "2025-10-31")
    ndvi_df = ee_array_to_df(ndvi_time_series, dataset_dict["ndvi"]["list of bands"])
    raw_mean_ndvi = ndvi_df["NDVI"].mean() * 0.0001
    mean_ndvi = np.round(raw_mean_ndvi, 2)

    info_result = {
        "chirps": mean_chirps,
        "era5_temp": mean_era5_temp,
        "soil_moist": mean_soil_moist,
        "ndvi": mean_ndvi,
    }

    return jsonify(info_result)


@app.route('/api/layers', methods=['POST'])
def get_layers():
    """
    API endpoint to get map layer tile URLs based on selected layers.
    
    This endpoint returns Google Earth Engine tile URLs for the requested map layers.
    Layers are ordered from bottom to top for proper stacking on the map.
    
    Request Body (JSON):
        layers (list): List of layer names to display. Options:
            - 'districts': District boundaries (black outlines)
            - 'flood': Flood risk index (green=low to red=high gradient)
            - 'drought': Drought risk index (green=low to red=high gradient)
            - 'landslide': Landslide risk index (green=low to red=high gradient)
    
    Returns:
        JSON: Dictionary containing:
            - layers (list): Ordered list (bottom to top) of layer objects, each with:
                - name (str): Layer identifier
                - url (str): Google Earth Engine tile URL template
    
    Example:
        POST /api/layers
        Body: {"layers": ["flood", "districts"]}
    """
    data = request.get_json()
    selected_layers = data.get('layers', ['districts'])
    
    # Define layer order (bottom to top)
    order = ["landslide", "drought", "flood", "districts"]
    
    layers = []
    for layer_name in order:
        if layer_name in selected_layers:
            tile_url = get_image_url(layer_name)
            layers.append({
                'name': layer_name,
                'url': tile_url
            })
    
    return jsonify({'layers': layers})

# --------------------------- For Testing Locally ---------------------------
# if __name__ == "__main__":
#     app.run(debug=True)