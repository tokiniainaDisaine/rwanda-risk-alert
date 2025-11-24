"""Plotting and Data Visualization Module

This module provides functions for creating time series plots of climate data and 
converting Earth Engine data to pandas DataFrames for visualization. It handles plotting
for rainfall, temperature, soil moisture, and vegetation health indices.

Global Variables:
    dataset_dict (dict): Configuration for each dataset including visualization parameters

Functions:
    get_time_series: Extract time series data from Earth Engine for a specific district
    ee_array_to_df: Convert Earth Engine array to pandas DataFrame
    t_kelvin_to_celsius: Convert temperature from Kelvin to Celsius
    get_dataset_info: Get plotting parameters for a dataset
    plot_dataset_test: Plot dataset on a matplotlib axis
    get_daily_average: Calculate daily averages from time series data
"""

from config import EE_PROJECT

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
# except Exception as e:\n#     print(f\"Error authenticating Earth Engine: {e}. Please ensure you have Earth Engine access.\")
#
# try:
#     ee.Initialize(project=EE_PROJECT)
# except Exception as e:
#     print(f\"Error initializing Earth Engine: {e}. Please ensure you are authenticated.\")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from src.fetch_datasets import fetch_all

chirps, era5_temp, soil_moist, ndvi, dem, slope = fetch_all()

# Dataset configuration dictionary with visualization parameters
dataset_dict = {
    "chirps": {
        "dataset": chirps,
        "list of bands": ["precipitation"],
        "title": "Precipitation in ",
        "xlabel": "Date",
        "ylabel": "Precipitation [mm]",
        "ylim_min": -0,
        "ylim_max": 100
    },
    "era5_temp": {
        "dataset": era5_temp,
        "list of bands": ["temperature_2m"],
        "title": "Temperature in ",
        "xlabel": "Date",
        "ylabel": "Temperature [C]",
        "ylim_min": 10,
        "ylim_max": 30
    },
    "soil_moist": {
        "dataset": soil_moist,
        "list of bands": ["volumetric_soil_water_layer_1"],
        "title": "Soil moisture in ",
        "xlabel": "Date",
        "ylabel": "Moisture [?]",
        "ylim_min": -0,
        "ylim_max": 1
    },
    "ndvi": {
        "dataset": ndvi,
        "list of bands": ["NDVI"],
        "title": "NDVI in ",
        "xlabel": "Date",
        "ylabel": "NDVI [?]",
        "ylim_min": -0,
        "ylim_max": 10000
    }
}

# Fetch Time series
def get_time_series(image_collection, district_name, start_date, end_date, scale=1000):
    """
    Extract time series data from an Earth Engine ImageCollection for a specific district.
    
    Args:
        image_collection (ee.ImageCollection): Earth Engine image collection to query
        district_name (str): Name of the district (must match FAO/GAUL database)
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        scale (int): Resolution in meters for data extraction (default: 1000m)
    
    Returns:
        list: Time series data as a list of dictionaries from Earth Engine
    """
    district = ee.FeatureCollection("FAO/GAUL/2015/level2") \
                    .filter(ee.Filter.eq("ADM0_NAME", "Rwanda")) \
                    .filter(ee.Filter.eq("ADM2_NAME", district_name)) \
                    .geometry()

    district_time_series = image_collection \
                            .filterDate(start_date, end_date) \
                            .getRegion(district, scale=scale) \
                            .getInfo()

    return district_time_series


# Convert to pandas DataFrame
def ee_array_to_df(arr, list_of_bands):
    """
    Transform client-side Earth Engine Image.getRegion array to pandas DataFrame.
    
    Args:
        arr (list): Array returned from ee.Image.getRegion()
        list_of_bands (list): List of band names to include in the DataFrame
    
    Returns:
        pd.DataFrame: DataFrame with columns: time, datetime, and specified bands
    """
    df = pd.DataFrame(arr)

    # Rearrange the header.
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)

    # Remove rows without data inside.
    df = df[['longitude', 'latitude', 'time', *list_of_bands]].dropna()

    # Convert the data to numeric values.
    for band in list_of_bands:
        df[band] = pd.to_numeric(df[band], errors='coerce')

    # Convert the time field into a datetime.
    df['datetime'] = pd.to_datetime(df['time'], unit='ms')

    # Keep the columns of interest.
    df = df[['time','datetime',  *list_of_bands]]

    return df


