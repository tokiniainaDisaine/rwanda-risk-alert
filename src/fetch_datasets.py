# Imports and Pre-requisites
from config import EE_PROJECT

import os
from src.geometry import districts, rwanda, rwanda_buffered

import ee
email = "alu-summative-account@rwanda-climate-alerts.iam.gserviceaccount.com"
# path = os.getenv("EE_KEY_PATH")
path = "D:\\PC DISAINE\\toky\\ALU\\term_3\\keys\\rwanda-climate-alerts-c17300261abd.json"
credentials = ee.ServiceAccountCredentials(email, path)
ee.Initialize(credentials)

# try:
#     ee.Authenticate()
# except Exception as e:
#     print(f"Error authenticating Earth Engine: {e}. Please ensure you have Earth Engine access.")
#
# try:
#     ee.Initialize(project=EE_PROJECT)
# except Exception as e:
#     print(f"Error initializing Earth Engine: {e}. Please ensure you are authenticated.")

# Collect Datasets
def fetch_dataset(image_collection,
                  start_date="2005-01-01",
                  end_date="2025-10-31",
                  geometry=rwanda_buffered,
                  select=True, band=None):
    """
    Fetch and filter an Earth Engine Image Collection.
    
    Args:
        image_collection (str): Earth Engine image collection ID
        start_date (str): Start date in YYYY-MM-DD format (default: "2005-01-01")
        end_date (str): End date in YYYY-MM-DD format (default: "2025-10-31")
        geometry (ee.Geometry): Region of interest (default: rwanda_buffered)
        select (bool): Whether to select specific band(s) (default: True)
        band (str or list): Band name(s) to select if select=True (default: None)
    
    Returns:
        ee.ImageCollection: Filtered and clipped image collection
    """
    filtered_image_collection = ee.ImageCollection(image_collection) \
                                .filterDate(start_date, end_date) \
                                .filterBounds(geometry) \
                                .map(lambda img: img.clip(geometry))

    if select:
        filtered_image_collection = filtered_image_collection.select(band)

    return filtered_image_collection

def fetch_all():
    """
    Fetch all climate and terrain datasets for Rwanda.
    
    This function retrieves the following datasets:
    - CHIRPS: Daily rainfall (mm/day)
    - ERA5 Land: Monthly temperature (Kelvin)
    - ERA5 Land: Monthly soil moisture (volumetric)
    - MODIS: Vegetation health index (NDVI)
    - SRTM: Digital Elevation Model (meters)
    - Terrain: Slope (degrees)
    
    Returns:
        tuple: (chirps, era5_temp, soil_moist, ndvi, dem, slope)
            - chirps (ee.ImageCollection): Daily rainfall data
            - era5_temp (ee.ImageCollection): Monthly temperature data  
            - soil_moist (ee.ImageCollection): Monthly soil moisture data
            - ndvi (ee.ImageCollection): Monthly NDVI data
            - dem (ee.Image): Digital elevation model
            - slope (ee.Image): Terrain slope
    """
    # CHIRPS Daily Rainfall (mm/day)
    chirps = fetch_dataset("UCSB-CHG/CHIRPS/DAILY",
                           select=False)

    # ERA5 Land Monthly Temperature
    era5_temp = fetch_dataset("ECMWF/ERA5_LAND/MONTHLY_AGGR",
                              select=True,
                              band="temperature_2m")

    # Soil Moisture (ERA5 Land)
    soil_moist = fetch_dataset("ECMWF/ERA5_LAND/MONTHLY_AGGR",
                               select=True,
                               band="volumetric_soil_water_layer_1")

    # MODIS NDVI (monthly, 250 m)
    ndvi = fetch_dataset("MODIS/061/MOD13A1",
                         select=True,
                         band="NDVI")

    # DEM (SRTM ~30m resolution)
    dem = ee.Image("USGS/SRTMGL1_003").clip(rwanda_buffered)

    # Calculate slope (degrees)
    slope = ee.Terrain.slope(dem)

    return chirps, era5_temp, soil_moist, ndvi, dem, slope
