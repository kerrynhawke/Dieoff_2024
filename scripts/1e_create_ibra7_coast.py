#!/usr/bin/env python3
import geopandas as gpd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

base_dir = os.path.dirname(__file__)

input_shp = os.path.join(
    base_dir, "..", "mask", "ibra7_subregions.shp"
)

output_shp = os.path.join(
    base_dir, "..", "mask", "ibra7_swwa_coast.shp"
)

fig_dir = os.path.join(base_dir, "..", "figs")
os.makedirs(fig_dir, exist_ok=True)

output_fig = os.path.join(
    fig_dir, "SWWA_ibra7_coast_check.png"
)

# how many main landmasses to keep
N_LARGEST = 2   # try 1 if you want only mainland

# ---------------------------------------------------------
# LOAD
# ---------------------------------------------------------

print("Loading IBRA subregions...")
regions = gpd.read_file(input_shp)

if regions.crs is not None:
    regions = regions.to_crs("EPSG:4326")

# ---------------------------------------------------------
# DISSOLVE
# ---------------------------------------------------------

print("Dissolving regions...")
regions["dissolve"] = 1
merged = regions.dissolve(by="dissolve")

# ---------------------------------------------------------
# SPLIT INTO POLYGONS
# ---------------------------------------------------------

print("Exploding into individual polygons...")
polys = merged.explode(index_parts=False).reset_index(drop=True)

# ---------------------------------------------------------
# FILTER LARGEST POLYGONS
# ---------------------------------------------------------

print("Selecting largest polygons...")

# IMPORTANT: compute area in projected CRS for accuracy
polys_proj = polys.to_crs("EPSG:3577")  # Australian Albers

polys["area"] = polys_proj.area

# sort largest first
polys = polys.sort_values("area", ascending=False)

# keep N largest
polys_main = polys.head(N_LARGEST)

print(f"Keeping {len(polys_main)} largest polygons")

# drop area column
polys_main = polys_main.drop(columns="area")

# merge them back
main_geom = polys_main.union_all()

main = gpd.GeoDataFrame(geometry=[main_geom], crs="EPSG:4326")

# ---------------------------------------------------------
# EXTRACT BOUNDARY
# ---------------------------------------------------------

print("Extracting clean outer boundary...")
boundary = main.boundary

coast = gpd.GeoDataFrame(geometry=boundary, crs=main.crs)

# ---------------------------------------------------------
# SAVE SHAPEFILE
# ---------------------------------------------------------

print(f"Saving coastline shapefile → {output_shp}")

coast.to_file(output_shp)

# ---------------------------------------------------------
# ✅ CHECK PLOT
# ---------------------------------------------------------

print("Creating check plot...")

fig, ax = plt.subplots(figsize=(6, 6))

# all polygons (faint)
polys.plot(ax=ax, facecolor="none", edgecolor="lightgray", linewidth=0.5)

# kept polygons
polys_main.plot(ax=ax, facecolor="lightblue", edgecolor="blue")

# final coastline
coast.plot(ax=ax, edgecolor="black", linewidth=2)

ax.set_title("Cleaned SWWA Coastline")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

plt.tight_layout()
plt.savefig(output_fig, dpi=300)
plt.close()

print(f"✅ Figure saved → {output_fig}")
print("\n✅ Done — cleaned coastline created!")

