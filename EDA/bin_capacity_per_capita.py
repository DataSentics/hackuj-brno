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

def label_frequency(row):
  if row['cyklus_vyvozu'] == '1x14 lichý':
    return 0.5
  if row['cyklus_vyvozu'] == '1x14 sudý':
    return 0.5
  if row['cyklus_vyvozu'] == '1x týdně':
    return 1.0
  if row['cyklus_vyvozu'] == '2x týdně':
    return 2.0
  if row['cyklus_vyvozu'] == '3x týdně':
    return 3.0
  if row['cyklus_vyvozu'] == '4x týdně':
    return 4.0
  if row['cyklus_vyvozu'] == '5x týdně':
    return 5.0
  if row['cyklus_vyvozu'] == '6x týdně':
    return 6.0
  if row['cyklus_vyvozu'] == '7x týdně':
    return 7.0
  return 7.0/30.0

# COMMAND ----------

bins_df['per_week_frequency'] = bins_df.apply(lambda row: label_frequency(row), axis=1)
bins_df = bins_df[bins_df['komodita_odpad_separovany'] == 'Papír']

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

bin_dist_df['dist_ceiled'] = bin_dist_df.apply(lambda x: 700.0 if x.dist_to_closest_bin > 700.0 else x.dist_to_closest_bin, axis=1)

fig, ax = plt.subplots(figsize = (25,25))
ax.set_facecolor('#0E1821')
brno_map.to_crs(epsg=4326).plot(ax=ax, color='#F0F0F0', linewidth=3, edgecolor='#0E1821')
bin_dist_df.to_crs(epsg=4326).plot(column = 'dist_ceiled', ax=ax, cmap = 'rainbow',
            legend = True, legend_kwds={'shrink': 0.3}, 
            markersize = 10)
ax.set_title('House to closest separation bin (ceiled scale)', fontsize=25)

# COMMAND ----------

bin_dist_df['dist_log'] = np.log(bin_dist_df['dist_to_closest_bin'])

fig, ax = plt.subplots(figsize = (25,25))
ax.set_facecolor('#0E1821')
brno_map.to_crs(epsg=4326).plot(ax=ax, color='#F0F0F0', linewidth=3, edgecolor='#0E1821')
bin_dist_df.to_crs(epsg=4326).plot(column = 'dist_log', ax=ax, cmap = 'rainbow',
            legend = True, legend_kwds={'shrink': 0.3}, 
            markersize = 10)
ax.set_title('House to closest separation bin (log scale)', fontsize=25)

# COMMAND ----------

bin_agg_df = bin_dist_df.groupby('tid', as_index=False).agg({'number_of_people': 'sum'})
bin_agg_df.display()

# COMMAND ----------

bin_agg_full_stats = bin_agg_df.set_index(['tid']).join(bins_df[['tid', 'objem', 'per_week_frequency', 'geometry']].set_index(['tid'])).reset_index()
bin_agg_full_stats.head()

# COMMAND ----------

len(bin_agg_full_stats)

# COMMAND ----------

bin_agg_full_stats = bin_agg_full_stats[bin_agg_full_stats.number_of_people > 0.0]
len(bin_agg_full_stats)

# COMMAND ----------

bin_agg_full_stats['exhaustion'] = bin_agg_full_stats.apply(lambda x: x.number_of_people/(x.objem *x.per_week_frequency), axis=1)

# COMMAND ----------

bin_agg_full_stats.sort_values(by='exhaustion', ascending=False).head()

# COMMAND ----------

bin_agg_full_stats_gdf = gpd.GeoDataFrame(bin_agg_full_stats)

# COMMAND ----------

bin_agg_full_stats_gdf[bin_agg_full_stats_gdf['tid'] == 14019].to_crs(INPUT_FORMAT)

# COMMAND ----------

fig, ax = plt.subplots(figsize = (25,25))
ax.set_facecolor('#0E1821')
brno_map.to_crs(epsg=4326).plot(ax=ax, color='#F0F0F0', linewidth=3, edgecolor='#0E1821')
bin_agg_full_stats_gdf.to_crs(epsg=4326).plot(column = 'exhaustion', ax=ax, cmap = 'rainbow',
            legend = True, legend_kwds={'shrink': 0.3}, 
            markersize = 10)
ax.set_title('Exhaustion of separation bins (normal scale)', fontsize=25)

# COMMAND ----------

bin_agg_full_stats_gdf['exhaustion_log'] = np.log(bin_agg_full_stats_gdf['exhaustion'])

fig, ax = plt.subplots(figsize = (25,25))
ax.set_facecolor('#0E1821')
brno_map.to_crs(epsg=4326).plot(ax=ax, color='#F0F0F0', linewidth=3, edgecolor='#0E1821')
bin_agg_full_stats_gdf.to_crs(epsg=4326).plot(column = 'exhaustion_log', ax=ax, cmap = 'rainbow',
            legend = True, legend_kwds={'shrink': 0.3}, 
            markersize = 10)
ax.set_title('Exhaustion of separation bins (log scale)', fontsize=25)

# COMMAND ----------


