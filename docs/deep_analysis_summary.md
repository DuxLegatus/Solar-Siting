# Deep Analysis Summary


## Overview

I selected three of the most prominent sites and analyzed them more closely.

The analysis includes:

- Slope analysis
- Aspect analysis
- Terrain suitability assessment
- Monthly terrain-adjusted irradiance calculation
- Final normalized suitability mapping

## Site 1:

## Terrain statistics 

| Metric | Value |
|---------|------:|
| Minimum slope | 0.00° |
| Maximum slope | 56.79° |
| Mean slope | 7.31° |
| Median slope | 2.46° |
| Terrain with slope < 5° | 65.69% |
| Terrain with slope < 10° | 75.50% |
| Terrain with slope < 15° | 81.16% |
| South-oriented terrain | 30.27% |


## Terrain Suitability

| Metric | Score |
|---------|------:|
| Slope score | 0.764 |
| Aspect score | 0.557 |
| Overall terrain suitability | **0.702** |

So the site 1 has very consistent and suitable terrain for the solar power. More than 75 % of its area has slope below 10°. One flaw that this site has is that only around 30% of the site is south-oriented, which is bringing overall score done a little bit.



## Site 2:

## Terrain statistics 

| Metric | Value |
|---------|------:|
| Minimum slope | 0.00° |
| Maximum slope | 67.33° |
| Mean slope | 10.40° |
| Median slope | 8.01° |
| Terrain with slope < 5° | 33.13% |
| Terrain with slope < 10° | 58.21% |
| Terrain with slope < 15° | 73.94% |
| South-oriented terrain | 49.26% |

## Terrain Suitability

| Metric | Score |
|---------|------:|
| Slope score | 0.611 |
| Aspect score | 0.682 |
| Overall terrain suitability | **0.632** |


Site 2 has way more steeper terrain compared to other sites, resulting in the lowest slope score. Fortunately almost half of the terrain is south-oriented which partially compensates for the steeper terrain.

## Site 3:

## Terrain statistics 

| Metric | Value |
|---------|------:|
| Minimum slope | 0.00° |
| Maximum slope | 48.26° |
| Mean slope | 4.37° |
| Median slope | 2.37° |
| Terrain with slope < 5° | 71.01% |
| Terrain with slope < 10° | 87.81% |
| Terrain with slope < 15° | 94.95% |
| South-oriented terrain | 50.74% |

## Terrain Suitability

| Metric | Score |
|---------|------:|
| Slope score | 0.880 |
| Aspect score | 0.693 |
| Overall terrain suitability | **0.824** |


site 3 actually has the most favorable terrain among the three candidates. around 90% of its terrain has slope below 10°, and approximately half of the terrain is south-oriented, which results in the highest suitability score



## Overall conclusion

Based on the terrain analysis, first and third sites are the most favorable for the solar farms, they have quite consistent and gentle terrain, which obviously helps maximize energy production, while also minimizing costs. Second site is ok too but I believe that steeper terrain will make it less economically feasible compared two other two candidates.


## methodology

I decided to calculate terrain suitability using weighted combination of slope(70%) and aspect(30%). I assigned greater value to slope, because construction feasibility generally has a larger influence on project cost than panel orientation.