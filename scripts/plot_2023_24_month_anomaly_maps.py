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

varinfo = {
    "precip": {
        "title": "Rainfall (mm)",
        "path": os.path.join(base_dir, "..", "outputs_maps", "swwa_precip_anom_2023_2024.nc"),
        "var": "precip",
        "vmin": -150,
        "vmax": 150,
        "cmap": "RdBu"
    },
    "tmax": {
        "title": "Tmax (C)",
        "path": os.path.join(base_dir, "..", "outputs_maps", "swwa_tmax_anom_2023_2024.nc"),
        "var": "tmax",
        "vmin": -6,
        "vmax": 6,
        "cmap": "RdBu_r"
    },
    "tmin": {
        "title": "Tmin (C)",
        "path": os.path.join(base_dir, "..", "outputs_maps", "swwa_tmin_anom_2023_2024.nc"),
        "var": "tmin",
        "vmin": -6,
        "vmax": 6,
        "cmap": "RdBu_r"
    },
    "vpd15": {
        "title": "VPD15 (kPa)",
        "path": os.path.join(base_dir, "..", "outputs_maps", "swwa_vpd15_anom_2023_2024.nc"),
        "var": "vpd15",
        "vmin": -4,
        "vmax": 4,
        "cmap": "RdBu"
    }
}

# ---------------------------------------------------------
# VARIABLES (rows)
# ---------------------------------------------------------

active_vars = ["precip", "tmax", "tmin", "vpd15"]

# ---------------------------------------------------------
# MONTH RANGE (columns)
# ---------------------------------------------------------

start_year = 2023
start_month = 7
end_year = 2024
end_month = 6

months = []
y = start_year
m = start_month
while (y < end_year) or (y == end_year and m <= end_month):
    months.append((y, m))
    m += 1
    if m > 12:
        m = 1
        y += 1

# Short month labels
month_short = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ---------------------------------------------------------
# LOAD REGION + MASK
# ---------------------------------------------------------

region_shp = os.path.join(base_dir, "..", "mask", "ibra7_swwa_mask_clean.shp")
mask_file = os.path.join(base_dir, "..", "mask", "awap_landmask.nc")

region = gpd.read_file(region_shp).to_crs("EPSG:4326")

mask_ds = xr.open_dataset(mask_file)
mask = mask_ds["landmask"]

rename_dict = {}
if "longitude" in mask.coords:
    rename_dict["longitude"] = "lon"
if "latitude" in mask.coords:
    rename_dict["latitude"] = "lat"
if rename_dict:
    mask = mask.rename(rename_dict)

# ---------------------------------------------------------
# FIGURE SETUP
# ---------------------------------------------------------

nrows = len(active_vars)
ncols = len(months)

fig, axes = plt.subplots(
    nrows, ncols,
    figsize=(1.45 * ncols, 2.6 * nrows),
    subplot_kw={"projection": ccrs.PlateCarree()}
)

axes = np.array(axes)

# ---------------------------------------------------------
# LOOP OVER VARIABLES × MONTHS
# ---------------------------------------------------------

for i, key in enumerate(active_vars):

    cfg = varinfo[key]

    for j, (year, month) in enumerate(months):

        ax = axes[i, j]

        ds = xr.open_dataset(cfg["path"])

        rename_dict = {}
        if "longitude" in ds.coords:
            rename_dict["longitude"] = "lon"
        if "latitude" in ds.coords:
            rename_dict["latitude"] = "lat"
        if rename_dict:
            ds = ds.rename(rename_dict)

        data = ds[cfg["var"]]

        subset = data.sel(
            time=(data.time.dt.year == year) &
                 (data.time.dt.month == month)
        ).squeeze()

        mask_interp = mask.interp_like(subset)
        subset = subset.where(mask_interp > 0.5)

        cf = ax.contourf(
            subset.lon,
            subset.lat,
            subset,
            levels=np.linspace(cfg["vmin"], cfg["vmax"], 41),
            cmap=cfg["cmap"],
            vmin=cfg["vmin"],
            vmax=cfg["vmax"],
            extend="both"
        )

        ax.set_extent([114.5, 120.0, -35.5, -28.6])

        ax.add_feature(cfeature.COASTLINE, edgecolor="0.4", linewidth=0.45)
        region.plot(ax=ax, facecolor="none", edgecolor="0.3",
                    linewidth=0.6, transform=ccrs.PlateCarree())

        # Thin box around each map
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(0.4)
            spine.set_edgecolor("0.3")

        # Remove ALL ticks and labels
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        # Row labels (variables)
        if j == 0:
            ax.set_ylabel(cfg["title"], fontsize=20)

        # Column labels (short month names)
        if i == 0:
            ax.set_title(month_short[month-1], fontsize=20)

