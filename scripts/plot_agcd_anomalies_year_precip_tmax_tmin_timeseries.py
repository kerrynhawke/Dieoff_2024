#!/usr/bin/env python3
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import pandas as pd
import os

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------
base_dir = os.path.dirname(__file__)

input_dir  = os.path.join(base_dir, "..", "outputs")
output_dir = os.path.join(base_dir, "..", "figs")

os.makedirs(output_dir, exist_ok=True)

# ---------------------------------------------------------
# FILES
# ---------------------------------------------------------
rain_monthly_file = "mask_month_means_agcd_precip_1900_2024.nc"
rain_clim_file    = "mask_monclim_agcd_precip_1971_2000.nc"

tmax_monthly_file = "mask_month_means_agcd_tmax_1910_2024.nc"
tmax_clim_file    = "mask_monclim_agcd_tmax_1971_2000.nc"

tmin_monthly_file = "mask_month_means_agcd_tmin_1910_2024.nc"
tmin_clim_file    = "mask_monclim_agcd_tmin_1971_2000.nc"

# ---------------------------------------------------------
# LOAD RAIN
# ---------------------------------------------------------
print("Loading rainfall...")

rain_ds   = xr.open_dataset(os.path.join(input_dir, rain_monthly_file))
rain_clim = xr.open_dataset(os.path.join(input_dir, rain_clim_file))

rain = rain_ds["precip"]
rain_clim_var = rain_clim["precip"]

rain_mnth = rain.mean(dim=("lat", "lon"))
rain_clim_mnth = rain_clim_var.mean(dim=("lat", "lon"))

years = rain_mnth["year"].values

rain_total = rain_mnth.sum(dim="month").values
rain_clim_total = rain_clim_mnth.sum().values

rain_anom = rain_total - rain_clim_total
rain_colors = ["blue" if v >= 0 else "red" for v in rain_anom]
rain_rm = pd.Series(rain_anom).rolling(10, center=True).mean()

# ---------------------------------------------------------
# FUNCTION TO PROCESS TEMP VARIABLES
# ---------------------------------------------------------
def process_temp(ds_file, clim_file, var_name):
    ds   = xr.open_dataset(os.path.join(input_dir, ds_file))
    clim = xr.open_dataset(os.path.join(input_dir, clim_file))

    data = ds[var_name]
    clim_data = clim[var_name]

    mnth = data.mean(dim=("lat", "lon"))
    clim_mnth = clim_data.mean(dim=("lat", "lon"))

    temp_years = mnth["year"].values

    annual = mnth.mean(dim="month").values
    clim_annual = clim_mnth.mean().values

    anom = annual - clim_annual
    rm = pd.Series(anom).rolling(10, center=True).mean()

    # Align to rainfall years
    anom_full = np.full(len(years), np.nan)
    rm_full   = np.full(len(years), np.nan)
    colors_full = ["gray"] * len(years)

    start_idx = np.where(years == temp_years[0])[0][0]

    anom_full[start_idx:] = anom
    rm_full[start_idx:]   = rm

    for i in range(start_idx, len(years)):
        colors_full[i] = "red" if anom_full[i] >= 0 else "blue"

    return anom_full, rm_full, colors_full


# ---------------------------------------------------------
# LOAD TMAX + TMIN
# ---------------------------------------------------------
print("Loading tmax...")
tmax_anom, tmax_rm, tmax_colors = process_temp(
    tmax_monthly_file, tmax_clim_file, "tmax"
)

print("Loading tmin...")
tmin_anom, tmin_rm, tmin_colors = process_temp(
    tmin_monthly_file, tmin_clim_file, "tmin"
)

# ---------------------------------------------------------
# PLOT (3 PANELS)
# ---------------------------------------------------------
fig, (ax1, ax2, ax3) = plt.subplots(
    3, 1, figsize=(15, 12), sharex=True,
    gridspec_kw={"height_ratios": [1, 1, 1]}
)

label_fs = 18
tick_fs  = 14

# -----------------------------
# PANEL 1 — RAIN
# -----------------------------
ax1.bar(years, rain_anom, color=rain_colors)
ax1.plot(years, rain_rm, color="black", linewidth=2)
ax1.axhline(0, color="gray", linewidth=1)

ax1.set_ylabel("Rainfall anomaly (mm)", fontsize=label_fs)
ax1.tick_params(axis="y", labelsize=tick_fs)
ax1.tick_params(axis="x", which="both", bottom=False, labelbottom=False)

# -----------------------------
# PANEL 2 — TMAX
# -----------------------------
ax2.bar(years, tmax_anom, color=tmax_colors)
ax2.plot(years, tmax_rm, color="black", linewidth=2)
ax2.axhline(0, color="gray", linewidth=1)

ax2.set_ylabel("Tmax anomaly (°C)", fontsize=label_fs)
ax2.tick_params(axis="y", labelsize=tick_fs)
ax2.tick_params(axis="x", which="both", bottom=False, labelbottom=False)

# -----------------------------
# PANEL 3 — TMIN
# -----------------------------
ax3.bar(years, tmin_anom, color=tmin_colors)
ax3.plot(years, tmin_rm, color="black", linewidth=2)
ax3.axhline(0, color="gray", linewidth=1)

ax3.set_ylabel("Tmin anomaly (°C)", fontsize=label_fs)
ax3.set_xlabel("Year", fontsize=label_fs, labelpad=15)
ax3.tick_params(axis="y", labelsize=tick_fs)

# Vertical year labels
ax3.set_xticks(years)
ax3.set_xticklabels(
    [str(y) if y % 5 == 0 else "" for y in years],
    fontsize=tick_fs,
    rotation=90
)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
fig.suptitle("SWWA Climate Anomalies (AGCD)", fontsize=20)

plt.tight_layout()
plt.subplots_adjust(bottom=0.15)

plt.subplots_adjust(bottom=0.15)

plt.figtext(
    0.98, 0.02,
    "Based on a 30-year climatology (1971–2000)",
    ha="right",
    fontsize=12
)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
outfile = os.path.join(output_dir, "SWWA_rain_tmax_tmin_anomaly_AGCD.png")

plt.savefig(outfile, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved → {outfile}")
