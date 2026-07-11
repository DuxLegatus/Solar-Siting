# Methodology

This document is supposed to explain the pipeline in detail, the design choices I made during production, and why I made them.

## 1. Grid Generation

This is a regular 0.25° latitude/longitude grid meant to represent Georgia. In total there are 123 points on the grid, spaced roughly 25km apart. I decided this resolution would be enough for this project, since it's fast and accurate enough to represent how suitable a region is for solar power at a national scale.

## 2. Terrain: Elevation, Slope, Aspect

Elevation, slope, and aspect are all sampled from the SRTM 30m DEM at each grid point.

**Aspect nodata handling**: flat terrain's aspect is represented by `-9999`. These points are converted to `NaN` before any trigonometric calculations are applied, so they don't silently create problems — if the conversion happened after computing `aspect_rad`, `radians(-9999)` would flow straight into the geometry calculations and produce a plausible-looking but meaningless value for flat points, instead of a clean, visible `NaN` I could actually catch.

## 3. Irradiance: Combining GSA and NASA POWER

The project initially used NASA POWER as the sole irradiance source. It has a simple, free monthly API and was the natural starting point. The issue only became apparent during validation: NASA POWER's native resolution is roughly 50km, and once I compared it against the Global Solar Atlas, it turned out my 123 grid points were mapping to just **15 truly distinct NASA POWER values**. Many "different" points on the grid were silently returning identical irradiance, regardless of real differences in terrain or local climate.

Rather than drop NASA POWER entirely, I combined it with the Global Solar Atlas: GSA supplies genuinely fine-grained (250m) spatial detail, and NASA POWER's monthly time series supplies the seasonal shape that GSA's annual-only Georgia data doesn't include on its own.

**Downscaling approach**: for each point, I computed the ratio of each NASA POWER month to that same point's NASA POWER annual average, then applied that ratio to GSA's annual value instead:

```
monthly_ratio[point, month] = nasa_power_monthly[point, month] / nasa_power_annual[point]
ghi_monthly[point, month]   = gsa_ghi_annual[point] * monthly_ratio[point, month]
dni_monthly[point, month]   = gsa_dni_annual[point] * monthly_ratio[point, month]
dif_monthly[point, month]   = gsa_dif_annual[point] * monthly_ratio[point, month]
```

The reasoning: NASA POWER's problem was *spatial* resolution, not *temporal* accuracy — its monthly seasonal cycle (day length, typical cloud season) is a large-scale climate feature that's captured reasonably well even at 50km. This lets each source do what it's actually good at: GSA for spatial detail, NASA POWER for seasonal shape. It does rest on the assumption that NASA POWER's *relative* monthly pattern is trustworthy even where its *absolute* magnitude wasn't — I'm stating that assumption explicitly here rather than leaving it implicit.

Before trusting this, I checked that each point's 12 monthly ratios averaged back to ≈1.0 (std ≈ 0.0007 across all points) — confirming the ratios were internally consistent with the annual value they were derived from.

## 4. Terrain Correction

The goal of this step is to convert horizontal-surface irradiance (GHI/DNI/DIF) into irradiance on the *actual* tilted surface at each grid point — using its real DEM-derived slope and aspect, not an assumed optimal panel angle.

**Formula**:
```
cos_zenith = sin(lat)·sin(declination) + cos(lat)·cos(declination)
cos_aoi    = cos_zenith·cos(slope) + sin_zenith·sin(slope)·cos(sun_azimuth − aspect)
cos_aoi    = clip(cos_aoi, 0, None)   # negative = sun is below the local horizon plane

adjusted_irradiance = dni_monthly · cos_aoi + dif_monthly · (1 + cos(slope)) / 2
```

Solar declination is a fixed monthly climatological value rather than solved per-day, and `sun_azimuth` is fixed at 180° (south), approximating the sun's position at solar noon in the Northern Hemisphere.

**Why this formula, and not an earlier version**: an earlier version of this correction applied a single ratio (`cos_aoi / cos_zenith`) directly to *total* GHI. Two problems with that, which I only caught during validation:

