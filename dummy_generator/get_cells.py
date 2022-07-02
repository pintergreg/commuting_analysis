import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

budapest = gpd.read_file("input/budapest_border.geojson", crs=4326)
area = budapest["geometry"][0]

header = ["radio", "mcc", "mnc", "lac", "cid", "?", "lon", "lat", "range",
          "samples", "changeable", "created", "updated", "avg_signal"]
opencellid = pd.read_csv("input/216.csv", names=header)

# create geometry table
opencellid["point_tuple"] = tuple(zip(opencellid["lon"], opencellid["lat"]))
opencellid["geometry"] = opencellid["point_tuple"].apply(Point)
cells = gpd.GeoDataFrame(opencellid, geometry="geometry", crs=4326)

# filter to Vodafone cells and remove 4G
cells = cells.query("mnc == 70 & radio != 'LTE'").copy()
# keep cells with at least 250 samples from Budapest
cells = cells.query("geometry.intersects(@area) & samples >= 250").copy()

# drop unnecessary columns
cells = cells.drop(["?", "changeable", "avg_signal", "point_tuple"], axis=1)
cells.to_csv("dummy_data/cells.csv", index=False)
