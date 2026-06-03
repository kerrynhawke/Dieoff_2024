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

tmean_monthly_file = "mask_month_means_agcd_tmean_1910_2024.nc"
tmean_clim_file    = "mask_monclim_agcd_tmean_1971_2000.nc"

tmin_monthly_file = "mask_month_means_agcd_tmin_1910_2024.nc"
tmin_clim_file    = "mask_monclim_agcd_tmin_1971_2000.nc"

vpd_monthly_file  = "mask_month_means_agcd_vpd15_1971_2024.nc"
vpd_clim_file     = "mask_monclim_agcd_vpd15_1971_2000.nc"

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
# GENERIC FUNCTION
# ---------------------------------------------------------
def process_variable(ds_file, clim_file, var_name):
    ds   = xr.open_dataset(os.path.join(input_dir, ds_file))
    clim = xr.open_dataset(os.path.join(input_dir, clim_file))

    data = ds[var_name]
    clim_data = clim[var_name]

    mnth = data.mean(dim=("lat", "lon"))
    clim_mnth = clim_data.mean(dim=("lat", "lon"))

    var_years = mnth["year"].values

    annual = mnth.mean(dim="month").values
    clim_annual = clim_mnth.mean().values

    anom = annual - clim_annual
    rm = pd.Series(anom).rolling(10, center=True).mean()

    anom_full = np.full(len(years), np.nan)
    rm_full   = np.full(len(years), np.nan)
    colors_full = ["gray"] * len(years)

    start_idx = np.where(years == var_years[0])[0][0]

    anom_full[start_idx:] = anom
    rm_full[start_idx:]   = rm

    for i in range(start_idx, len(years)):
        colors_full[i] = "red" if anom_full[i] >= 0 else "blue"

    return anom_full, rm_full, colors_full

# ---------------------------------------------------------
# LOAD VARIABLES
# ---------------------------------------------------------
print("Loading tmax...")
tmax_anom, tmax_rm, tmax_colors = process_variable(
    tmax_monthly_file, tmax_clim_file, "tmax"
)

print("Loading tmean...")
tmean_anom, tmean_rm, tmean_colors = process_variable(
    tmean_monthly_file, tmean_clim_file, "tmean"
)

print("Loading tmin...")
tmin_anom, tmin_rm, tmin_colors = process_variable(
    tmin_monthly_file, tmin_clim_file, "tmin"
)

print("Loading VPD...")
vpd_anom, vpd_rm, vpd_colors = process_variable(
    vpd_monthly_file, vpd_clim_file, "vpd"
)

# ---------------------------------------------------------
# PLOT (5 PANELS)
# ---------------------------------------------------------
fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(
    5, 1, figsize=(15, 16), sharex=True
)

label_fs = 18
tick_fs  = 14

# ----------------------------- RAIN
ax1.bar(years, rain_anom, color=rain_colors)
ax1.plot(years, rain_rm, color="black", linewidth=2)
ax1.axhline(0, color="gray")
ax1.set_ylabel("Rainfall (mm)", fontsize=label_fs)
ax1.tick_params(axis="x", bottom=False, labelbottom=False)

# ----------------------------- TMAX
ax2.bar(years, tmax_anom, color=tmax_colors)
ax2.plot(years, tmax_rm, color="black", linewidth=2)
ax2.axhline(0, color="gray")
ax2.set_ylabel("Tmax (°C)", fontsize=label_fs)
ax2.tick_params(axis="x", bottom=False, labelbottom=False)

# ----------------------------- TMEAN ✅
ax3.bar(years, tmean_anom, color=tmean_colors)
ax3.plot(years, tmean_rm, color="black", linewidth=2)
ax3.axhline(0, color="gray")
ax3.set_ylabel("Tmean (°C)", fontsize=label_fs)
ax3.tick_params(axis="x", bottom=False, labelbottom=False)

# ----------------------------- TMIN
ax4.bar(years, tmin_anom, color=tmin_colors)
ax4.plot(years, tmin_rm, color="black", linewidth=2)
ax4.axhline(0, color="gray")
ax4.set_ylabel("Tmin (°C)", fontsize=label_fs)
ax4.tick_params(axis="x", bottom=False, labelbottom=False)

# ----------------------------- VPD
ax5.bar(years, vpd_anom, color=vpd_colors)
ax5.plot(years, vpd_rm, color="black", linewidth=2)
ax5.axhline(0, color="gray")
ax5.set_ylabel("VPD (kPa, 3pm)", fontsize=label_fs)
ax5.set_xlabel("Year", fontsize=label_fs, labelpad=20)

# X-axis
ax5.set_xticks(years)
ax5.set_xticklabels(
    [str(y) if y % 5 == 0 else "" for y in years],
    fontsize=tick_fs,
    rotation=90
)

# ---------------------------------------------------------
# TITLE + NOTE
# ---------------------------------------------------------
fig.suptitle("SWWA Climate Anomalies (AGCD)", fontsize=20)

plt.tight_layout()
plt.subplots_adjust(bottom=0.18)

plt.figtext(
    0.98, -0.50,
    "Based on a 30-year climatology (1971–2000)",
    transform=ax5.transAxes,
    ha="right",
    va="top",
    fontsize=12
)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
outfile = os.path.join(output_dir, "SWWA_climate_5panel_anomaly_AGCD.png")

plt.savefig(outfile, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved → {outfile}")
