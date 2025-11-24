"""Risk Index Calculation and Map Layer Generation Module

This module calculates disaster risk indices for floods, droughts, and landslides
across Rwanda using multiple climate and terrain datasets. It normalizes input data
and combines them using weighted formulas to generate risk maps.

Risk Indices:
    - Flood Risk: Based on rainfall, temperature, and slope
    - Drought Risk: Based on rainfall deficit, soil moisture deficit, and temperature
    - Landslide Risk: Based on rainfall, soil moisture, and slope

Global Variables:
    map_layers_dict (dict): Dictionary mapping layer names to Earth Engine objects

Functions:
    aggregate_monthly: Aggregate image collection by month
    calculate_baseline: Calculate baseline and anomalies for a dataset
    normalize: Normalize image values to 0-1 range
    aggregate_risk: Aggregate risk indices by district
    calculate_indexes: Calculate all three risk indices
    get_image_url: Get Google Earth Engine tile URL for a layer
"""

from config import EE_PROJECT

# Initialize Google Earth Engine
import os
import ee
email = "alu-summative-account@rwanda-climate-alerts.iam.gserviceaccount.com"
path = os.getenv("EE_KEY_PATH")
credentials = ee.ServiceAccountCredentials(email, path)
ee.Initialize(credentials)

# Alternative authentication (commented out)
# try:
#     ee.Authenticate()
# except Exception as e:
#     print(f\"Error authenticating Earth Engine: {e}. Please ensure you have Earth Engine access.\")
#
# try:
#     ee.Initialize(project=EE_PROJECT)
# except Exception as e:
#     print(f\"Error initializing Earth Engine: {e}. Please ensure you are authenticated.\")

from src.geometry import districts
from src.fetch_datasets import fetch_all

chirps, era5_temp, soil_moist, ndvi, dem, slope = fetch_all()

def aggregate_monthly(image_collection):
    """
    Aggregate an image collection by month.
    
    Args:
        image_collection (ee.ImageCollection): Image collection to aggregate
    
    Returns:
        tuple: (monthly_result, monthly_sum)
            - monthly_result (ee.ImageCollection): Collection with month property added
            - monthly_sum (ee.Image): Sum of all images in collection
    """
    monthly_result = image_collection.map(lambda img: img.set("month", img.date().format("YYYY-MM")))
    monthly_sum = monthly_result.reduce(ee.Reducer.sum())
    return monthly_result, monthly_sum


def calculate_baseline(image_collection):
    """
    Calculate baseline statistics and anomalies for a climate dataset.
    
    Compares recent period (2025) against a historical baseline (2005-2015)
    to identify climate anomalies.
    
    Args:
        image_collection (ee.ImageCollection): Climate dataset to analyze
    
    Returns:
        tuple: (baseline, baseline_mean, anomaly)
            - baseline (ee.ImageCollection): Historical period data (2005-2015)
            - baseline_mean (ee.Image): Mean of historical period
            - anomaly (ee.Image): Relative anomaly (recent-baseline)/baseline
    """
    # Define baseline period (2005–2015)
    baseline = image_collection.filterDate("2005-01-01", "2015-12-31")

    # Mean rainfall baseline
    baseline_mean = baseline.mean()

    # Recent period (2025)
    recent = image_collection.filterDate("2025-01-01", "2025-10-31").mean()

    # Rainfall anomaly (recent vs baseline) - relative change
    anomaly = recent.subtract(baseline_mean).divide(baseline_mean)

    return baseline, baseline_mean, anomaly


def normalize(img, region):
    """
    Normalize image values to 0-1 range based on min/max values in the region.
    
    Args:
        img (ee.Image): Image to normalize
        region (ee.Geometry): Region to compute min/max statistics
    
    Returns:
        ee.Image: Normalized image with values in range [0, 1]
    """
    min_dict = img.reduceRegion(
        reducer=ee.Reducer.min(),
        geometry=region,
        scale=1000,
        maxPixels=1e13,
        bestEffort=True
    ).values().get(0)
    max_dict = img.reduceRegion(
        reducer=ee.Reducer.max(),
        geometry=region,
        scale=1000,
        maxPixels=1e13,
        bestEffort=True
    ).values().get(0)

    min_value = ee.Number(min_dict)
    max_value = ee.Number(max_dict)

    return img.subtract(min_value).divide(max_value.subtract(min_value))


