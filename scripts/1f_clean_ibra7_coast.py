#!/usr/bin/env python3
import geopandas as gpd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

base_dir = os.path.dirname(__file__)

input_shp = os.path.join(
    base_dir, "..", "mask", "ibra7_swwa_coast.shp"
)

output_shp = os.path.join(
    base_dir, "..", "mask", "ibra7_swwa_coast_clean.shp"
)

fig_dir = os.path.join(base_dir, "..", "figs")
os.makedirs(fig_dir, exist_ok=True)

output_fig = os.path.join(
    fig_dir, "SWWA_ibra7_coast_check.png"
)

# ✅ buffer distance NOW IN METRES
SMOOTH_DISTANCE = 5000   # 5 km

# ---------------------------------------------------------
# LOAD
# ---------------------------------------------------------

print("Loading original coastline...")
coast = gpd.read_file(input_shp)

# ---------------------------------------------------------
# PROJECT TO METRIC CRS (CRITICAL)
# ---------------------------------------------------------

print("Projecting to EPSG:3577...")
coast_proj = coast.to_crs("EPSG:3577")

# ---------------------------------------------------------
# CLEAN GEOMETRY
# ---------------------------------------------------------

print("Cleaning geometry...")

coast_proj["dissolve"] = 1
coast_proj = coast_proj.dissolve(by="dissolve")

# ✅ buffer in METRES (fast and correct now)
coast_proj["geometry"] = (
    coast_proj.buffer(SMOOTH_DISTANCE)
              .buffer(-SMOOTH_DISTANCE)
)

# ---------------------------------------------------------
# REMOVE SMALL FRAGMENTS
# ---------------------------------------------------------

print("Removing small fragments...")

parts = coast_proj.explode(index_parts=False).reset_index(drop=True)

parts["area_km2"] = parts.area / 1e6

parts = parts.sort_values("area_km2", ascending=False)

main = parts.head(1)

# ---------------------------------------------------------
# REPROJECT BACK
# ---------------------------------------------------------

print("Reprojecting back to EPSG:4326...")
main = main.to_crs("EPSG:4326")

# ---------------------------------------------------------
# EXTRACT BOUNDARY
# ---------------------------------------------------------

print("Extracting boundary...")
boundary = main.boundary

clean_coast = gpd.GeoDataFrame(
    geometry=boundary,
    crs="EPSG:4326"
)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

print(f"Saving cleaned coastline → {output_shp}")

if os.path.exists(output_shp):
    print("Overwriting existing cleaned shapefile")

clean_coast.to_file(output_shp)

# ---------------------------------------------------------
# CHECK PLOT
# ---------------------------------------------------------

print("Creating plot...")

fig, ax = plt.subplots(figsize=(6, 6))

# original (light grey)
coast.plot(ax=ax, edgecolor="lightgray", linewidth=1)

# cleaned (black)
clean_coast.plot(ax=ax, edgecolor="black", linewidth=2)

ax.set_title("Cleaned SWWA Coastline")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

plt.tight_layout()
plt.savefig(output_fig, dpi=300)
plt.close()

print(f"✅ Figure saved → {output_fig}")
print("\n✅ Done")
