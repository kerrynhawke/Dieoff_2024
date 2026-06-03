#!/usr/bin/env python3
import xarray as xr
import numpy as np
import os

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------

tmax_pattern = "/pvol/AGCD/v1-0-3/tmax/mean/r005/01day/*.nc"
vp_pattern   = "/pvol/AGCD/v1-0-3/vapourpres_h15/mean/r005/01day/*.nc"

variable = "vpd"

mask_file = "../mask/ibra7_swwa_mask_clean.nc"

start_year = 1971
end_year   = 2024

output_dir = "../outputs"

periods = {
    "1971_2000": (1971, 1990, f"{output_dir}/mask_monclim_agcd_vpd15_1971_2000.nc"),
    "1995_2024": (1995, 2024, f"{output_dir}/mask_monclim_agcd_vpd15_1995_2024.nc"),
}

all_monthly_means_out = f"{output_dir}/mask_month_means_agcd_vpd15_{start_year}_{end_year}.nc"

# ----------------------------------------------------
# LOAD DATA
# ----------------------------------------------------

print("Loading tmax...")
ds_tmax = xr.open_mfdataset(tmax_pattern, combine="by_coords", parallel=False)

print("Loading vapour pressure (h15)...")
ds_vp = xr.open_mfdataset(vp_pattern, combine="by_coords", parallel=False)

ds_tmax = xr.decode_cf(ds_tmax).sortby("time")
ds_vp   = xr.decode_cf(ds_vp).sortby("time")

print("tmax time:", ds_tmax.time.min().values, "→", ds_tmax.time.max().values)
print("vp time:",   ds_vp.time.min().values,   "→", ds_vp.time.max().values)

# ----------------------------------------------------
# SELECT VARIABLES
# ----------------------------------------------------

tmax = ds_tmax["tmax"]
vp   = ds_vp["vapourpres"]

# Convert hPa → kPa
vp = vp / 10.0

# ----------------------------------------------------
# ✅ FIX: NORMALIZE TIME
# ----------------------------------------------------

tmax["time"] = tmax["time"].dt.floor("D")
vp["time"]   = vp["time"].dt.floor("D")

# ----------------------------------------------------
# ALIGN TIME
# ----------------------------------------------------

tmax, vp = xr.align(tmax, vp, join="inner")

if tmax.time.size == 0:
    raise RuntimeError("ERROR: No overlapping time after alignment")

print("Aligned time:", tmax.time.min().values, "→", tmax.time.max().values)

# Apply time range
tmax = tmax.sel(time=slice(f"{start_year}-01-01", f"{end_year}-12-31"))
vp   = vp.sel(time=slice(f"{start_year}-01-01", f"{end_year}-12-31"))

print("Time length:", tmax.time.size)

# ----------------------------------------------------
# LOAD MASK
# ----------------------------------------------------

print("Loading mask...")

mask_ds = xr.open_dataset(mask_file)
mask_var = list(mask_ds.data_vars)[0]
mask = mask_ds[mask_var]

mask = mask.rename({
    "latitude": "lat",
    "longitude": "lon"
}).squeeze()

# ----------------------------------------------------
# INTERPOLATE MASK
# ----------------------------------------------------

mask_interp = mask.interp(
    lat=tmax.lat,
    lon=tmax.lon,
    method="nearest"
)

# ----------------------------------------------------
# VPD FUNCTION
# ----------------------------------------------------

def calc_vpd(T, ea):
    es = 0.6108 * np.exp((17.27 * T) / (T + 237.3))
    return es - ea

# ----------------------------------------------------
# COMPUTE VPD
# ----------------------------------------------------

print("Computing VPD...")

vpd_daily = calc_vpd(tmax, vp)
vpd_daily = vpd_daily.clip(min=0)

# Mask (no drop)
vpd_daily = vpd_daily.where(mask_interp == 1)

print("Time length after masking:", vpd_daily.time.size)

# ----------------------------------------------------
# DAILY → MONTHLY
# ----------------------------------------------------

print("Aggregating to monthly...")

vpd_monthly = vpd_daily.resample(time="1MS").mean()
vpd_monthly = vpd_monthly.where(mask_interp == 1, drop=True)

# ----------------------------------------------------
# MONTHLY MEANS PER YEAR
# ----------------------------------------------------

monthly_means = []

years = np.arange(start_year, end_year + 1)

for yr in years:
    print(f"  Processing {yr}")

    ds_year = vpd_monthly.sel(time=str(yr))

    if ds_year.time.size != 12:
        print(f"  Skipping {yr}")
        continue

    mth = ds_year.groupby("time.month").mean("time")
    mth = mth.expand_dims(year=[yr])

    monthly_means.append(mth)

all_monthly_means = xr.concat(monthly_means, dim="year")
all_monthly_means.name = variable

# ----------------------------------------------------
# SAVE
# ----------------------------------------------------

os.makedirs(output_dir, exist_ok=True)

if os.path.exists(all_monthly_means_out):
    os.remove(all_monthly_means_out)

print("Saving:", os.path.abspath(all_monthly_means_out))
all_monthly_means.to_netcdf(all_monthly_means_out)

# ----------------------------------------------------
# CLIMATOLOGIES
# ----------------------------------------------------

for label, (start_c, end_c, outfile) in periods.items():

    print(f"\n=== Climatology {label} ({start_c}-{end_c}) ===")

    subset = all_monthly_means.sel(year=slice(start_c, end_c))
    clim = subset.mean(dim="year")
    clim.name = variable

    if os.path.exists(outfile):
        os.remove(outfile)

    print("Saving:", os.path.abspath(outfile))
    clim.to_netcdf(outfile)

# ----------------------------------------------------
# CLEAN UP
# ----------------------------------------------------

ds_tmax.close()
ds_vp.close()
mask_ds.close()

print("\n✅ Done — AGCD VPD_h15 complete")