def t_kelvin_to_celsius(t_kelvin):
    """
    Convert temperature from Kelvin to degrees Celsius.
    
    Args:
        t_kelvin (float): Temperature in Kelvin
    
    Returns:
        float: Temperature in Celsius
    """
    t_celsius =  t_kelvin - 273.15
    return t_celsius


def get_dataset_info(district, dataset_name, dataset_info):
    """
    Get plotting parameters for a specific dataset.
    
    Args:
        district (str): Name of the district
        dataset_name (str): Name of the dataset ('chirps', 'era5_temp', 'soil_moist', 'ndvi')
        dataset_info (dict): Dataset configuration dictionary
    
    Returns:
        dict: Plotting parameters including title, labels, and axis limits
    """
    dataset = dataset_info[dataset_name]

    plot_params = {
        "district": district,
        "list_of_bands": dataset["list of bands"],
        "title": dataset["title"] + district,
        "xlabel": dataset["xlabel"],
        "ylabel": dataset["ylabel"],
        "ylim_min": dataset["ylim_min"],
        "ylim_max": dataset["ylim_max"]
    }

    return plot_params


def plot_dataset_test(dataframe, dataset_name, ax, dataset_parameters=None):
    """
    Plot dataset on a matplotlib axis.
    
    Handles two modes:
    - With dataset_parameters: Plot raw data points with formatting
    - Without dataset_parameters: Plot aggregated means as overlay
    
    Args:
        dataframe (pd.DataFrame): Data to plot
        dataset_name (str): Name of the dataset for special handling
        ax (matplotlib.axes.Axes): Matplotlib axis to plot on
        dataset_parameters (dict, optional): Plotting parameters. If None, plots as overlay
    """
    # Convert temperature from Kelvin to Celsius if needed
    if dataset_name == "era5_temp":
        if dataset_parameters:
            dataframe["temperature_2m"] = dataframe["temperature_2m"].apply(t_kelvin_to_celsius)
        else:
            dataframe["agg"] = dataframe["agg"].apply(t_kelvin_to_celsius)

    if dataset_parameters:
        # Plot raw data with comprehensive formatting
        district = f"{dataset_parameters["district"]} (trend)"
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # e.g., "Jun 2025"
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        ax.set_title(dataset_parameters["title"], fontsize=16)
        ax.set_xlabel(dataset_parameters["xlabel"], fontsize=14)
        ax.set_ylabel(dataset_parameters["ylabel"], fontsize=14)
        ax.set_ylim(dataset_parameters["ylim_min"], dataset_parameters["ylim_max"])
        ax.grid(lw=0.5, ls='--', alpha=0.7)

        ax.scatter(dataframe["datetime"], dataframe[dataset_parameters["list_of_bands"]],
                   color='gray', linewidth=1, alpha=0.1, label=district)
    else:
        # Plot aggregated mean as overlay
        x = dataframe["datetime"]
        y = dataframe["agg"]
        ax.scatter(x, y, s=100, color='red', linewidth=1, alpha=0.5, label="Mean")
        ax.plot(x, y, color='gray', linestyle='--', linewidth=1, label='Graph')

    ax.legend(fontsize=14, loc='upper right')


def get_daily_average(dataframe, dataset_info):
    """
    Calculate daily averages from time series data.
    
    Args:
        dataframe (pd.DataFrame): Time series data with 'datetime' column
        dataset_info (dict): Dataset configuration containing band names
    
    Returns:
        pd.DataFrame: Aggregated data with columns: datetime, agg (mean value)
    """
    dataframe = dataframe.drop("time", axis=1)
    df_combined = dataframe.groupby("datetime").agg(
        agg = (dataset_info["list of bands"][0], "mean"),
    ).reset_index()
    return df_combined
