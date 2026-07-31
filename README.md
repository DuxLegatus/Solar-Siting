# Optimal Solar Deployment Siting in Georgia: A Seasonal Complementarity Model

## Research Question
This project identifies optimal regions for solar deployment in Georgia by combining solar irradiance, terrain suitability, and seasonal generation value, explicitly weighting winter solar potential to address Georgia's hydropower seasonality gap, where reduced winter hydro output currently drives reliance on energy imports and gas generation.

## Methodology
1. **Grid**: a 0.25° regular grid over Georgia (~25km spacing, 122 points).
2. **Terrain**: elevation, slope, and aspect derived from the SRTM DEM.
3. **Irradiance**: Irradiance was derived from GSA annual averages which were then scaled by Nasa power ratios.
4. **Transmission Line**: High-voltage transmission line network used to estimate grid accessibility. Data is derived from OpenStreetMap.
5. **Terrain correction**: an isotropic-sky transposition model (`DNI·cos(AOI) + DIF·(1+cos(slope))/2`) projects horizontal irradiance onto each point's *actual* DEM-derived slope and aspect, rather than assuming an optimal tilt angle.
6. **Suitability score**: a winter-weighted aggregation of monthly adjusted irradiance per point, reflecting the seasonal complementarity goal above.

Full derivation and formulas in `docs/methodology.md`.

## Validation
Getting the irradiance numbers correct is one of the most important things in the project, thats why I decided to check it against the independent source and then display the results.

The irradiance check compares the downscled irradiance against **PVGIS** (JRC's PVGIS-SARAH3 dataset, built on ERA5 reanalysis). PVGIS is basically the european equivalent of GSA, therefore if irradiance scores were close to each other that would prove that the downscaled irradiance data was correct

| Metric | Value |
|---|---|
| R² | 0.85 |
| MAE | 0.86 kWh/m²/day |
| RMSE | 1.08 kWh/m²/day |
| MBE | +0.12 kWh/m²/day |
| Points compared | 1,464 (122 grid points × 12 months) |

The strong correlation (R²=0.85) is suggesting the model captures the main spatial and seasonal patterns in irradiance.

## Known Limitations

- **Grid resolution** (0.25°, ~25km spacing) works well for national-scale screening but is too coarse to make individual site-level decisions from directly.
- **Several weighting factors in the suitability score** (land cover multipliers, the protected-area minimum-size threshold, grid proximity's voltage/distance parameters) are just rough estimates and not empirecally derived models. See `docs/methodology.md` for the specific values and reasoning behind each.

## Repo Structure
```
data/
  raw/            # untouched downloaded data (GSA rasters, NASA POWER, DEM, etc.)
  processed/      # cleaned/merged datasets ready for modeling
notebooks/        # exploratory analysis, model development
src/               # reusable pipeline scripts (data pull, processing, modeling)
site/              # Flask app for the public-facing results website
docs/              # methodology notes, validation results, literature review
```

## Data Sources
- **Solar irradiance (GHI/DNI/DIF, annual, 250m):** [Global Solar Atlas](https://globalsolaratlas.info) (Solargis)
- **Solar irradiance (monthly seasonal shape):** [NASA POWER](https://power.larc.nasa.gov) (`ALLSKY_SFC_SW_DWN`)
- **Independent irradiance validation:** [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) (JRC, PVGIS-SARAH3 / ERA5)
- **Elevation / slope / aspect:** SRTM 30m
- **Hydro seasonal generation (context/motivation):** GSE, IEA, ISET-PI
- **Transmission lines:** [OpenStreetMap](https://www.openstreetmap.org) (via Geofabrik extract)

## Setup
```bash
pip install -r requirements.txt
```

## Status
Project started: June 2026. See `docs/` for methodology notes, validation results, and literature review.
