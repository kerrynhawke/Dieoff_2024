#!/usr/bin/env python3
import xarray as xr
import os

# ---------------------------------------------------------
# CONFIG (ONLY CHANGE THIS SECTION)
# ---------------------------------------------------------

var = "vpd15"   # ✅ choose: "tmin", "tmax", "precip", "vpd15"

input_base = "/pvol/AGCD/v1-0-3"

var_paths = {
    "tmin":   f"{input_base}/tmin/mean/r005/01month/*.nc",
    "tmax":   f"{input_base}/tmax/mean/r005/01month/*.nc",
    "precip": f"{input_base}/precip/total/r005/01month/*.nc",
    "vpd15":  f"{input_base}/vapourpres_h15/mean/r005/01day/*.nc",
}

# ✅ Correct variable names inside files
file_var_names = {
    "tmin": "tmin",
    "tmax": "tmax",
    "precip": "precip",
    "vpd15": "vapourpres",
}

input_pattern = var_paths[var]
file_var = file_var_names[var]

output_dir = "../outputs_maps"
os.makedirs(output_dir, exist_ok=True)

# Spatial domain
lat_min, lat_max = -37.0, -27.7
lon_min, lon_max = 113.3, 120.2

# Climatology periods
periods = {
    "1961_1990": (1961, 1990),
    "1971_2000": (1971, 2000),
    "1995_2024": (1995, 2024),
}

baseline_key = "1971_2000"

# Target period
target_years = [2023, 2024]
target_months = list(range(1, 13))

# Control behaviour
force_recompute_clim = False

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

print(f"Loading AGCD {var}...")

ds = xr.open_mfdataset(input_pattern, combine="by_coords", chunks=None)

# ✅ Fix coordinate names (lat/lon consistency)
rename_dict = {}
if "longitude" in ds.coords:
    rename_dict["longitude"] = "lon"
if "latitude" in ds.coords:
    rename_dict["latitude"] = "lat"
if rename_dict:
    ds = ds.rename(rename_dict)

# ✅ Spatial subset
ds = ds.sel(
    lat=slice(lat_min, lat_max),
    lon=slice(lon_min, lon_max)
)

# ✅ Explicit variable selection (critical fix)
if file_var not in ds.data_vars:
    raise ValueError(f"Variable '{file_var}' not found in dataset")

data = ds[file_var]

# ✅ Convert daily → monthly (VPD only)
if var == "vpd15":
    print("Converting daily data to monthly means...")
    data = data.resample(time="1M").mean()

# ✅ Standardise output variable name
data.name = var

# ✅ Sanity check
print(f"Data dims: {data.dims}")
if "lon" not in data.dims:
    raise ValueError("ERROR: No longitude dimension found — check input data")

# ---------------------------------------------------------
# CLIMATOLOGIES
# ---------------------------------------------------------

print("\n=== CLIMATOLOGIES ===")

climatologies = {}

for label, (start, end) in periods.items():

    outfile = os.path.join(output_dir, f"swwa_{var}_clim_{label}.nc")

    if os.path.exists(outfile) and not force_recompute_clim:
        print(f"✔ Using existing: {label}")
        clim = xr.open_dataset(outfile)[var]

    else:
        print(f"Computing: {label}")

        subset = data.sel(time=slice(f"{start}-01-01", f"{end}-12-31"))

        clim = subset.groupby("time.month").mean("time")
        clim.name = var

        clim = clim.load()  # ✅ avoid Dask issues
        clim.to_netcdf(outfile)

        print(f"Saved: {outfile}")

    climatologies[label] = clim

# ---------------------------------------------------------
# TARGET DATA
# ---------------------------------------------------------

print("\n=== EXTRACTING TARGET DATA ===")

target = data.sel(time=data.time.dt.year.isin(target_years))
target = target.sel(time=target.time.dt.month.isin(target_months))

print(f"Selected: years={target_years}, months={target_months}")

target = target.load()

print(f"Target dims: {target.dims}")

# ---------------------------------------------------------
# SAVE RAW MONTHLY DATA
# ---------------------------------------------------------

raw_file = os.path.join(
    output_dir,
    f"swwa_{var}_monthly_{min(target_years)}_{max(target_years)}.nc"
)

target.to_netcdf(raw_file)
print(f"Saved raw monthly data: {raw_file}")

# ---------------------------------------------------------
# COMPUTE ANOMALIES
# ---------------------------------------------------------

print("\n=== COMPUTING ANOMALIES ===")

baseline = climatologies[baseline_key].load()

anom = target.groupby("time.month") - baseline
anom.name = var

# ✅ Final sanity check
print(f"Anomaly dims: {anom.dims}")
if "lon" not in anom.dims:
    raise ValueError("ERROR: Output anomaly missing lon dimension")

anom_file = os.path.join(
    output_dir,
    f"swwa_{var}_anom_{min(target_years)}_{max(target_years)}.nc"
)

anom.to_netcdf(anom_file)

print(f"Saved anomalies: {anom_file}")

# ---------------------------------------------------------
# CLEAN UP
# ---------------------------------------------------------

ds.close()

print(f"\n✅ Done — SWWA {var} processing complete")
