import matplotlib
matplotlib.use('agg')
import numpy as np
import io, base64

from flask import Flask, render_template, request, jsonify
# import pandas as pd
# import matplotlib.pyplot as plt
#
# from config import EE_PROJECT
from src.risk_map import get_image_url
from src.plot import *
from src.fetch_datasets import fetch_all

import ee
try:
    ee.Authenticate()
except Exception as e:
    print(f"Error authenticating Earth Engine: {e}. Please ensure you have Earth Engine access.")

try:
    ee.Initialize(project=EE_PROJECT)
except Exception as e:
    print(f"Error initializing Earth Engine: {e}. Please ensure you are authenticated.")


# ---- Load data ----
district_df = pd.read_csv("data/district_boundaries/csv/District_Boundaries.csv")
district_list = np.sort(district_df["district"].unique())
chirps, era5_temp, soil_moist, ndvi, dem, slope = fetch_all()
dataset_list = tuple(dataset_dict.keys())

# ---- Create Flask app ----
app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', districts=district_list)


@app.route('/api/plot')
def get_plot():
    """API endpoint to generate and return plot as base64 image"""
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
    API endpoint to generate and return plot as base64 image
    -----------------Feel free to use for loop if things start to get annoying-------------------------
    """
    selected_district = request.args.get('district', district_list[0])

    # Generate time series data
    chirps_time_series = get_time_series(
                            dataset_dict["chirps"]["dataset"],
                            selected_district,
                            "2025-10-01",
                            "2025-10-31")
    chirps_df = ee_array_to_df(chirps_time_series, dataset_dict["chirps"]["list of bands"])

    era5_temp_time_series = get_time_series(
                            dataset_dict["era5_temp"]["dataset"],
                            selected_district,
                            "2025-10-01",
                            "2025-10-31")
    era5_temp_df = ee_array_to_df(era5_temp_time_series, dataset_dict["era5_temp"]["list of bands"])
    era5_temp_df["temperature_2m"] = era5_temp_df["temperature_2m"].apply(t_kelvin_to_celsius)

    soil_moist_time_series = get_time_series(
                            dataset_dict["soil_moist"]["dataset"],
                            selected_district,
                            "2025-10-01",
                            "2025-10-31")
    soil_moist_df = ee_array_to_df(soil_moist_time_series, dataset_dict["soil_moist"]["list of bands"])

    ndvi_time_series = get_time_series(
                            dataset_dict["ndvi"]["dataset"],
                            selected_district,
                            "2025-10-01",
                            "2025-10-31")
    ndvi_df = ee_array_to_df(ndvi_time_series, dataset_dict["ndvi"]["list of bands"])

    info_result = {
        "chirps": chirps_df.to_dict(orient="records"),
        "era5_temp": era5_temp_df.to_dict(orient="records"),
        "soil_moist": soil_moist_df.to_dict(orient="records"),
        "ndvi": ndvi_df.to_dict(orient="records"),
    }

    return jsonify(info_result)


@app.route('/api/layers', methods=['POST'])
def get_layers():
    """API endpoint to get map layer tile URLs"""
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


if __name__ == "__main__":
    app.run(debug=True)