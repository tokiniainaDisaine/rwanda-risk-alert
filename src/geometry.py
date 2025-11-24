"""Geometry Module for Rwanda

This module defines geographic boundaries and geometries for Rwanda used in the
climate risk alert system. It fetches district boundaries from FAO/GAUL and defines
polygons for Rwanda's geographic extent.

Constants:
    districts (ee.FeatureCollection): Rwanda district boundaries from FAO/GAUL 2015 level 2
    rwanda (ee.Geometry.Polygon): Bounding box polygon encompassing Rwanda
    rwanda_buffered (ee.Geometry): Rwanda bounding box with 10km buffer for edge effects
"""

from config import EE_PROJECT
import ee

# Initialize Google Earth Engine
import os
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
#     print(f\"Error initializing Earth Engine: {e}. Please ensure you are authenticated.")

# Fetch the district outline of Rwanda from FAO GAUL database
districts = ee.FeatureCollection("FAO/GAUL/2015/level2") \
            .filter(ee.Filter.eq("ADM0_NAME", "Rwanda"))

# Polygon englobing Rwanda (approximate bounding box)
# Coordinates: [longitude, latitude]
#   Southwest corner: 28.70°E, 2.85°S
#   Northeast corner: 31.00°E, 1.00°S
rwanda = ee.Geometry.Polygon([
    [
        [28.70, -2.85],  # Southwest corner
        [31.00, -2.85],  # Southeast corner
        [31.00, -1.00],  # Northeast corner
        [28.70, -1.00]   # Northwest corner
    ]
])

# Add a 10km buffer to Rwanda's polygon to capture border effects
rwanda_buffered = rwanda.buffer(10000)  # 10,000 meters = 10 km
