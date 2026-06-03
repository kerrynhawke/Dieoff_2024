#!/usr/bin/env python3
import xarray as xr
import matplotlib.pyplot as plt
import os

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------

NCFILE = "/mnt/d/data/0_masks/IBRA/SWWA/ibra7_swwa_mask_clean.nc"
OUTPUT_DIR = "../figs"
OUTPUT_FILE = "ibra7_swwamaskregion_nc.png"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------------------------
# LOAD NETCDF MASK
# ----------------------------------------------------

print(f"Loading NetCDF mask: {NCFILE}")
ds = xr.open_dataset(NCFILE)
mask = ds["mask"]

# ----------------------------------------------------
# PLOT
# ----------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 10))

mask.plot(
    ax=ax,
    cmap="Greys",
    add_colorbar=False
)

ax.set_title("IBRA7 SWWA mask", fontsize=14)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

ax.set_xticks([])
ax.set_yticks([])

# ----------------------------------------------------
# SAVE
# ----------------------------------------------------

save_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved map to: {save_path}")
