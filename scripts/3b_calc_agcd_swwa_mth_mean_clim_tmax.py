#!/usr/bin/env python3
import xarray as xr
import os

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

# ✅ CHANGE: tmax input path
input_pattern = "/pvol/AGCD/v1-0-3/tmax/mean/r005/01month/*.nc"

# ✅ CHANGE: variable name
variable = "tmax"

output_dir = "../outputs_maps"
os.makedirs(output_dir, exist_ok=True)

# ✅ SAME DOMAIN (unchanged)
lat_min, lat_max = -37.0, -27.7
lon_min, lon_max = 113.3, 120.2

# ✅ SAME climatology periods
periods = {
    "1961_1990": (1961, 1990),
    "1971_2000": (1971, 2000),   # baseline
    "1995_2024": (1995, 2024),
}

baseline_key = "1971_2000"

# ✅ SAME target period
target_years = [2023, 2024]
target_months = list(range(1, 13))

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

print("Loading AGCD tmax...")

ds = xr.open_mfdataset(input_pattern, combine="by_coords")

# ✅ SAME domain subset
ds = ds.sel(
    lat=slice(lat_min, lat_max),
    lon=slice(lon_min, lon_max)
)

data = ds[variable]

# ✅ SAME time coords
data["year"] = data["time"].dt.year
data["month"] = data["time"].dt.month

# ---------------------------------------------------------
# CREATE / LOAD CLIMATOLOGIES
# ---------------------------------------------------------

print("\n=== CLIMATOLOGIES ===")

climatologies = {}

for label, (start, end) in periods.items():

    # ✅ CHANGE: filename uses tmax
    outfile = os.path.join(output_dir, f"swwa_tmax_clim_{label}.nc")

    if os.path.exists(outfile):
        print(f"✔ Using existing: {label}")
        clim = xr.open_dataset(outfile)[variable]

    else:
        print(f"Computing: {label}")

        subset = data.sel(time=slice(f"{start}-01-01", f"{end}-12-31"))

        clim = subset.groupby("month").mean("time")
        clim.name = variable

        clim.to_netcdf(outfile)
        print(f"Saved: {outfile}")

    climatologies[label] = clim

# ---------------------------------------------------------
# SELECT TARGET DATA
# ---------------------------------------------------------

print("\n=== EXTRACTING TARGET DATA ===")

target = data.sel(time=data["year"].isin(target_years))
target = target.sel(time=target["month"].isin(target_months))

print(f"Selected: years={target_years}, months={target_months}")

# ---------------------------------------------------------
# SAVE RAW MONTHLY DATA
# ---------------------------------------------------------

raw_file = os.path.join(
    output_dir,
    f"swwa_tmax_monthly_{min(target_years)}_{max(target_years)}.nc"
)

target.to_netcdf(raw_file)
print(f"Saved raw monthly data: {raw_file}")

# ---------------------------------------------------------
# COMPUTE ANOMALIES
# ---------------------------------------------------------

print("\n=== COMPUTING ANOMALIES ===")

baseline = climatologies[baseline_key]

anom = target.groupby("month") - baseline
anom.name = variable

anom_file = os.path.join(
    output_dir,
    f"swwa_tmax_anom_{min(target_years)}_{max(target_years)}.nc"
)

anom.to_netcdf(anom_file)

print(f"Saved anomalies: {anom_file}")

# ---------------------------------------------------------
# CLEAN UP
# ---------------------------------------------------------

ds.close()

print("\n✅ Done — SWWA tmax maps ready")
