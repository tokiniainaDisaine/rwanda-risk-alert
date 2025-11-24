"""Configuration Module for Rwanda Climate Alerts

This module contains configuration settings for Google Earth Engine authentication
and project identification.

Attributes:
    EE_PROJECT (str): Google Earth Engine project ID, can be overridden using the 
                      EE_PROJECT environment variable. Default: 'rwanda-climate-alerts'
"""

import os

# Earth Engine project id (can be overridden with EE_PROJECT env var)
EE_PROJECT = os.environ.get("EE_PROJECT", "rwanda-climate-alerts")