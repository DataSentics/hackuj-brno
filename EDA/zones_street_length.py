# Databricks notebook source
# MAGIC %pip install geopandas
# MAGIC %pip install rtree
# MAGIC %pip install pygeos

# COMMAND ----------

import geopandas as gpd

# COMMAND ----------

MAX_M_DISTANCE = 200
INPUT_FORMAT = 'epsg:4326'
METRES_FORMAT = 'EPSG:5514'

# COMMAND ----------

streets_df = gpd.read_file('../data/ulice.geojson').set_crs(INPUT_FORMAT).to_crs(METRES_FORMAT)
zones_df = (gpd.read_file('../data/rezidentni_zony.geojson')
               .set_crs(INPUT_FORMAT)
               .drop(columns=['poznamka', 'platnostdo', 'platnostod', 'datum_exportu'])
               .to_crs(METRES_FORMAT))

# COMMAND ----------

streets_df.count()

# COMMAND ----------

streets_df.length.sum() / 1000

# COMMAND ----------

streets_df.head(15)

# COMMAND ----------

streets_df.shape[0]

# COMMAND ----------

streets_in_zones_df = streets_df.sjoin(zones_df, )

# COMMAND ----------

streets_in_zones_df.shape[0]

# COMMAND ----------

streets_in_zones_df.head(15).display()

# COMMAND ----------

deduplicated = streets_in_zones_df.drop_duplicates(subset=['ObjectId_left'])

# COMMAND ----------

streets_in_zones_df.length.sum() / 1000

# COMMAND ----------

deduplicated.length.sum() / 1000

# COMMAND ----------


