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
# VARIABLES TO PLOT
# ---------------------------------------------------------
variables_to_plot = ["precip", "tmax", "tmin", "vpd"]

# ---------------------------------------------------------
# FILE MAP
# ---------------------------------------------------------
files = {
    "precip": {
        "monthly": "mask_month_means_agcd_precip_1900_2024.nc",
        "var":     "precip",
        "ylabel":  "Rainfall (mm)"
    },
    "tmax": {
        "monthly": "mask_month_means_agcd_tmax_1910_2024.nc",
        "var":     "tmax",
        "ylabel":  "Tmax (°C)"
    },
    "tmin": {
        "monthly": "mask_month_means_agcd_tmin_1910_2024.nc",
        "var":     "tmin",
        "ylabel":  "Tmin (°C)"
    },
    "vpd": {
        "monthly": "mask_month_means_agcd_vpd15_1971_2024.nc",
        "var":     "vpd",
        "ylabel":  "VPD15 (kPa)"
    }
}

# ---------------------------------------------------------
# FUNCTION: extract July 2023 → June 2024
# ---------------------------------------------------------
def extract_2023_24(mnth):
    m23 = mnth.sel(year=2023, month=slice(7, 12))
    m24 = mnth.sel(year=2024, month=slice(1, 6))
    out = xr.concat([m23, m24], dim="month")
    dates = pd.date_range("2023-07-01", "2024-06-01", freq="MS")
    return out.assign_coords(time=("month", dates))

# ---------------------------------------------------------
# FUNCTION: compute climatology stats
# ---------------------------------------------------------
def compute_climatology(mnth):
    clim_mean = mnth.mean(dim="year")
    clim_p10  = mnth.quantile(0.10, dim="year")
    clim_p90  = mnth.quantile(0.90, dim="year")
    return clim_mean, clim_p10, clim_p90

# ---------------------------------------------------------
# PROCESS ALL VARIABLES
# ---------------------------------------------------------
processed = {}

for var in variables_to_plot:
    cfg = files[var]

    ds = xr.open_dataset(os.path.join(input_dir, cfg["monthly"]))
    data = ds[cfg["var"]]  # dims: year, month, lat, lon

    # area‑average
    mnth = data.mean(dim=("lat", "lon"))

    # extract 2023–24
    mnth_2324 = extract_2023_24(mnth)

    # climatology
    clim_mean, clim_p10, clim_p90 = compute_climatology(mnth)

    # match months
    months = mnth_2324["time.month"].values
    mean_vals = clim_mean.sel(month=months)
    p10_vals  = clim_p10.sel(month=months)
    p90_vals  = clim_p90.sel(month=months)

    processed[var] = {
        "mnth_2324": mnth_2324,
        "mean": mean_vals,
        "p10": p10_vals,
        "p90": p90_vals
    }

# ---------------------------------------------------------
# PLOT (4‑panel figure)
# ---------------------------------------------------------
fig, axes = plt.subplots(
    len(variables_to_plot), 1,
    figsize=(14, 12),
    sharex=True
)

label_fs = 16
tick_fs  = 13

# Month labels (12 months only)
month_labels = ["Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun"]

# X positions
x = np.arange(12)

# Year label positions
pos_2023 = (2 + 3) / 2   # between Sep (2) and Oct (3)
pos_2024 = (8 + 9) / 2   # between Mar (8) and Apr (9)

for i, var in enumerate(variables_to_plot):
    ax = axes[i]
    cfg = files[var]
    d = processed[var]

    # shaded band
    ax.fill_between(
        x,
        d["p10"],
        d["p90"],
        color="lightgray",
        alpha=0.5
    )

    # mean line
    ax.plot(
        x,
        d["mean"],
        color="dimgray",
        linewidth=2
    )

    # rainfall = bars
    if var == "precip":
        ax.bar(
            x,
            d["mnth_2324"].values,
            width=0.9,
            color="steelblue",
            label="2023–24 monthly rainfall"
        )
    else:
        # other variables = asterisks
        ax.plot(
            x,
            d["mnth_2324"].values,
            marker="*",
            markersize=14,
            linestyle="None",
            color="black",
            label="* 2023–24 monthly mean (Tmax, Tmin, VPD15)"
        )

    ax.set_ylabel(cfg["ylabel"], fontsize=label_fs)
    ax.grid(alpha=0.3)

# ---------------------------------------------------------
# X‑axis formatting
# ---------------------------------------------------------
axes[-1].set_xticks(x)
axes[-1].set_xticklabels(month_labels, fontsize=tick_fs)

# Add year labels on second row
axes[-1].text(pos_2023, -0.25, "2023", ha="center", fontsize=14)
axes[-1].text(pos_2024, -0.25, "2024", ha="center", fontsize=14)

# ---------------------------------------------------------
# LEGEND BELOW FIGURE (closer to bottom panel)
# ---------------------------------------------------------
legend_elements = [
    plt.Line2D([0], [0], color="dimgray", linewidth=2,
               label="Long-term average"),
    plt.Line2D([0], [0], color="lightgray", linewidth=10, alpha=0.5,
               label="Long-term 10th–90th percentiles"),
    plt.Line2D([0], [0], color="steelblue", linewidth=10,
               label="2023–24 monthly rainfall"),
    plt.Line2D([0], [0], marker="*", color="black", linestyle="None", markersize=12,
               label="* 2023–24 monthly mean (Tmax, Tmin, VPD15)")
]

fig.legend(
    handles=legend_elements,
    loc="lower center",
    ncol=2,
    fontsize=13,
    frameon=False,
    bbox_to_anchor=(0.5, -0.02)   # closer to bottom panel
)

plt.tight_layout(rect=[0, 0.06, 1, 1])   # adjust bottom margin

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
outfile = os.path.join(output_dir, "2023_2024_month_anomaly_timeseries.png")
plt.savefig(outfile, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved → {outfile}")

