#!/usr/bin/env python3
import geopandas as gpd
import os

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------

INPUT_SHP = "/mnt/d/data/0_masks/IBRA/downloaded-Australia/ibra7_subregions.shp"
OUTPUT_SHP = "/mnt/d/data/0_masks/IBRA/SWWA/ibra7_swwaregions.shp"

os.makedirs(os.path.dirname(OUTPUT_SHP), exist_ok=True)

# ----------------------------------------------------
# LOAD SHAPEFILE
# ----------------------------------------------------

print(f"Loading shapefile: {INPUT_SHP}")
gdf = gpd.read_file(INPUT_SHP)

print("Columns available:", gdf.columns)

# ----------------------------------------------------
# TARGET IBRA7 SUBREGIONS
# ----------------------------------------------------

TARGET_SUBREGIONS = [
    "DANDARAGAN PLATEAU",
    "LESUEUR SANDPLAIN",
    "NORTHERN JARRAH FOREST",
    "PERTH",
    "SOUTHERN JARRAH FOREST",
    "WARREN"
]

# ----------------------------------------------------
# FILTER
# ----------------------------------------------------

if "SUB_NAME_7" not in gdf.columns:
    raise ValueError("SUB_NAME_7 column not found in shapefile.")

# Normalise to uppercase for matching
gdf["SUB_NAME_7_UP"] = gdf["SUB_NAME_7"].str.upper()

gdf_sel = gdf[gdf["SUB_NAME_7_UP"].isin(TARGET_SUBREGIONS)]

print(f"Selected {len(gdf_sel)} polygons from {len(gdf)} total.")

# ----------------------------------------------------
# SAVE
# ----------------------------------------------------

gdf_sel.to_file(OUTPUT_SHP)
print(f"Saved SWWA IBRA7 shapefile to: {OUTPUT_SHP}")
