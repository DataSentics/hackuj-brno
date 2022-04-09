# Databricks notebook source
# MAGIC %pip install geopandas
# MAGIC %pip install rtree
# MAGIC %pip install pygeos

# COMMAND ----------

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

# COMMAND ----------

MAX_M_DISTANCE = 200
INPUT_FORMAT = 'epsg:4326'
METRES_FORMAT = 'EPSG:5514'

# COMMAND ----------

bins_df = gpd.read_file('../data/kontajnery.geojson').set_crs(INPUT_FORMAT).to_crs(METRES_FORMAT)
zones_df = (gpd.read_file('../data/rezidentni_zony.geojson')
               .set_crs(INPUT_FORMAT)
               .drop(columns=['poznamka', 'platnostdo', 'platnostod', 'datum_exportu'])
               .to_crs(METRES_FORMAT))

# COMMAND ----------

public_bins_df = bins_df[bins_df.verejnost == "A"][["tid", "typ_odpad_separovany", "komodita_odpad_separovany", "geometry"]]
public_bins_df.head()

# COMMAND ----------

zones_df.head()

# COMMAND ----------

public_bins_df.groupby("typ_odpad_separovany").count().display()

# COMMAND ----------

public_bins_df.groupby("komodita_odpad_separovany").count().display()

# COMMAND ----------

bio_bins_df = public_bins_df[public_bins_df.komodita_odpad_separovany == "Biologický odpad"]
paper_bins_df = public_bins_df[public_bins_df.komodita_odpad_separovany == "Papír"]
glass_bins_df = public_bins_df[(public_bins_df.komodita_odpad_separovany == "Sklo bílé") | (public_bins_df.komodita_odpad_separovany == "Sklo barevné")]
textil_bins_df = public_bins_df[public_bins_df.komodita_odpad_separovany == "Textil"]
plastic_bins_df = public_bins_df[public_bins_df.komodita_odpad_separovany == "Plasty, nápojové kartony a hliníkové plechovky od nápojů"]

# COMMAND ----------

bio_to_zones_df = bio_bins_df.sjoin_nearest(zones_df, lsuffix="bins", rsuffix="zones", distance_col="distance", max_distance=MAX_M_DISTANCE)
paper_to_zones_df = paper_bins_df.sjoin_nearest(zones_df, lsuffix="bins", rsuffix="zones", distance_col="distance", max_distance=MAX_M_DISTANCE)
glass_to_zones_df = glass_bins_df.sjoin_nearest(zones_df, lsuffix="bins", rsuffix="zones", distance_col="distance", max_distance=MAX_M_DISTANCE)
textil_to_zones_df = textil_bins_df.sjoin_nearest(zones_df, lsuffix="bins", rsuffix="zones", distance_col="distance", max_distance=MAX_M_DISTANCE)
plastic_to_zones_df = plastic_bins_df.sjoin_nearest(zones_df, lsuffix="bins", rsuffix="zones", distance_col="distance", max_distance=MAX_M_DISTANCE)

# COMMAND ----------

print((1.0 * len(bio_to_zones_df)) / len(bio_bins_df))
print((1.0 * len(paper_to_zones_df)) / len(paper_bins_df))
print((1.0 * len(glass_to_zones_df)) / len(glass_bins_df))
print((1.0 * len(textil_to_zones_df)) / len(textil_bins_df))
print((1.0 * len(plastic_to_zones_df)) / len(plastic_bins_df))

# COMMAND ----------

(0.43454871488344293+0.4679186228482003+0.4167134043746495)/3

# COMMAND ----------

brno_map = gpd.read_file('https://opendata.arcgis.com/datasets/1fcc06f548c34e93b9dd3014f8e58f8e_0.geojson')
brno_map.plot(linewidth=3, edgecolor='black')

# COMMAND ----------

rows = []
for i, row in paper_bins_df.iterrows():
    if row.tid not in paper_to_zones_df.tid.values:
        rows.append(row)

paper_outside_zone_df = gpd.GeoDataFrame( pd.concat(rows, axis=1).T ).set_crs(METRES_FORMAT)

# COMMAND ----------

fig, ax = plt.subplots(figsize = (25,25))
ax.set_facecolor('#0E1821')
brno_map.to_crs(epsg=4326).plot(ax=ax, color='#F0F0F0', linewidth=3, edgecolor='#0E1821')
paper_to_zones_df.to_crs(epsg=4326).plot(ax=ax, color='#5864FF')
paper_outside_zone_df.to_crs(epsg=4326).plot(ax=ax, color='#C23838')
ax.set_title('Brno paper bins', fontsize=25)

# COMMAND ----------

rows = []
for i, row in plastic_bins_df.iterrows():
    if row.tid not in plastic_to_zones_df.tid.values:
        rows.append(row)

plastic_outside_zone_df = gpd.GeoDataFrame( pd.concat(rows, axis=1).T ).set_crs(METRES_FORMAT)

# COMMAND ----------

fig, ax = plt.subplots(figsize = (25,25))
ax.format_coord = lambda x, y: ''
brno_map.to_crs(epsg=4326).plot(ax=ax, color='lightgrey', linewidth=3, edgecolor='black')
plastic_bins_df.to_crs(epsg=4326).plot(ax=ax, color='yellow')
plastic_outside_zone_df.to_crs(epsg=4326).plot(ax=ax, color='red')
ax.set_title('Brno plastic bins', fontsize=25)

# COMMAND ----------

rows = []
for i, row in glass_bins_df.iterrows():
    if row.tid not in glass_to_zones_df.tid.values:
        rows.append(row)

glass_outside_zone_df = gpd.GeoDataFrame( pd.concat(rows, axis=1).T ).set_crs(METRES_FORMAT)

# COMMAND ----------

fig, ax = plt.subplots(figsize = (25,25))
ax.format_coord = lambda x, y: ''
brno_map.to_crs(epsg=4326).plot(ax=ax, color='lightgrey', linewidth=3, edgecolor='black')
glass_bins_df.to_crs(epsg=4326).plot(ax=ax, color='green')
glass_outside_zone_df.to_crs(epsg=4326).plot(ax=ax, color='red')
ax.set_title('Brno glass bins', fontsize=25)

# COMMAND ----------


