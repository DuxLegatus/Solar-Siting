# Optimal Solar Deployment Siting in Georgia: A Seasonal Complementarity Model

## Research Question
This project identifies optimal regions for solar deployment in Georgia by combining solar irradiance, terrain suitability, and seasonal generation value — explicitly weighting winter solar potential to address Georgia's hydropower seasonality gap, where reduced winter hydro output currently drives reliance on energy imports and gas generation.

## Methodology
1. **Grid**: a 0.25° regular grid over Georgia (~25km spacing, 123 points).
2. **Terrain**: elevation, slope, and aspect derived from the SRTM DEM.
3. **Irradiance**: GHI, DNI, and DIF sourced from the Global Solar Atlas (GSA/Solargis) at 250m resolution. GSA only provides annual averages for Georgia, so monthly variation is reconstructed by scaling each point's annual value using NASA POWER's monthly-to-annual ratio — GSA supplies the spatial precision, NASA POWER supplies the seasonal shape.
4. **Terrain correction**: an isotropic-sky transposition model (`DNI·cos(AOI) + DIF·(1+cos(slope))/2`) projects horizontal irradiance onto each point's *actual* DEM-derived slope and aspect, rather than assuming an optimal tilt angle.
5. **Suitability score**: a winter-weighted aggregation of monthly adjusted irradiance per point, reflecting the seasonal complementarity goal above.

Full derivation and formulas in `docs/methodology.md`.

## Validation
Getting the irradiance numbers right matters more than any other part of this pipeline, so it's validated against two very different kinds of reference data, not just one comparison that could look good by chance.

The strongest check compares `adjusted_irradiance` against **PVGIS** (JRC's PVGIS-SARAH3 dataset, built on ERA5 reanalysis). This is a genuinely independent source and it's queried using each point's real slope and aspect rather than an idealized tilt, so it's testing the model on its own terms:

| Metric | Value |
|---|---|
| R² | 0.85 |
| MAE | 0.86 kWh/m²/day |
| RMSE | 1.08 kWh/m²/day |
| MBE | +0.12 kWh/m²/day |
| Points compared | 1,440 (122 grid points × 12 months) |

The strong correlation (R²=0.85) says the model is capturing real spatial and seasonal irradiance patterns, not just producing plausible-looking numbers. The small positive bias is discussed under Known Limitations below — it has a specific, explainable cause rather than being unexplained noise.

Two additional, less independent checks were also run and are documented in `docs/validation_summary.md`: a comparison against GSA's own GTI layer (limited by GTI's optimum-tilt assumption, which doesn't match real terrain), and an internal consistency check confirming the GSA-downscaling step didn't introduce errors.

## Known Limitations
Being upfront about what this model doesn't do is as important as showing what it does:

- **Grid resolution** (0.25°, ~25km spacing) works well for national-scale screening but is too coarse to make individual site-level decisions from directly.
- **No horizon/terrain shading is modeled** only local slope/aspect tilt. This is the likely cause of the small positive bias seen in the PVGIS validation (MBE ≈ +0.12 kWh/m²/day): PVGIS accounts for nearby terrain blocking the sun at low angles, and this pipeline currently doesn't.
- **No grid/transmission proximity factor** is included yet, despite being one of the biggest practical constraints in real-world solar siting.
- **Land cover suitability weights** (if included) are illustrative starting values, not empirically derived from published siting studies. See `docs/methodology.md` for the full caveat.

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

## Setup
```bash
pip install -r requirements.txt
```

## Status
Project started: June 2026. See `docs/` for methodology notes, validation results, and literature review.
