# Databricks notebook source
# MAGIC %pip install geopandas
# MAGIC %pip install rtree
# MAGIC %pip install pygeos

# COMMAND ----------

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

# COMMAND ----------

MAX_M_DISTANCE = 200
INPUT_FORMAT = 'epsg:4326'
METRES_FORMAT = 'EPSG:5514'

# COMMAND ----------

bins_df = gpd.read_file('../data/kontajnery.geojson').set_crs(INPUT_FORMAT).to_crs(METRES_FORMAT)
capita_df = (gpd.read_file('../data/pocet_osob.geojson')
               .set_crs(INPUT_FORMAT)
               .to_crs(METRES_FORMAT))

# COMMAND ----------

def label_interval(row):
  if row['cyklus_vyvozu'] == '1x14 lichý':
    return 14.0
  if row['cyklus_vyvozu'] == '1x14 sudý':
    return 14.0
  if row['cyklus_vyvozu'] == '1x týdně':
    return 7.0
  if row['cyklus_vyvozu'] == '2x týdně':
    return 3.5
  if row['cyklus_vyvozu'] == '3x týdně':
    return 7.0 / 3.0
  if row['cyklus_vyvozu'] == '4x týdně':
    return 7.0 / 4.0
  if row['cyklus_vyvozu'] == '5x týdně':
    return 7.0 / 5.0
  if row['cyklus_vyvozu'] == '6x týdně':
    return 7.0 / 6.0
  if row['cyklus_vyvozu'] == '7x týdně':
    return 1.0
  return 30.0

# COMMAND ----------

bins_df['interval'] = bins_df.apply(lambda row: label_interval(row), axis=1)

# COMMAND ----------

bins_df.head()

# COMMAND ----------

capita_df.head()

# COMMAND ----------

bin_dist_df = capita_df.sjoin_nearest(bins_df, how='left', lsuffix='capita', rsuffix='bin', distance_col='dist_to_closest_bin')

# COMMAND ----------

bin_dist_df.head()

# COMMAND ----------

brno_map = gpd.read_file('https://opendata.arcgis.com/datasets/1fcc06f548c34e93b9dd3014f8e58f8e_0.geojson')

# COMMAND ----------

geo_df['dist_log'] = np.log(geo_df['dist_to_closest_bin'])

fig, ax = plt.subplots(figsize = (25,25))
ax.set_facecolor('#0E1821')
bin_dist_df.to_crs(epsg=4326).plot(ax=ax, color='#F0F0F0', linewidth=3, edgecolor='#0E1821')
paper_to_zones_df.to_crs(epsg=4326).plot(ax=ax, color='#5864FF')
paper_outside_zone_df.to_crs(epsg=4326).plot(ax=ax, color='#C23838')
ax.set_title('Brno paper bins', fontsize=25)
