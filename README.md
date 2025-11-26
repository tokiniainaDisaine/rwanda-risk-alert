# Rwanda Risk Alert

Interactive Flask-based web application for visualizing climate risk indices (flood, drought, landslide) for Rwanda using Google Earth Engine datasets and real-time climate data.

[Demo video](https://youtu.be/MunDz9aqjms)

[Check out the website ;)](https://athena-holdings.tech)

## Features
- Interactive map (Leaflet) with selectable risk layers and district boundaries
- Time-series plots for districts (precipitation, temperature, soil moisture, vegetation health (NDVI))
- Monthly climate data dashboard with real-time statistics

## Repository structure (important files)
- `app.py` — Flask application entrypoint and API routes
- `src/` — application modules
  - `fetch_datasets.py` — Earth Engine dataset loaders
  - `geometry.py` — EE geometries and district FeatureCollection
  - `risk_map.py` — build risk index layers & export tile URLs
  - `plot.py` — generate time-series plots
- `templates/` — HTML templates for Flask
- `static/` — CSS and JavaScript files
- `data/` — local datasets (CSV/shapefile exports)

## Requirements
- Python 3.13.2+ (development tested python 3.13.2 and higher)
- Earth Engine account or key
- Packages (install with pip):
  - flask
  - pandas, numpy, matplotlib
  - earthengine-api
  - (optionally) geemap for local testing/visualization

Install quickly:
```bash
python -m pip install -r requirements.txt
```

## Running the app locally

### 1. Clone the repo:
```bash
git clone https://github.com/tokiniainaDisaine/rwanda-risk-alert.git
cd rwanda-risk-alert
```

### 2. Setup a virtual environment:
Create the virtual environment.
```bash
python -m venv /path/to/your/venv
```
Activate it:
```bash
source /path/to/your/venv/bin/activate
```

### 3. Install the dependencies:
```bash
python -m pip install -r requirements.txt
```

### 4. Authenticate the Google Earth Engine API:
There are two possible ways to authenticate Earth Engine:

* A. Through a service account key:

    Add your json key path as an environment variable
    ```bash
    export EE_KEY_PATH='/path/to/your/key.json'
    ```

* B. From repository root (if you have a Google Earth Engine account) :
    ```bash
    earthengine authenticate
    ```
    Follow the printed URL and paste the token when prompted.

### 5. Run the app:

Uncomment the last 2 lines of app.py:
```python
if __name__ == "__main__":
    app.run()
```

Then run: 

```bash
python app.py
```
Finally, follow the link from the output:
  
e.g. 
```
http://127.0.0.1:5000
```

## Google Earth Engine setup
1. Install Earth Engine API if not installed:
   ```bash
   python -m pip install earthengine-api
   ```
2. Authenticate (command-line recommended):
      ```bash
      earthengine authenticate
      ```
      Follow the printed URL and paste the token when prompted.

3. In code the project is initialized as:
   ```python
   ee.Initialize(project="rwanda-climate-alerts")
   # or if you have a service account key
   ee.Initialize(credentials)
   ```
   Ensure your account has access to that project or change to your own EE project (replace project="rwanda-climate-alerts" by project="[your-earth-engine-project]").

For more details, please refer to the Earth Engine documentation:
-  [Earth Engine access](https://developers.google.com/earth-engine/guides/access)
-  [Authentication and Initialization](https://developers.google.com/earth-engine/guides/auth)

Note: Earth Engine objects live in the cloud. Local shapefiles must be uploaded as EE assets (or converted to CSV/GeoJSON and accessed locally) — `.getInfo()` only works on EE objects already in the cloud.

## Data Sources
- [Earth Engine Datasets](https://earthengine.google.com/)
- [District/Sectors CSV](https://geospatial-open-data-site-nisrgis.hub.arcgis.com/datasets/b4bcf921d2854ef6a39e94185abf11bc_0/explore?location=-2.064849%2C29.917646%2C8.32)
- [Model Evaluation and Validation](https://www.gfdrr.org/sites/default/files/publication/National_Risk_Atlas_of_Rwanda_electronic_version_0.pdf)

## API and Resource Attribution

This application relies on several APIs, datasets, and open-source technologies. We gratefully acknowledge the following:

### Data Providers and APIs

#### Google Earth Engine
- **Provider**: [Google Earth Engine](https://earthengine.google.com/)
- **Usage**: Primary platform for satellite imagery and geospatial datasets
- **License**: [Earth Engine Terms of Service](https://earthengine.google.com/terms/)
- **Citation**: Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., & Moore, R. (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*.

#### CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data)
- **Provider**: [University of California, Santa Barbara (UCSB)](https://www.chc.ucsb.edu/data/chirps)
- **Dataset**: `UCSB-CHG/CHIRPS/DAILY`
- **Usage**: Daily rainfall data (mm/day)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Citation**: Funk, C., Peterson, P., Landsfeld, M. et al. (2015). The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes. *Scientific Data*, 2, 150066.

#### ERA5-Land (ECMWF Reanalysis v5)
- **Provider**: [European Centre for Medium-Range Weather Forecasts (ECMWF)](https://www.ecmwf.int/)
- **Dataset**: `ECMWF/ERA5_LAND/MONTHLY_AGGR`
- **Usage**: Monthly temperature (2m) and soil moisture data
- **License**: [Copernicus License](https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf)
- **Citation**: Muñoz Sabater, J. (2019). ERA5-Land monthly averaged data from 1950 to present. *Copernicus Climate Change Service (C3S) Climate Data Store (CDS)*.

#### MODIS NDVI (Moderate Resolution Imaging Spectroradiometer)
- **Provider**: [NASA](https://modis.gsfc.nasa.gov/)
- **Dataset**: `MODIS/061/MOD13A1`
- **Usage**: Normalized Difference Vegetation Index (NDVI) for vegetation health monitoring
- **License**: [NASA Earth Science Data and Information Policy](https://science.nasa.gov/earth-science/earth-science-data/data-information-policy)
- **Citation**: Didan, K. (2021). MODIS/Terra Vegetation Indices 16-Day L3 Global 500m SIN Grid V061. NASA EOSDIS Land Processes DAAC.

#### SRTM Digital Elevation Model
- **Provider**: [USGS](https://www.usgs.gov/)
- **Dataset**: `USGS/SRTMGL1_003`
- **Usage**: Elevation data (~30m resolution) for terrain analysis and slope calculations
- **License**: Public Domain
- **Citation**: NASA JPL (2013). NASA Shuttle Radar Topography Mission Global 1 arc second. NASA EOSDIS Land Processes DAAC.

### Frontend Libraries and Mapping

#### Leaflet
- **Provider**: [Leaflet](https://leafletjs.com/)
- **Version**: 1.9.4
- **Usage**: Interactive map rendering and layer management
- **License**: BSD 2-Clause License
- **Copyright**: © 2010-2023 Vladimir Agafonkin, © 2010-2011 CloudMade

#### OpenStreetMap
- **Provider**: [OpenStreetMap Contributors](https://www.openstreetmap.org/)
- **Usage**: Base map tiles
- **License**: [Open Data Commons Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/)
- **Attribution**: © OpenStreetMap contributors

#### Bootstrap
- **Provider**: [Bootstrap](https://getbootstrap.com/)
- **Version**: 5.3.0
- **Usage**: CSS framework for responsive UI components
- **License**: MIT License
- **Copyright**: © 2011-2023 The Bootstrap Authors

### Backend Technologies

#### Flask
- **Provider**: [Pallets Projects](https://palletsprojects.com/p/flask/)
- **Usage**: Web framework for API endpoints and server-side rendering
- **License**: BSD 3-Clause License

#### Matplotlib
- **Provider**: [Matplotlib Development Team](https://matplotlib.org/)
- **Usage**: Time-series plot generation
- **License**: [Matplotlib License (PSF-based)](https://matplotlib.org/stable/users/project/license.html)

#### Pandas
- **Provider**: [Pandas Development Team](https://pandas.pydata.org/)
- **Usage**: Data manipulation and time-series processing
- **License**: BSD 3-Clause License

#### NumPy
- **Provider**: [NumPy Developers](https://numpy.org/)
- **Usage**: Numerical computations
- **License**: BSD 3-Clause License

### District Boundary Data
- **Provider**: [Rwanda National Institute of Statistics (NISR) GIS](https://geospatial-open-data-site-nisrgis.hub.arcgis.com/)
- **Dataset**: District Boundaries CSV
- **License**: Open Data

### Risk Assessment Framework
- **Reference**: [National Risk Atlas of Rwanda](https://www.gfdrr.org/sites/default/files/publication/National_Risk_Atlas_of_Rwanda_electronic_version_0.pdf)
- **Provider**: Global Facility for Disaster Reduction and Recovery (GFDRR) & Government of Rwanda
- **Usage**: Model validation and risk assessment methodology

### Initial Personal Project

- **Provider**: [Inital Prototype](https://github.com/TheRealToky/rwanda-climate-alerts)
- **Usage**: The proprietary base code that was used for this project

---

**Disclaimer**: This application is for educational and informational purposes only. While we strive for accuracy, users should verify critical information with official sources before making decisions based on this data.


## Styling (CSS)
Flask serves static files from the `static/` folder. Customize the UI by editing `static/custom.css`. Example snippet:
```css
/* static/custom.css */
body { background:#f8fafc; font-family: "Segoe UI", Roboto, Arial; }
.card { border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,0.07); }
.card-header { background:#f0f2f6 !important; font-weight:600; }
```

## Data / Shapefiles
- The app currently expects district boundaries CSV at:
  `data/district_boundaries/csv/District_Boundaries.csv`
- If you have shapefiles and want them as EE FeatureCollections, upload them to Earth Engine assets and reference the asset path in `src/geometry.py` or `src/risk_map.py`.

## Development notes / TODOs
- Several functions in `src/risk_map.py`, `src/plot.py` and `src/fetch_datasets.py` are placeholders and need implementation:
  - risk index calculations, normalization, aggregation
  - image export / tile URL generation (for Leaflet)
  - time-series extraction and conversion to pandas DataFrame
- API endpoints in `app.py` can be enhanced to return map layers (tile URLs/GeoJSON) and base64 image source for plots.
- Consider caching Earth Engine requests to avoid repeated heavy operations.

## Troubleshooting
- Earth Engine errors: re-run `earthengine authenticate` and ensure `ee.Initialize()` is called. For headless servers, follow the CLI instructions.
- If map tiles are blank: verify `get_image_url` returns a valid tile/XYZ URL or GeoJSON and that Leaflet layers are created correctly.
- For local testing of shapefiles: use `geopandas` to inspect before uploading to EE.

## License
Add a license of your choice (e.g., MIT). This repository does not include a license file by default.

## Contact / Next steps
- Implement missing functions in `src/` to produce working layers/plots.
- Upload any local spatial assets to Earth Engine if you want server-side processing and `.getInfo()` usage.