def aggregate_risk(risk_index):
    """
    Aggregate risk index values by district.
    
    Args:
        risk_index (ee.Image): Risk index image
    
    Returns:
        ee.FeatureCollection: District-level statistics with mean risk values
    """
    district_stats = risk_index.reduceRegions(
        collection=districts,
        reducer=ee.Reducer.mean(),
        scale=1000
    )
    return district_stats


def calculate_indexes():
    """
    Calculate flood, drought, and landslide risk indices for Rwanda.
    
    Risk formulas:
    - Flood Risk = 0.4*rain + 0.3*temp + 0.2*slope
    - Drought Risk = 0.4*(1-rain) + 0.3*(1-soil_moist) + 0.3*temp
    - Landslide Risk = 0.4*rain + 0.3*soil_moist + 0.3*slope
    
    All inputs are normalized anomalies (0-1 range) before combination.
    
    Returns:
        tuple: (flood_risk_index, drought_risk_index, landslide_risk_index)
            Each is an ee.Image with risk values in range [0, 1]
    
    Note:
        NDVI is currently commented out due to data issues being resolved
    """
    # Calculate baselines and anomalies
    rain_baseline, rain_baseline_mean, rain_anomaly = calculate_baseline(chirps)
    temp_baseline, temp_baseline_mean, temp_anomaly = calculate_baseline(era5_temp)
    soil_moist_baseline, soil_moist_baseline_mean, soil_moist_anomaly = calculate_baseline(soil_moist)
    # ndvi_baseline, ndvi_baseline_mean, ndvi_anomaly = calculate_baseline(ndvi)

    # Normalize all inputs to 0-1 range
    rain_norm = normalize(rain_anomaly, districts)
    temp_norm = normalize(temp_anomaly, districts)
    soil_moist_norm = normalize(soil_moist_anomaly, districts)
    # ndvi_norm = normalize(ndvi_anomaly, districts)

    # dem_norm = normalize(dem, districts)
    slope_norm = normalize(slope, districts)

    # Calculate Flood Risk Index
    # Higher rainfall + higher temperature + steeper slopes = higher flood risk
    flood_risk_index = rain_norm.multiply(0.4) \
                        .add(temp_norm.multiply(0.3)) \
                        .add(slope_norm.multiply(0.2))
                        # .add(ndvi_norm.multiply(0.2)) \

    # Calculate Drought Risk Index
    # Lower rainfall + lower soil moisture + higher temperature = higher drought risk
    drought_risk_index = rain_norm.multiply(-1).add(1).multiply(0.4) \
                        .add(soil_moist_norm.multiply(-1).add(1).multiply(0.3)) \
                        .add(temp_norm.multiply(0.3))
                        # .add(ndvi_norm.multiply(-1).add(1).multiply(0.2)) \
    # NDVI is causing some trouble, still in the process of figuring it out

    # Calculate Landslide Risk Index
    # Higher rainfall + higher soil moisture + steeper slopes = higher landslide risk
    landslide_risk_index = rain_norm.multiply(0.4) \
                            .add(soil_moist_norm.multiply(0.3)) \
                            .add(slope_norm.multiply(0.3))

    return flood_risk_index, drought_risk_index, landslide_risk_index

# Calculate risk indices
flood_risk, drought_risk, landslide_risk = calculate_indexes()

# Map layers dictionary for frontend access
map_layers_dict = {
    "districts": districts,
    "flood": flood_risk,
    "drought": drought_risk,
    "landslide": landslide_risk,
}

def get_image_url(selected_layer):
    """
    Get Google Earth Engine tile URL for a map layer.
    
    Generates visualization parameters and returns the tile URL template
    for rendering layers in Leaflet.
    
    Args:
        selected_layer (str): Layer name - 'districts', 'flood', 'drought', or 'landslide'
    
    Returns:
        str: Google Earth Engine tile URL template for the layer
    
    Visualization:
        - Districts: Black outlines
        - Risk layers: Green (low risk) to Yellow to Red (high risk) gradient
    """
    dataset = map_layers_dict[selected_layer]
    if selected_layer == "districts":
        # Render district boundaries as black outlines
        fc = dataset
        # vis = {"color": "black"}
        vis = {"palette": ["black"]}
        image = ee.Image().paint(fc, 0, 1)
        map_id = ee.data.getMapId({"image": image.visualize(**vis)})
        tile_url = map_id["tile_fetcher"].url_format

    else:
        # Render risk layers with green-yellow-red gradient
        vis_params = {"min": 0, "max": 1, "palette": ["green", "yellow", "red"]}
        map_id_dict = ee.data.getMapId({'image': dataset.visualize(**vis_params)})
        tile_url = map_id_dict['tile_fetcher'].url_format

    return tile_url
