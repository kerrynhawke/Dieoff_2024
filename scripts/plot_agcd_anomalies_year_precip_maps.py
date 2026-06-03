#!/usr/bin/env python3
import xarray as xr
import matplotlib.pyplot as plt
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import os
import calendar

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

base_dir = os.path.dirname(__file__)

anom_file = os.path.join(
    base_dir, "..", "outputs_maps",
    "swwa_precip_anom_2023_2024.nc"
)

shp_file = os.path.join(
    base_dir, "..", "mask",
    "ibra7_swwa_mask_clean.shp"
)

fig_dir = os.path.join(base_dir, "..", "figs")
os.makedirs(fig_dir, exist_ok=True)

plot_year  = 2024
plot_month = 3   # March

vmin = -150
vmax = 150
levels = np.linspace(vmin, vmax, 61)

variable = "precip"
panel_label = "a"

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

print("Loading anomaly data...")
ds = xr.open_dataset(anom_file)
data = ds[variable]

subset = data.sel(
    time=(data.time.dt.year == plot_year) &
         (data.time.dt.month == plot_month)
).squeeze()

print(f"Plotting: {plot_year}-{plot_month:02d}")

# ---------------------------------------------------------
# LOAD SHAPEFILE
# ---------------------------------------------------------

print("Loading shapefile...")
region = gpd.read_file(shp_file)

if region.crs is not None:
    region = region.to_crs("EPSG:4326")

# ---------------------------------------------------------
# PLOT
# ---------------------------------------------------------

fig = plt.figure(figsize=(6, 5))
ax = plt.axes(projection=ccrs.PlateCarree())

# ✅ Domain
ax.set_extent([114.5, 120.0, -35.5, -28.6])

# ✅ Data
cf = ax.contourf(
    subset.lon,
    subset.lat,
    subset,
    levels=levels,
    cmap="RdBu",
    extend="both",
    zorder=0
)

# ✅ Coastline
ax.add_feature(
    cfeature.COASTLINE,
    edgecolor="0.5",
    linewidth=0.8,
    zorder=1
)

# ✅ SWWA boundary
region.plot(
    ax=ax,
    facecolor="none",
    edgecolor="0.3",
    linewidth=1.5,
    transform=ccrs.PlateCarree(),
    zorder=2
)

# ---------------------------------------------------------
# ✅ TICKS (remove first labels only)
# ---------------------------------------------------------

xticks = np.arange(114.5, 120.1, 1.0)
yticks = np.arange(-35.5, -28.5, 1.0)

ax.set_xticks(xticks, crs=ccrs.PlateCarree())
ax.set_yticks(yticks, crs=ccrs.PlateCarree())

# ✅ Blank first label only
xlabels = [f"{x:.1f}" if i != 0 else "" for i, x in enumerate(xticks)]
ylabels = [f"{y:.1f}" if i != 0 else "" for i, y in enumerate(yticks)]

ax.set_xticklabels(xlabels)
ax.set_yticklabels(ylabels)

ax.tick_params(
    axis="both",
    labelsize=8,
    top=False,
    right=False
)

# ---------------------------------------------------------
# ✅ PANEL LABEL
# ---------------------------------------------------------

month_name = calendar.month_abbr[plot_month]

ax.text(
    0.01, 1.02,
    f"({panel_label}) {month_name} {plot_year}",
    transform=ax.transAxes,
    ha="left",
    va="bottom",
    fontsize=12,
    fontweight="bold"
)

# ---------------------------------------------------------
# COLORBAR
# ---------------------------------------------------------

cbar = plt.colorbar(cf, ax=ax, orientation="vertical", pad=0.02)
cbar.set_label("Precip anomaly (mm)")

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

outfile = os.path.join(
    fig_dir,
    f"SWWA_precip_anom_{plot_year}_{plot_month:02d}_map.png"
)

print("Saving figure to:", outfile)

if os.path.exists(outfile):
    os.remove(outfile)

plt.savefig(outfile, dpi=300, bbox_inches="tight")
plt.close()

print(f"✅ Saved → {outfile}")
