#!/usr/bin/env python3
import xarray as xr
import numpy as np
import os

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------

# ✅ VARIABLES TO PROCESS
variables = ["tmax", "tmin"]

# ✅ AGCD base path
base_input = "/pvol/AGCD/v1-0-3"

# ✅ Mask
mask_file = "../mask/ibra7_swwa_mask_clean.nc"

# ---- USER YEAR RANGE ----
start_year = 1910
end_year   = 2024

# ---- OUTPUT DIR ----
output_dir = "../outputs_maps"

# ---- CLIMATOLOGY PERIODS ----
clim_periods = {
    "1961_1990": (1961, 1990),
    "1971_2000": (1971, 2000),
    "1995_2024": (1995, 2024),
}

# ----------------------------------------------------
# LOAD + FIX MASK (do once)
# ----------------------------------------------------

print("Loading mask...")

mask_ds = xr.open_dataset(mask_file)
mask_var = list(mask_ds.data_vars)[0]
mask = mask_ds[mask_var]

mask = mask.rename({
    "latitude": "lat",
    "longitude": "lon"
}).squeeze()

print("Mask dims:", mask.dims)

# ----------------------------------------------------
# LOOP OVER VARIABLES
# ----------------------------------------------------

for variable in variables:

    print("\n" + "="*50)
    print(f"Processing variable: {variable}")
    print("="*50)

    # ----------------------------------------------------
    # INPUT PATH
    # ----------------------------------------------------

    input_pattern = f"{base_input}/{variable}/mean/r005/01month/*.nc"

    print("Loading AGCD data...")

    ds = xr.open_mfdataset(
        input_pattern,
        combine="by_coords"
    )

    ds = ds.sel(time=slice(f"{start_year}-01-01", f"{end_year}-12-31"))

    print(f"Data time range: {ds.time.min().values} → {ds.time.max().values}")

    # ----------------------------------------------------
    # INTERPOLATE MASK (to each variable grid)
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
        print(f"  {variable}: {yr}")

        ds_year = masked.sel(time=str(yr))

        if ds_year.time.size != 12:
            print(f"  Skipping {yr} (incomplete)")
            continue

        mth = ds_year.groupby("time.month").mean("time")
        mth = mth.expand_dims(year=[yr])

        monthly_means.append(mth)

    if not monthly_means:
        print(f"No valid data for {variable}, skipping...")
        ds.close()
        continue

    all_monthly_means = xr.concat(monthly_means, dim="year")
    all_monthly_means.name = variable

    # ----------------------------------------------------
    # SAVE MONTHLY MEANS
    # ----------------------------------------------------

    os.makedirs(output_dir, exist_ok=True)

    monthly_out = f"{output_dir}/swwa_{variable}_monthly_{start_year}_{end_year}.nc"

    print("Saving monthly means to:")
    print(os.path.abspath(monthly_out))

    if os.path.exists(monthly_out):
        os.remove(monthly_out)

    all_monthly_means.to_netcdf(monthly_out)

    # ----------------------------------------------------
    # CLIMATOLOGIES
    # ----------------------------------------------------

    for label, (start_c, end_c) in clim_periods.items():

        print(f"\nClimatology {variable} {label}")

        subset = all_monthly_means.sel(year=slice(start_c, end_c))

        clim = subset.mean(dim="year")
        clim.name = variable

        outfile = f"{output_dir}/swwa_{variable}_clim_{start_year}_{end_year}.nc"

        print("Saving to:")
        print(os.path.abspath(outfile))

        if os.path.exists(outfile):
            os.remove(outfile)

        clim.to_netcdf(outfile)

    # ----------------------------------------------------
    # CLEAN UP VARIABLE DATASET
    # ----------------------------------------------------

    ds.close()

# ----------------------------------------------------
# FINAL CLEANUP
# ----------------------------------------------------

mask_ds.close()

print("\n✅ All variables processed successfully")
