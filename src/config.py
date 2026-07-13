from pathlib import Path
import numpy as np 

PROJECT_ROOT = Path(__file__).resolve().parent.parent
 
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"
SITE_DIR = PROJECT_ROOT / "site"

NATURAL_EARTH_SHP = RAW_DIR / "naturalearth" / "ne_10m_admin_0_countries.shp"
 
DEM_TIF = RAW_DIR / "dem" / "output_SRTMGL1.tif"
SLOPE_TIF = RAW_DIR / "dem" / "slope.tif"
ASPECT_TIF = RAW_DIR / "dem" / "aspect.tif"
 
WORLDCOVER_TILES_DIR = RAW_DIR / "MAP"
 
GSA_GHI_TIF = RAW_DIR / "validation" / "GHI.tif"
GSA_DNI_TIF = RAW_DIR / "validation" / "DNI.tif"
GSA_DIF_TIF = RAW_DIR / "validation" / "DIF.tif"

WDPA_SHAPEFILES = [
    RAW_DIR / "WDPA_WDOECM_Jul2026_Public_GEO_shp_0" / "WDPA_WDOECM_Jul2026_Public_GEO_shp-polygons.shp",
    RAW_DIR / "WDPA_WDOECM_Jul2026_Public_GEO_shp_1" / "WDPA_WDOECM_Jul2026_Public_GEO_shp-polygons.shp",
    RAW_DIR / "WDPA_WDOECM_Jul2026_Public_GEO_shp_2" / "WDPA_WDOECM_Jul2026_Public_GEO_shp-polygons.shp",
]

GRID_POINTS_CSV = PROCESSED_DIR / "georgia_grid_points.csv"
ELEVATION_CSV = PROCESSED_DIR / "georgia_elevation.csv"
SLOPE_ASPECT_CSV = PROCESSED_DIR / "georgia_slope_aspect.csv"
LANDCOVER_CSV = PROCESSED_DIR / "georgia_grid_with_landtype.csv"
PROTECTED_AREA_CSV = PROCESSED_DIR / "georgia_protected_area.csv"
 
NASA_POWER_RAW_CSV = PROCESSED_DIR / "solar_irradiance_processed.csv"
NASA_POWER_MONTHLY_AVG_CSV = PROCESSED_DIR / "solar_irradiance_monthly_avg.csv"
IRRADIANCE_DOWNSCALED_CSV = PROCESSED_DIR / "georgia_irradiance_downscaled.csv"
 
SOLAR_DATA_DEBUG_CSV = PROCESSED_DIR / "georgia_solar_data_full_debug.csv"
SOLAR_DATA_FINAL_CSV = PROCESSED_DIR / "georgia_solar_data_final.csv"
SUITABILITY_CSV = PROCESSED_DIR / "georgia_solar_suitability.csv"
 
PVGIS_POA_CSV = PROCESSED_DIR / "georgia_pvgis_poa.csv"
PVGIS_VALIDATION_CSV = PROCESSED_DIR / "adjusted_irradiance_pvgis_validation.csv"


SUITABILITY_MAP_PNG = DOCS_DIR / "solar_suitability.png"
PVGIS_SCATTER_PNG = DOCS_DIR / "adjusted_irradiance_vs_pvgis.png"
PVGIS_ERROR_HISTOGRAM_PNG = DOCS_DIR / "pvgis_error_histogram.png"
PVGIS_ERROR_VS_SLOPE_PNG = DOCS_DIR / "pvgis_error_vs_slope.png"
PVGIS_ERROR_BY_MONTH_PNG = DOCS_DIR / "pvgis_error_by_month.png"
SUITABILITY_MAP_HTML = SITE_DIR / "georgia_suitability_map.html"

GRID_LAT_MIN, GRID_LAT_MAX = 41.0, 43.6
GRID_LON_MIN, GRID_LON_MAX = 40.0, 46.6,
GRID_STEP = 0.25

DECLINATION_BY_MONTH = {
    1: -20.9, 2: -13.0, 3: -2.4, 4: 9.4, 5: 18.8, 6: 23.1,
    7: 21.2, 8: 13.5, 9: 2.2, 10: -9.6, 11: -18.9, 12: -23.0,
}

TOTAL_ANNUAL_IMPORTS_GWH = 790
MONTHLY_IMPORTS_GWH = {1: 247, 2: 207, 3: 147, 11: 81, 12: 108}
IMPORT_SHARE_BY_MONTH = {
    month: round(gwh / TOTAL_ANNUAL_IMPORTS_GWH, 2)
    for month, gwh in MONTHLY_IMPORTS_GWH.items()
}

SYSTEM_LOSS_FACTOR = 0.85


WORLDCOVER_CLASSES = {
    10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland",
    50: "Built-up", 60: "Bare / sparse vegetation", 70: "Snow and ice",
    80: "Permanent water bodies", 90: "Herbaceous wetland", 95: "Mangroves",
    100: "Moss and lichen", 0: "No data",
}

SOLAR_MULTIPLIER_BY_LANDCOVER = {
    10: 0.15, 20: 0.25, 30: 0.85, 40: 0.80, 50: 0.05,
    60: 0.95, 70: 0.00, 80: 0.00, 90: 0.30, 95: 0.05, 100: 0.10,
    0: np.nan,  # no data - unknown
}