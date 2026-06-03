#!/usr/bin/env python3
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import os

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------

INPUT_SHP = "/mnt/d/data/0_masks/IBRA/SWWA/ibra7_swwaregions.shp"
OUTPUT_SHP = "/mnt/d/data/0_masks/IBRA/SWWA/ibra7_swwa_mask_clean.shp"

os.makedirs(os.path.dirname(OUTPUT_SHP), exist_ok=True)

# ----------------------------------------------------
# LOAD
# ----------------------------------------------------

gdf = gpd.read_file(INPUT_SHP)
gdf["MERGE_ID"] = 1
merged = gdf.dissolve(by="MERGE_ID")

# ----------------------------------------------------
# EXPLODE INTO INDIVIDUAL POLYGONS
# ----------------------------------------------------

parts = merged.explode(index_parts=True, ignore_index=True)

# Project to metres for area calculation
parts = parts.to_crs(3857)
parts["AREA"] = parts.area

# ----------------------------------------------------
# IDENTIFY MAINLAND (largest polygon)
# ----------------------------------------------------

mainland = parts.loc[[parts["AREA"].idxmax()]]

# ----------------------------------------------------
# REMOVE HOLES FROM MAINLAND ONLY
# ----------------------------------------------------

def remove_holes(geom):
    if isinstance(geom, Polygon):
        return Polygon(geom.exterior)   # keep only outer boundary
    return geom

mainland["geometry"] = mainland["geometry"].apply(remove_holes)

# ----------------------------------------------------
# KEEP ALL OTHER ISLANDS (unchanged)
# ----------------------------------------------------

islands = parts.drop(parts["AREA"].idxmax())

# ----------------------------------------------------
# RECOMBINE MAINLAND + ISLANDS
# ----------------------------------------------------

clean = gpd.GeoDataFrame(
    pd.concat([mainland, islands], ignore_index=True),
    crs=parts.crs
)

# Back to geographic CRS
clean = clean.to_crs(4326)

# ----------------------------------------------------
# SAVE
# ----------------------------------------------------

clean.to_file(OUTPUT_SHP)
print(f"Saved cleaned SWWA mask to: {OUTPUT_SHP}")
