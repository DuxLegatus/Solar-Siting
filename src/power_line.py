from pyrosm import OSM
from config import OSM_DATA

osm = OSM(OSM_DATA)


power = osm.get_data_by_custom_criteria(
    custom_filter={
        "power": [
            "line",
            "minor_line",
            "substation"
        ]
    },
    filter_type="keep"
)
power_lines = power[
    power["power"].isin(["line", "minor_line"])
]

substations = power[
    power["power"] == "substation"
]
power_lines.to_file(
    "../data/raw/power_lines.geojson",
    driver="GeoJSON"
)

substations.to_file(
    "../data/raw/substations.geojson",
    driver="GeoJSON"
)