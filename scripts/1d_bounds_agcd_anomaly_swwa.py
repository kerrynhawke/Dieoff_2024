#!/usr/bin/env python3
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

base_dir = os.path.dirname(__file__)

shp_file = os.path.join(base_dir, "..", "mask", "ibra7_swwa_mask_clean.shp")

# Output figure
fig_dir = os.path.join(base_dir, "..", "figs")
os.makedirs(fig_dir, exist_ok=True)

outfile = os.path.join(fig_dir, "SWWA_bounds_check.png")

# Buffer (degrees)
buffer = 1.5

# ---------------------------------------------------------
# LOAD SHAPEFILE
# ---------------------------------------------------------

print("Loading shapefile...")
region = gpd.read_file(shp_file)

# Ensure lat/lon CRS
if region.crs is not None:
    region = region.to_crs("EPSG:4326")

print("\nCRS:", region.crs)

# ---------------------------------------------------------
# GET BOUNDS
# ---------------------------------------------------------

lon_min, lat_min, lon_max, lat_max = region.total_bounds

print("\n--- Raw bounds ---")
print(f"lat_min = {lat_min:.2f}, lat_max = {lat_max:.2f}")
print(f"lon_min = {lon_min:.2f}, lon_max = {lon_max:.2f}")

# Apply buffer
lat_min_buf = lat_min - buffer
lat_max_buf = lat_max + buffer
lon_min_buf = lon_min - buffer
lon_max_buf = lon_max + buffer

print("\n--- Buffered bounds ---")
print(f"lat_min = {lat_min_buf:.2f}, lat_max = {lat_max_buf:.2f}")
print(f"lon_min = {lon_min_buf:.2f}, lon_max = {lon_max_buf:.2f}")

# ---------------------------------------------------------
# READY-TO-USE SNIPPET
# ---------------------------------------------------------

print("\n--- Copy/paste into your scripts ---\n")

print(f"lat_min, lat_max = {lat_min_buf:.2f}, {lat_max_buf:.2f}")
print(f"lon_min, lon_max = {lon_min_buf:.2f}, {lon_max_buf:.2f}")

# ---------------------------------------------------------
# PLOT CHECK FIGURE
# ---------------------------------------------------------

print("\nPlotting sanity check figure...")

fig = plt.figure(figsize=(8, 6))
ax = plt.axes(projection=ccrs.PlateCarree())

# Set map extent to buffered box
ax.set_extent([lon_min_buf, lon_max_buf, lat_min_buf, lat_max_buf])

# Add coastline
ax.add_feature(cfeature.COASTLINE, linewidth=1)
ax.add_feature(cfeature.BORDERS, linestyle=":", alpha=0.5)

# Plot shapefile boundary
region.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=1.5,
    transform=ccrs.PlateCarree()
)

# Draw bounding box
ax.plot(
    [lon_min_buf, lon_max_buf, lon_max_buf, lon_min_buf, lon_min_buf],
    [lat_min_buf, lat_min_buf, lat_max_buf, lat_max_buf, lat_min_buf],
    color="red",
    linewidth=2,
    linestyle="--",
    transform=ccrs.PlateCarree(),
    label="Buffered domain"
)

# Gridlines
gl = ax.gridlines(draw_labels=True, linestyle="--", alpha=0.5)
gl.top_labels = False
gl.right_labels = False

# Title
plt.title("SWWA Region and Buffered Domain")

# Save
plt.savefig(outfile, dpi=300, bbox_inches="tight")
plt.close()

print(f"\n✅ Figure saved → {outfile}")
print("\n✅ Done")
