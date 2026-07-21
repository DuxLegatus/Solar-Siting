# Methodology

This document is supposed to explain the pipeline in detail, the design choices I made during production, and why I made them.

## 1. Grid Generation

This is a regular 0.25° latitude/longitude grid meant to represent Georgia. In total there are 123 points on the grid, spaced roughly 25km apart. I decided this resolution would be enough for this project, since it's fast and accurate enough to represent how suitable a region is for solar power at a national scale.

## 2. Terrain: Elevation, Slope, Aspect

Elevation, slope, and aspect are all sampled from the SRTM 30m DEM at each grid point.

**Aspect nodata handling**: flat terrain's aspect is represented by `-9999`. These points are converted to `NaN` so they don't create problems, during the calculation. If I didn't do the conversion before the calculations I would get results that are misrepresantation of the actual suitability.

## 3. Irradiance: Combining GSA and NASA POWER

Initially I decided to use nasa power for the irradiance. It has a simple, free monthly API and was the natural starting point, however it had its limitations, which I was not aware of at the start of the project. The issue only became apparent during validation: NASA POWER's native resolution is roughly 50km, and once I compared it against the Global Solar Atlas, it turned out my 123 grid points were mapping to 15 distinct NASA POWER values. Many "different" points on the grid were silently returning identical irradiance, regardless of real differences in terrain or local climate.

Rather than to drop NASA POWER entirely, I combined it with the Global Solar Atlas: GSA supplies fine-grained (250m) spatial detail, and NASA POWER's monthly time series supplies the seasonal shape that GSA's annual-only Georgia data doesn't include on its own.

**Downscaling approach**: for each point, I computed the ratio of each NASA POWER month to that same point's NASA POWER annual average, then applied that ratio to GSA's annual value instead:

```
monthly_ratio[point, month] = nasa_power_monthly[point, month] / nasa_power_annual[point]
ghi_monthly[point, month]   = gsa_ghi_annual[point] * monthly_ratio[point, month]
dni_monthly[point, month]   = gsa_dni_annual[point] * monthly_ratio[point, month]
dif_monthly[point, month]   = gsa_dif_annual[point] * monthly_ratio[point, month]
```

The reasoning: NASA POWER's problem was *spatial* resolution, not *temporal* accuracy. Its monthly seasonal cycle (day length, typical cloud season) is a large-scale climate feature that's captured reasonably well even at 50km. This lets each source do what it's good at: GSA for spatial detail, NASA POWER for seasonal shape. It does rest on the assumption that NASA POWER's *relative* monthly pattern is trustworthy even where its *absolute* magnitude wasn't.

## 4. Terrain Correction

The main goal of this step was to apply aoi(angle of incidence) into the calculations. That way we would have gotten data that actually represents the tilted terrain instead of just straight irradiance which does not factor in things like slope, aspect and suns position during certain months etc.

**Formula**:
```
cos_zenith = sin(lat)·sin(declination) + cos(lat)·cos(declination)
cos_aoi    = cos_zenith·cos(slope) + sin_zenith·sin(slope)·cos(sun_azimuth − aspect)
cos_aoi    = clip(cos_aoi, 0, None)   # negative = sun is below the local horizon plane

adjusted_irradiance = dni_monthly · cos_aoi + dif_monthly · (1 + cos(slope)) / 2
```

Solar declination is a fixed monthly climatological value rather than solved per-day, and `sun_azimuth` is fixed at 180° (south), approximating the sun's position at solar noon in the Northern Hemisphere.


## 5. Grid accesibility

This step is supposed to get data of transmission lines in the georgia. This is very important, because for solar plants to actually work effectively there is need for transmission lines to be close to the actual plant location. This data was fetched from OpenStreetMap.
After fetching the data, it is processed and then the calculation is run to compute how close is the line to the grid point. if it does exceeds certain range, The score will go down.
**Formula for grid score**
```
line_score = 1 / (1 + distance_to_line_km / 25)
substation_score = 1 / (1 + distance_to_substation_km / 25)
grid_score = (line_score + substation_score) / 2
```

## 6. Suitability Score
This is supposed to use all of the data to get the final Suitability score

**Formula**:
```
suitability_score[point] = Σ over months (
    adjusted_irradiance[point, month]
    × energy_import_share[month]
    × solar_multiplier[point]
    × protected_multiplier[point]
    × grid_score[point]
    × system_loss_factor
)
```

**Energy_import_share** was derived from the 2023 georgian import needs, where our total imports were 790GWh.

| Month | Import share |
|---|---|
| Jan | 31% |
| Feb | 26% |
| Mar | 19% |
| Nov | 10% |
| Dec | 14% |
| Apr–Oct | 0% |

Only five months which imported matter to the final suitability score.
**The Solar_multiplier** penalizes certain land types. the land type data for Georgia was arquired from the ESA WorldCover.
**The Protected_multiplier** is represantation of nationally protected areas in Georgia. The data for it was gathered from WDPA. If the area is protected then solar suitability becomes 0 in that region.
**system_loss_factor** is applied which ranges from 0.75 to 0.9 based on the adjustable parameter, but the default value of this is 0.85

## 7. Validation

I checked irradiance accuracy against PVGIS, which is a tool developed by the European Commission that calculates the solar energy production potential of photovoltaic systems at any location worldwide. It is free, fast and completely independet from GSA, so it was a natural choice when picking a source to verify my data.

| Check | Reference | Independence | Purpose |
|---|---|---|---|
| `adjusted_irradiance` vs PVGIS | JRC PVGIS-SARAH3/ERA5 | Fully independent (different satellite record, different methodology, uses each point's real slope/aspect) | Primary external validation |

**PVGIS result (primary validation)**: R²=0.85, MAE=0.86 kWh/m²/day, MBE=+0.12 kWh/m²/day, n=1,464 point-months.

The R² is the number I trust most here. It confirms `adjusted_irradiance` tracks real spatial and seasonal variation as measured by an independent source, not that the two datasets happen to land in a similar numeric range.

A closer look at the residuals (error broken down by slope and by month) shows the average error isn't uniform: it's a real seasonal swing, overestimating in summer and underestimating in winter, rather than a flat bias or one driven by terrain steepness. 

Full metrics and plots for all comparisons are in `validation_summary.md` and the accompanying PNGs.

## 8. Known Limitations
- **Grid resolution** (0.25°, ~25km spacing) is fine for national-scale screening, but too coarse for individual site-level decisions.
- **Downscaled irradiance carries a seasonal bias**  see validation_summary.md for the full residual analysis and what it means for this project's winter-focused goal.
- **Several weighting factors in the suitability score** (land cover multipliers, the protected-area minimum-size threshold, and grid proximity's voltage/distance parameters) reflect judgment calls rather than published, empirically-derived models.


## 9. Data Sources
- **Solar irradiance (GHI/DNI/DIF, annual, 250m):** [Global Solar Atlas](https://globalsolaratlas.info) (Solargis)
- **Solar irradiance (monthly seasonal shape):** [NASA POWER](https://power.larc.nasa.gov) (`ALLSKY_SFC_SW_DWN`)
- **Independent irradiance validation:** [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) (JRC, PVGIS-SARAH3 / ERA5)
- **Elevation / slope / aspect:** SRTM 30m
- **Hydro seasonal generation (context/motivation):** GSE, IEA, ISET-PI