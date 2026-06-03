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
    "swwa_tmin_anom_2023_2024.nc"
)

region_shp = os.path.join(
    base_dir, "..", "mask",
    "ibra7_swwa_mask_clean.shp"
)

mask_file = os.path.join(
    base_dir, "..", "mask",
    "awap_landmask.nc"
)

fig_dir = os.path.join(base_dir, "..", "figs")
os.makedirs(fig_dir, exist_ok=True)

# ✅ PERIOD
start_year = 2023
start_month = 4
end_year = 2024
end_month = 7

# ✅ COLOUR SCALE
vmin = -4
vmax = 4
levels = np.linspace(vmin, vmax, 51)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

print("Loading anomaly data...")
ds = xr.open_dataset(anom_file)
data = ds["tmin"]

# ---------------------------------------------------------
# LOAD AND FIX MASK
# ---------------------------------------------------------

print("Loading AWAP land mask...")
mask_ds = xr.open_dataset(mask_file)

mask = mask_ds["landmask"]

print("Original mask shape:", mask.shape)

# ✅ rename coords
mask = mask.rename({
    "latitude": "lat",
    "longitude": "lon"
})

# ✅ interpolate to data grid
mask = mask.interp_like(data)

# ✅ CRITICAL FIX: threshold after interpolation
mask = mask > 0.5

print("Aligned mask shape:", mask.shape)
print("Land fraction:", mask.mean().values)

# ---------------------------------------------------------
# BUILD TIME LIST
# ---------------------------------------------------------

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
# LOAD REGION
# ---------------------------------------------------------

region = gpd.read_file(region_shp).to_crs("EPSG:4326")

# ---------------------------------------------------------
# CREATE GRID
# ---------------------------------------------------------

ncols = 4
nrows = int(np.ceil(nplots / ncols))

fig, axes = plt.subplots(
    nrows, ncols,
    figsize=(8.5, 3*nrows),
    subplot_kw={"projection": ccrs.PlateCarree()}
)

axes = axes.flatten()

# ---------------------------------------------------------
# PLOTTING LOOP
# ---------------------------------------------------------

for i, (year, month) in enumerate(times):

    print(f"Plotting {year}-{month:02d}")

    ax = axes[i]

    subset = data.sel(
        time=(data.time.dt.year == year) &
             (data.time.dt.month == month)
    ).squeeze()

    # ✅ APPLY LAND MASK
    subset = subset.where(mask)

    # ✅ DOMAIN
    ax.set_extent([114.5, 120.0, -35.5, -28.6])

    # ✅ DATA
    cf = ax.contourf(
        subset.lon,
        subset.lat,
        subset,
        levels=levels,
        cmap="RdBu_r",
        vmin=vmin,
        vmax=vmax,
        extend="both",
        zorder=0
    )

    # ✅ COASTLINE
    ax.add_feature(
        cfeature.COASTLINE,
        edgecolor="0.5",
        linewidth=0.8,
        zorder=1
    )

    # ✅ REGION
    region.plot(
        ax=ax,
        facecolor="none",
        edgecolor="0.3",
        linewidth=1.2,
        transform=ccrs.PlateCarree(),
        zorder=2
    )

    # -----------------------------------------------------
    # TICKS
    # -----------------------------------------------------

    xticks = np.arange(114.5, 120.1, 1.5)
    yticks = np.arange(-35.5, -28.5, 1.5)

    ax.set_xticks(xticks, crs=ccrs.PlateCarree())
    ax.set_yticks(yticks, crs=ccrs.PlateCarree())

    row = i // ncols
    col = i % ncols

    if row == nrows - 1:
        ax.set_xticklabels(
            [f"{x:.1f}" if j != 0 else "" for j, x in enumerate(xticks)],
            fontsize=7
        )
        ax.tick_params(axis="x", bottom=True)
    else:
        ax.set_xticklabels([])
        ax.tick_params(axis="x", bottom=False)

    if col == 0:
        ax.set_yticklabels(
            [f"{y:.1f}" if j != 0 else "" for j, y in enumerate(yticks)],
            fontsize=7
        )
        ax.tick_params(axis="y", left=True)
    else:
        ax.set_yticklabels([])
        ax.tick_params(axis="y", left=False)

    ax.tick_params(top=False, right=False)

    # ✅ PANEL LABEL
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

# ---------------------------------------------------------
# REMOVE EMPTY PANELS
# ---------------------------------------------------------

for j in range(nplots, len(axes)):
    fig.delaxes(axes[j])

# ---------------------------------------------------------
# LAYOUT
# ---------------------------------------------------------

fig.subplots_adjust(
    left=0.05,
    right=0.98,
    top=0.97,
    bottom=0.12,
    wspace=0.01,
    hspace=0.15
)

# ---------------------------------------------------------
# COLORBAR
# ---------------------------------------------------------

cbar_ax = fig.add_axes([0.25, 0.04, 0.5, 0.015])

cbar = fig.colorbar(
    cf,
    cax=cbar_ax,
    orientation="horizontal",
    extend="both"
)

ticks = np.arange(-6, 6, 0.5)
cbar.set_ticks(ticks)
cbar.set_ticklabels([f"{t:g}" for t in ticks])

cbar.set_label("Tmax anomaly (mm)", fontsize=10)
cbar.ax.tick_params(labelsize=8, length=3)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

outfile = os.path.join(fig_dir, "SWWA_tmin_panel_maps_landonly.png")

print("Saving figure to:", outfile)

if os.path.exists(outfile):
    os.remove(outfile)

plt.savefig(outfile, dpi=300)
plt.close()

print(f"✅ Saved → {outfile}")
