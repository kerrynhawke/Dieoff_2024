#!/usr/bin/env python3
import xarray as xr
import matplotlib.pyplot as plt
import geopandas as gpd
import cartopy.crs as ccrs
import numpy as np
import os
import calendar

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

base_dir = os.path.dirname(__file__)

anom_file = os.path.join(
    base_dir, "..", "outputs_maps",
    "swwa_tmax_anom_2023_2024.nc"
)

region_shp = os.path.join(
    base_dir, "..", "mask",
    "ibra7_swwa_mask_clean.shp"
)

coast_shp = os.path.join(
    base_dir, "..", "mask",
    "ibra7_swwa_coast_clean.shp"
)

fig_dir = os.path.join(base_dir, "..", "figs")
os.makedirs(fig_dir, exist_ok=True)

# ✅ SELECT PERIOD (EDIT THIS)
start_year = 2023
start_month = 4
end_year = 2024
end_month = 7     # July

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

print("Loading anomaly data...")
ds = xr.open_dataset(anom_file)
data = ds["tmax"]

# ---------------------------------------------------------
# BUILD TIME LIST
# ---------------------------------------------------------

print("Building time sequence...")

times = []
y, m = start_year, start_month

while (y < end_year) or (y == end_year and m <= end_month):
    times.append((y, m))
    m += 1
    if m > 12:
        m = 1
        y += 1

nplots = len(times)
print(f"Total panels: {nplots}")

# ---------------------------------------------------------
# LOAD SHAPEFILES
# ---------------------------------------------------------

region = gpd.read_file(region_shp).to_crs("EPSG:4326")
coast  = gpd.read_file(coast_shp).to_crs("EPSG:4326")

# ---------------------------------------------------------
# CREATE FIGURE GRID
# ---------------------------------------------------------

ncols = 4
nrows = int(np.ceil(nplots / ncols))

fig, axes = plt.subplots(
    nrows, ncols,
    figsize=(12, 3*nrows),
    subplot_kw={"projection": ccrs.PlateCarree()}
)

axes = axes.flatten()

# ---------------------------------------------------------
# PLOT LOOP
# ---------------------------------------------------------

for i, (year, month) in enumerate(times):

    ax = axes[i]

    subset = data.sel(
        time=(data.time.dt.year == year) &
             (data.time.dt.month == month)
    ).squeeze()

    # ✅ auto colour scale (per panel)
    vmin = float(subset.min())
    vmax = float(subset.max())
    levels = np.linspace(vmin, vmax, 40)

    # ✅ map extent
    ax.set_extent([114.5, 120.0, -35.5, -28.6])

    # ✅ filled contours
    cf = ax.contourf(
        subset.lon,
        subset.lat,
        subset,
        levels=levels,
        cmap="RdBu",
        extend="both"
    )

    # ✅ coastline
    coast.plot(
        ax=ax,
        edgecolor="0.5",
        linewidth=0.8,
        transform=ccrs.PlateCarree()
    )

    # ✅ region outline
    region.plot(
        ax=ax,
        facecolor="none",
        edgecolor="0.3",
        linewidth=1.2,
        transform=ccrs.PlateCarree()
    )

    # ✅ ticks
    xticks = np.arange(114.5, 120.1, 1.5)
    yticks = np.arange(-35.5, -28.5, 1.5)

    ax.set_xticks(xticks, crs=ccrs.PlateCarree())
    ax.set_yticks(yticks, crs=ccrs.PlateCarree())

    ax.set_xticklabels([f"{x:.1f}" if i != 0 else "" for i, x in enumerate(xticks)])
    ax.set_yticklabels([f"{y:.1f}" if i != 0 else "" for i, y in enumerate(yticks)])

    ax.tick_params(labelsize=6, top=False, right=False)

    # ✅ panel label (a, b, c...)
    label = chr(97 + i)
    month_name = calendar.month_abbr[month]

    ax.text(
        0.01, 1.02,
        f"({label}) {month_name} {year}",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        fontweight="bold"
    )

    # ✅ individual colorbar
    cbar = plt.colorbar(cf, ax=ax, orientation="vertical", pad=0.01)
    cbar.ax.tick_params(labelsize=6)

# ---------------------------------------------------------
# REMOVE UNUSED AXES
# ---------------------------------------------------------

for j in range(nplots, len(axes)):
    fig.delaxes(axes[j])

# ---------------------------------------------------------
# FINAL LAYOUT
# ---------------------------------------------------------

plt.tight_layout()

outfile = os.path.join(fig_dir, "SWWA_tmax_panel_maps_noscale.png")

plt.savefig(outfile, dpi=300)
plt.close()

print(f"✅ Saved → {outfile}")
