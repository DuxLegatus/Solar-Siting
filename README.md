# Optimal Solar Deployment Siting in Georgia: A Seasonal Complementarity Model

## Research Question
This project identifies optimal regions for solar deployment in Georgia by combining solar irradiance, terrain suitability, and seasonal generation value — explicitly weighting winter solar potential to address Georgia's hydropower seasonality gap, where reduced winter hydro output currently drives reliance on energy imports and gas generation.

## Repo Structure
\`\`\`
data/
  raw/            # untouched downloaded data (NASA POWER, DEM, etc.)
  processed/      # cleaned/merged datasets ready for modeling
notebooks/        # exploratory analysis, model development
src/               # reusable pipeline scripts (data pull, processing, modeling)
site/              # Flask app for the public-facing results website (Pi-hosted)
docs/              # methodology notes, literature review, write-up drafts
\`\`\`

## Data Sources
- **Solar irradiance (monthly):** NASA POWER cAPI
- **Elevation / slope / aspect:** SRTM 30m or Copernicus DEM
- **Hydro seasonal generation (context/motivation):** GSE, IEA, ISET-PI

## Status
Project started: June 2026. See `docs/` for methodology notes and literature review.