1. It only calculates sun geometry at solar noon, then applies that single ratio to a full day's energy total — implicitly assuming the noon sun angle represents the whole day's irradiance distribution. This breaks down badly at low sun angles (winter, higher latitudes), where the ratio can swing much larger than the real all-day average would justify.
2. It doesn't separate beam and diffuse irradiance. GHI is a mix of both, but only the beam component should be scaled by a directional cosine factor — diffuse skylight arrives from the whole sky dome and needs a different kind of transposition (a tilted surface "sees" less of the sky as it tilts away from horizontal, independent of exact sun position).

The current formula fixes both: it applies the beam correction (`cos_aoi`) only to DNI (already a beam-only, sun-normal quantity, so no separate zenith correction is needed), and applies a separate isotropic-sky diffuse transposition to DIF — the standard Liu-Jordan isotropic-sky model.


## 5. Suitability Score
This is supposed to use all of the data to get the final Suitability score

**Formula**:
```
suitability_score[point] = Σ over months (
    adjusted_irradiance[point, month]
    × energy_import_share[month]
    × solar_multiplier[point]
    × protected_multiplier[point]
    × 0.85
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

Only five months which actually imported matter to the final suitability score.
**The Solar_multiplier** penalizes certain land types. the land type data for Georgia was arquired from the ESA WorldCover.
**The Protected_multiplier** is represantation of nationally protected areas in Georgia. The data for it was gathered from WDPA. If the area is protected then solar suitability becomes 0 in that region.
A fixed 0.85 multiplier is also applied, representing an estimated system loss factor

## 6. Validation

I checked irradiance accuracy against multiple references, deliberately varying in how independent each one is from my pipeline's own inputs — a comparison against a source that shares data lineage with my inputs can look artificially good without actually proving anything.

| Check | Reference | Independence | Purpose |
|---|---|---|---|
| `adjusted_irradiance` vs PVGIS | JRC PVGIS-SARAH3/ERA5 | Fully independent — different satellite record, different methodology, uses each point's real slope/aspect | Primary external validation |
| `adjusted_irradiance` vs GTI | GSA/Solargis | Same provider as my irradiance inputs; GTI also assumes optimum tilt, not real terrain | Secondary check, expected structural gap |
| `raw_irradiance` vs GHI | GSA/Solargis | Not independent — `raw_irradiance` is derived directly from this layer | Internal consistency check on the downscaling math, not external validation |

**PVGIS result (primary validation)**: R²=0.85, MAE=0.86 kWh/m²/day, MBE=+0.12 kWh/m²/day, n=1,440 point-months.

The R² is the number I trust most here — it confirms `adjusted_irradiance` tracks real spatial and seasonal variation as measured by a genuinely independent source, not just that the two datasets happen to land in a similar numeric range. That distinction matters — see the sidebar below.

The small positive MBE (+0.12) is consistent with something my model doesn't do: PVGIS applies DEM-based horizon shading (accounting for nearby terrain blocking low-angle sun), while my correction only considers local slope/aspect tilt, not surrounding terrain. I've listed this under Known Limitations rather than treating it as unexplained error.

Full metrics and plots for all three comparisons are in `validation_summary.md` and the accompanying PNGs.

## 7. Known Limitations
- **Grid resolution** (0.25°, ~25km spacing) is fine for national-scale screening, but too coarse for individual site-level decisions.
- **No horizon/terrain shading is modeled** — only local slope/aspect tilt, evidenced by the positive MBE in the PVGIS validation.
- **No grid/transmission proximity factor** is included yet, despite being one of the biggest practical constraints in real-world solar siting.
- **Land cover suitability multipliers** (if included) are illustrative starting values, not empirically derived from a published weighting scheme — see the notes in that script for the reasoning.


## 8. Data Sources
- **Solar irradiance (GHI/DNI/DIF, annual, 250m):** [Global Solar Atlas](https://globalsolaratlas.info) (Solargis)
- **Solar irradiance (monthly seasonal shape):** [NASA POWER](https://power.larc.nasa.gov) (`ALLSKY_SFC_SW_DWN`)
- **Independent irradiance validation:** [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) (JRC, PVGIS-SARAH3 / ERA5)
- **Elevation / slope / aspect:** SRTM 30m
- **Hydro seasonal generation (context/motivation):** GSE, IEA, ISET-PI