# ---------------------------------------------------------
# YEAR LABELS ABOVE MONTH BLOCKS (centered between months)
# ---------------------------------------------------------

# Figure margins
left = 0.055
right = 0.998
usable_width = right - left
col_width = usable_width / ncols

# Midpoints:
# 2023 block: Jul(0)–Dec(5) → midpoint between Sep(2) & Oct(3) = 2.5
# 2024 block: Jan(6)–Jun(11) → midpoint between Mar(8) & Apr(9) = 8.5
mid_2023 = left + col_width * 2.5
mid_2024 = left + col_width * 8.5

# Raise the labels slightly above previous placement
year_label_y = 0.985   # was 0.975

fig.text(mid_2023, year_label_y, "2023", ha="center", fontsize=22)
fig.text(mid_2024, year_label_y, "2024", ha="center", fontsize=22)

# Vertical separator between Dec (5) and Jan (6)
sep_x = left + col_width * 6
fig.text(sep_x, 0.95, "|", ha="center", va="bottom", fontsize=32)

# ---------------------------------------------------------

plt.subplots_adjust(
    left=0.055,
    right=0.998,
    top=0.94,
    bottom=0.14,
    wspace=0.0,
    hspace=0.11
)

# ---------------------------------------------------------
# COLORBARS (Rainfall | Temperature | VPD)
# ---------------------------------------------------------

cbar_height = 0.02
cbar_y = 0.06

rain_ax = fig.add_axes([0.10, cbar_y, 0.25, cbar_height])
temp_ax = fig.add_axes([0.40, cbar_y, 0.25, cbar_height])
vpd_ax  = fig.add_axes([0.70, cbar_y, 0.25, cbar_height])

# Rainfall
rain_cfg = varinfo["precip"]
rain_norm = plt.Normalize(rain_cfg["vmin"], rain_cfg["vmax"])
rain_cmap = plt.cm.get_cmap(rain_cfg["cmap"])
cb1 = plt.colorbar(
    plt.cm.ScalarMappable(norm=rain_norm, cmap=rain_cmap),
    cax=rain_ax,
    orientation="horizontal"
)
cb1.set_label("Rainfall anomaly (mm)", fontsize=14)
cb1.ax.tick_params(labelsize=12)

# Temperature
temp_norm = plt.Normalize(-6, 6)
temp_cmap = plt.cm.get_cmap("RdBu_r")
cb2 = plt.colorbar(
    plt.cm.ScalarMappable(norm=temp_norm, cmap=temp_cmap),
    cax=temp_ax,
    orientation="horizontal"
)
cb2.set_label("Temperature anomaly (C)", fontsize=14)
cb2.ax.tick_params(labelsize=12)

# VPD
vpd_cfg = varinfo["vpd15"]
vpd_norm = plt.Normalize(vpd_cfg["vmin"], vpd_cfg["vmax"])
vpd_cmap = plt.cm.get_cmap(vpd_cfg["cmap"])
cb3 = plt.colorbar(
    plt.cm.ScalarMappable(norm=vpd_norm, cmap=vpd_cmap),
    cax=vpd_ax,
    orientation="horizontal"
)
cb3.set_label("VPD anomaly (kPa)", fontsize=14)
cb3.ax.tick_params(labelsize=12)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

outfile = os.path.join(
    base_dir, "..", "figs",
    f"2023_2024_month_anomaly_maps.png"
)

print("Saving figure to:", outfile)

plt.savefig(outfile, dpi=300, bbox_inches="tight")
plt.close()

print("Done. Output file:", outfile)

