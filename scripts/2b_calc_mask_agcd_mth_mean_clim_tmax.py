#!/usr/bin/env python3
import xarray as xr
import numpy as np
import os

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------

# AGCD monthly tmax files
input_pattern = "/pvol/AGCD/v1-0-3/tmax/mean/r005/01month/*.nc"

variable = "tmax"

# Mask
mask_file = "../mask/ibra7_swwa_mask_clean.nc"

# ---- USER YEAR RANGE ----
start_year = 1910
end_year   = 2024

# ---- OUTPUT DIR ----
output_dir = "../outputs"

# ---- CLIMATOLOGY PERIODS ----
periods = {
    "1961_1990": (1961, 1990, f"{output_dir}/mask_monclim_agcd_tmax_1961_1990.nc"),
    "1971_2000": (1971, 2000, f"{output_dir}/mask_monclim_agcd_tmax_1971_2000.nc"),
    "1995_2024": (1995, 2024, f"{output_dir}/mask_monclim_agcd_tmax_1995_2024.nc"),
}

# ALL monthly means output
all_monthly_means_out = f"{output_dir}/mask_month_means_agcd_tmax_{start_year}_{end_year}.nc"


# ----------------------------------------------------
# LOAD AGCD DATA
# ----------------------------------------------------

print("Loading AGCD tmax data...")

ds = xr.open_mfdataset(
    input_pattern,
    combine="by_coords"
)

print(ds)

# Select time range
ds = ds.sel(time=slice(f"{start_year}-01-01", f"{end_year}-12-31"))

print(f"Data time range: {ds.time.min().values} → {ds.time.max().values}")


# ----------------------------------------------------
# LOAD + FIX MASK
# ----------------------------------------------------

print("Loading mask...")

mask_ds = xr.open_dataset(mask_file)
mask_var = list(mask_ds.data_vars)[0]
mask = mask_ds[mask_var]

# ✅ Rename to match AGCD grid
mask = mask.rename({
    "latitude": "lat",
    "longitude": "lon"
})

mask = mask.squeeze()

print("Mask dims:", mask.dims)


# ----------------------------------------------------
# INTERPOLATE MASK
# ----------------------------------------------------

print("Interpolating mask...")

mask_interp = mask.interp(
    lat=ds.lat,
    lon=ds.lon,
    method="nearest"
)

print("Interpolated mask dims:", mask_interp.dims)


# ----------------------------------------------------
# APPLY MASK
# ----------------------------------------------------

print("Applying mask...")

masked = ds[variable].where(mask_interp == 1)


# ----------------------------------------------------
# MONTHLY MEANS (PER YEAR)
# ----------------------------------------------------

print("Computing monthly means...")

monthly_means = []

years = np.arange(start_year, end_year + 1)

for yr in years:
    print(f"  Processing {yr}")

    ds_year = masked.sel(time=str(yr))

    if ds_year.time.size != 12:
        print(f"  Skipping {yr} (incomplete)")
        continue

    mth = ds_year.groupby("time.month").mean("time")
    mth = mth.expand_dims(year=[yr])

    monthly_means.append(mth)

# Combine all years
all_monthly_means = xr.concat(monthly_means, dim="year")
all_monthly_means.name = variable


# ----------------------------------------------------
# SAVE MONTHLY MEANS
# ----------------------------------------------------

os.makedirs(output_dir, exist_ok=True)

print("Saving monthly means to:")
print(os.path.abspath(all_monthly_means_out))

if os.path.exists(all_monthly_means_out):
    os.remove(all_monthly_means_out)

all_monthly_means.to_netcdf(all_monthly_means_out)


# ----------------------------------------------------
# CLIMATOLOGIES
# ----------------------------------------------------

for label, (start_c, end_c, outfile) in periods.items():

    print(f"\n=== Climatology {label} ({start_c}-{end_c}) ===")

    subset = all_monthly_means.sel(year=slice(start_c, end_c))

    clim = subset.mean(dim="year")
    clim.name = variable

    os.makedirs(os.path.dirname(outfile), exist_ok=True)

    print("Saving to:")
    print(os.path.abspath(outfile))

    if os.path.exists(outfile):
        os.remove(outfile)

    clim.to_netcdf(outfile)


# ----------------------------------------------------
# CLEAN UP
# ----------------------------------------------------

ds.close()
mask_ds.close()

print("\n✅ Done")
