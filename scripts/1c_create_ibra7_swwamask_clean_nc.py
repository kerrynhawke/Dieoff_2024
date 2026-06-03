#!/usr/bin/env python3
import geopandas as gpd
import xarray as xr
import numpy as np
from rasterio import features
from affine import Affine
import os

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------

INPUT_SHP = "/mnt/d/data/0_masks/IBRA/SWWA/ibra7_swwa_mask_clean.shp"
OUTPUT_NC = "/mnt/d/data/0_masks/IBRA/SWWA/ibra7_swwa_mask_clean.nc"

RES = 0.01   # keep your high resolution

# ----------------------------------------------------
# LOAD SHAPEFILE
# ----------------------------------------------------

print("Loading shapefile...")
gdf = gpd.read_file(INPUT_SHP).to_crs(4326)
print("Shapefile loaded.")

minx, miny, maxx, maxy = gdf.total_bounds
print(f"Bounding box: {minx:.3f}, {miny:.3f}, {maxx:.3f}, {maxy:.3f}")

# ----------------------------------------------------
# CREATE GRID
# ----------------------------------------------------

print("Creating grid...")
lons = np.arange(minx, maxx + RES, RES)
lats = np.arange(maxy, miny - RES, -RES)  # descending for rasterio

height = len(lats)
width = len(lons)
print(f"Grid size: {height} × {width}")

# ----------------------------------------------------
# BUILD AFFINE TRANSFORM
# ----------------------------------------------------

transform = Affine.translation(minx, maxy) * Affine.scale(RES, -RES)

# ----------------------------------------------------
# RASTERIZE
# ----------------------------------------------------

print("Rasterizing mask...")
shapes = [(geom, 1) for geom in gdf.geometry]

mask = features.rasterize(
    shapes=shapes,
    out_shape=(height, width),
    transform=transform,
    fill=0,
    dtype="int8"
)

print("Rasterization complete.")

# ----------------------------------------------------
# SAVE NETCDF (ERA5‑compatible coordinate names)
# ----------------------------------------------------

print("Saving NetCDF...")

ds = xr.Dataset(
    {"mask": (("latitude", "longitude"), mask)},
    coords={"latitude": lats, "longitude": lons},
)

ds["mask"].attrs["description"] = "SWWA mask on native-resolution grid (1=inside, 0=outside)"
ds.attrs["source_shapefile"] = INPUT_SHP

ds.to_netcdf(OUTPUT_NC)
print(f"Saved native-grid SWWA mask to: {OUTPUT_NC}")
