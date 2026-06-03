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

temp_monthly_file = "mask_month_means_agcd_tmax_1910_2024.nc"
temp_clim_file    = "mask_monclim_agcd_tmax_1971_2000.nc"

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

rain_years = rain_mnth["year"].values

rain_total = rain_mnth.sum(dim="month").values
rain_clim_total = rain_clim_mnth.sum().values

rain_anom = rain_total - rain_clim_total
rain_colors = ["blue" if v >= 0 else "red" for v in rain_anom]
rain_rm = pd.Series(rain_anom).rolling(10, center=True).mean()

# ---------------------------------------------------------
# LOAD TEMP
# ---------------------------------------------------------
print("Loading temperature...")

temp_ds   = xr.open_dataset(os.path.join(input_dir, temp_monthly_file))
temp_clim = xr.open_dataset(os.path.join(input_dir, temp_clim_file))

temp = temp_ds["tmax"]
temp_clim_var = temp_clim["tmax"]

temp_mnth = temp.mean(dim=("lat", "lon"))
temp_clim_mnth = temp_clim_var.mean(dim=("lat", "lon"))

temp_years = temp_mnth["year"].values

temp_annual = temp_mnth.mean(dim="month").values
temp_clim_annual = temp_clim_mnth.mean().values

temp_anom = temp_annual - temp_clim_annual
temp_rm = pd.Series(temp_anom).rolling(10, center=True).mean()

# ---------------------------------------------------------
# ALIGN TO RAINFALL YEARS (1900–2024)
# ---------------------------------------------------------
years = rain_years

# Create full arrays
temp_anom_full = np.full(len(years), np.nan)
temp_rm_full   = np.full(len(years), np.nan)
temp_colors_full = ["gray"] * len(years)

# Find insertion index
start_idx = np.where(years == temp_years[0])[0][0]

# Fill arrays
temp_anom_full[start_idx:] = temp_anom
temp_rm_full[start_idx:]   = temp_rm

for i in range(start_idx, len(years)):
    temp_colors_full[i] = "red" if temp_anom_full[i] >= 0 else "blue"

# ---------------------------------------------------------
# PLOT
# ---------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(15, 10), sharex=True,
    gridspec_kw={"height_ratios": [1, 1]}
)

label_fs = 18
tick_fs  = 14

# -----------------------------
# RAINFALL PANEL
# -----------------------------
ax1.bar(years, rain_anom, color=rain_colors)
ax1.plot(years, rain_rm, color="black", linewidth=2)
ax1.axhline(0, color="gray", linewidth=1)

ax1.set_ylabel("Rainfall anomaly (mm)", fontsize=label_fs)
ax1.tick_params(axis="y", labelsize=tick_fs)
ax1.tick_params(axis="x", which="both", bottom=False, labelbottom=False)

# -----------------------------
# TEMPERATURE PANEL
# -----------------------------
ax2.bar(years, temp_anom_full, color=temp_colors_full)
ax2.plot(years, temp_rm_full, color="black", linewidth=2)
ax2.axhline(0, color="gray", linewidth=1)

ax2.set_ylabel("Temperature anomaly (°C)", fontsize=label_fs)
ax2.set_xlabel("Year", fontsize=label_fs, labelpad=15)
ax2.tick_params(axis="y", labelsize=tick_fs)

# Optional: mark missing early period
ax2.text(years[2], np.nanmax(temp_anom_full)*0.8,
         "No tmax data before 1910", fontsize=10, color="gray")

# ---------------------------------------------------------
# X-TICKS (every 5 years labelled)
# ---------------------------------------------------------
ax2.set_xticks(years)
ax2.set_xticklabels(
    [str(y) if y % 5 == 0 else "" for y in years],
    fontsize=tick_fs,
    rotation=90,
    ha="center"
)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
fig.suptitle("SWWA Climate Anomalies (AGCD)", fontsize=20)

plt.tight_layout()

plt.tight_layout()
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
outfile = os.path.join(output_dir, "SWWA_rain_temp_anomaly_AGCD.png")

plt.savefig(outfile, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved → {outfile}")
