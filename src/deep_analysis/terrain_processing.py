import rasterio
import numpy as np
import xdem

base_path = "../data/raw/deep_analysis/"
for i in range(1,4):
    filepath = f"{base_path}output_hh({i}).tif"
    dem = xdem.DEM(filepath)
    metric_crs = dem.get_metric_crs()
    dem_projected = dem.reproject(crs=metric_crs,nodata=-99999)
    slope = xdem.terrain.slope(dem_projected)
    aspect = xdem.terrain.aspect(dem_projected)
    hillshade = xdem.terrain.hillshade(dem_projected)
    outputs = [
        (f"{base_path}site_{i}_slope.tif", slope),
        (f"{base_path}site_{i}_aspect.tif", aspect),
        (f"{base_path}site_{i}_hillshade.tif", hillshade),
        (f"{base_path}site_{i}_dem_projected.tif", dem_projected),
    ]
    for filename, data in outputs:
        profile = {
            'driver': 'GTiff',
            'dtype': data.dtype,
            'count': 1,
            'width': data.shape[-1],
            'height': data.shape[-2],
            'transform': dem_projected.transform,
            'crs': dem_projected.crs,
            'nodata': -99999
        }
        
        with rasterio.open(filename, "w", **profile) as dst:
            dst.write(data.data.astype(data.dtype), 1)

        

