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
# ✅ SELECT VARIABLES
# ---------------------------------------------------------
variables_to_plot = [
    "precip",
    "tmax",
    "tmean",
    "tmin",
    "vpd"
]

# ---------------------------------------------------------
# FILE MAP
# ---------------------------------------------------------
files = {
    "precip": {
        "monthly": "mask_month_means_agcd_precip_1900_2024.nc",
        "clim":    "mask_monclim_agcd_precip_1971_2000.nc",
        "var":     "precip",
        "ylabel":  "Rainfall (mm)"
    },
    "tmax": {
        "monthly": "mask_month_means_agcd_tmax_1910_2024.nc",
        "clim":    "mask_monclim_agcd_tmax_1971_2000.nc",
        "var":     "tmax",
        "ylabel":  "Tmax (°C)"
    },
    "tmean": {
        "monthly": "mask_month_means_agcd_tmean_1910_2024.nc",
        "clim":    "mask_monclim_agcd_tmean_1971_2000.nc",
        "var":     "tmean",
        "ylabel":  "Tmean (°C)"
    },
    "tmin": {
        "monthly": "mask_month_means_agcd_tmin_1910_2024.nc",
        "clim":    "mask_monclim_agcd_tmin_1971_2000.nc",
        "var":     "tmin",
        "ylabel":  "Tmin (°C)"
    },
    "vpd": {
        "monthly": "mask_month_means_agcd_vpd15_1971_2024.nc",
        "clim":    "mask_monclim_agcd_vpd15_1971_2000.nc",
        "var":     "vpd",
        "ylabel":  "VPD (kPa, 3pm)"
    }
}

# ---------------------------------------------------------
# LOAD RAIN FIRST (master axis)
# ---------------------------------------------------------
print("Loading rainfall reference...")

rain_cfg = files["precip"]

rain_ds   = xr.open_dataset(os.path.join(input_dir, rain_cfg["monthly"]))
rain_clim = xr.open_dataset(os.path.join(input_dir, rain_cfg["clim"]))

rain = rain_ds[rain_cfg["var"]]
rain_clim_var = rain_clim[rain_cfg["var"]]

rain_mnth = rain.mean(dim=("lat", "lon"))
rain_clim_mnth = rain_clim_var.mean(dim=("lat", "lon"))

years = rain_mnth["year"].values

# ---------------------------------------------------------
# FUNCTION TO PROCESS ANY VARIABLE
# ---------------------------------------------------------
def process_variable(cfg):
    ds   = xr.open_dataset(os.path.join(input_dir, cfg["monthly"]))
    clim = xr.open_dataset(os.path.join(input_dir, cfg["clim"]))

    data = ds[cfg["var"]]
    clim_data = clim[cfg["var"]]

    mnth = data.mean(dim=("lat", "lon"))
    clim_mnth = clim_data.mean(dim=("lat", "lon"))

    var_years = mnth["year"].values

    if cfg["var"] == "precip":
        annual = mnth.sum(dim="month").values
        clim_val = clim_mnth.sum().values
    else:
        annual = mnth.mean(dim="month").values
        clim_val = clim_mnth.mean().values

    anom = annual - clim_val
    rm = pd.Series(anom).rolling(10, center=True).mean()

    anom_full = np.full(len(years), np.nan)
    rm_full   = np.full(len(years), np.nan)
    colors = ["gray"] * len(years)

    start_idx = np.where(years == var_years[0])[0][0]

    anom_full[start_idx:] = anom
    rm_full[start_idx:]   = rm

    for i in range(start_idx, len(years)):
        colors[i] = "blue" if cfg["var"] == "precip" and anom_full[i] >= 0 else \
                    "red"  if cfg["var"] != "precip" and anom_full[i] >= 0 else \
                    "red"  if cfg["var"] == "precip" else "blue"

    return anom_full, rm_full, colors

# ---------------------------------------------------------
# LOAD SELECTED VARIABLES
# ---------------------------------------------------------
results = {}

for var in variables_to_plot:
    print(f"Processing {var}...")
    results[var] = process_variable(files[var])

# ---------------------------------------------------------
# PLOT (dynamic panels)
# ---------------------------------------------------------
nplots = len(variables_to_plot)

fig, axes = plt.subplots(
    nplots, 1, figsize=(15, 3*nplots), sharex=True  # single column plot width
#    nplots, 1, figsize=(7, 2.8*nplots), sharex=True # 2 column plot width
)

if nplots == 1:
    axes = [axes]

label_fs = 18
tick_fs  = 14

for i, (ax, var) in enumerate(zip(axes, variables_to_plot)):

    anom, rm, colors = results[var]

    ax.bar(years, anom, color=colors)
    ax.plot(years, rm, color="black", linewidth=2)
    ax.axhline(0, color="gray")

    ax.set_ylabel(files[var]["ylabel"], fontsize=label_fs)

    if ax != axes[-1]:
        ax.tick_params(axis="x", bottom=False, labelbottom=False)

    ax.tick_params(axis="y", labelsize=tick_fs)

    # ✅ PANEL LABEL
    label = f"{chr(97 + i)})"   # a), b), c), ...
    ax.text(
        0.02, 0.92,
        label,
        transform=ax.transAxes,
        fontsize=14,
        fontweight="bold",
        va="top",
        ha="left"
    )

# ---------------------------------------------------------
# ALIGN Y-AXIS LABELS
# ---------------------------------------------------------
for ax in axes:
    ax.yaxis.set_label_coords(-0.05, 0.5)

# ---------------------------------------------------------
# X AXIS (bottom only)
# ---------------------------------------------------------
axes[-1].set_xlabel("Year", fontsize=label_fs, labelpad=20)

axes[-1].set_xticks(years)
axes[-1].set_xticklabels(
    [str(y) if y % 5 == 0 else "" for y in years],
    fontsize=tick_fs,
    rotation=90
)

# ---------------------------------------------------------
# TITLE + FOOTNOTE
# ---------------------------------------------------------
fig.suptitle("SWWA Climate Anomalies (AGCD)", fontsize=20)

plt.tight_layout()
plt.subplots_adjust(bottom=0.22)

axes[-1].text(
    1.0, -0.60,
    "Based on a 30-year climatology (1971–2000)",
    transform=axes[-1].transAxes,
    ha="right",
    va="top",
    fontsize=12
)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
outfile = os.path.join(output_dir, "SWWA_dynamic_panel_AGCD.png")

plt.savefig(outfile, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved → {outfile}")
