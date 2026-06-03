# Project Overview
This git repository contains the scripts and workflow used in the climate analysis of the 2024 browning event in southwest Western Australia as part of a research project looking into the drivers and impacts of this event (article TBA).


# Directory Structure
```
|-- Dieoff_2024
	|-- figs		    (all graph outputs) 
	|-- mask		    (coast and IBRA masks)
	|-- outputs		    (all data outputs)
	|-- outputs_maps	(all map outputs)
	|-- scripts		    (all calculation, plotting scripts)
```
# Input data
## 1. AGCD data
The Australian Gridded Climate Data (AGCD) is a high-resolution gridded precipitation dataset that provides spatially continuous gridded data across the whole of continental Australia (Evans et al., 2020; Jones et al., 2009). It is available at daily, monthly, and annual intervals, with spatial resolutions of 0.05° × 0.05° (approximately 5 km²) and 0.01 × 0.01° (approximately 1 km²). Compiled using manual and automated rain gauge observations collected by the Australian Bureau of Meteorology, the AGCD has two versions: the original AGCD v1 (previously referred to as the Australian Water Availability Project, AWAP) and the updated AGCD v2. With challenges posed by limited station data in certain areas, the dataset is particularly valuable in remote regions, like much of Western Australia, where observational data is sparse. It was developed specifically for climate analysis within the Australian region (Evans et al., 2020) and has been widely applied since its inception for applications such as studies of rainfall trends (e.g., McKay et al., 2023; Waha et al., 2022), extreme events (e.g., Dowdy & Catto, 2017) and evaluations of seasonal forecasts (Firth et al., 2024) and regional climate model outputs (e.g., Chapman et al., 2023; Thambipillai et al., 2026). In this study, AGCD v2 was used, the data were stored in NetCDF format and analysed using Python v3.9.23 (Python Software Foundation, 2025).

## 2. Regions (IBRA)
The IBRA regions of Lesueur Sandplain, Dandaragan Plateau, Perth, Northern Jarrah Forest, Southern Jarrah Forest, and Warren (DCCEEW, 2012) were used as a mask to represent the southwestern Australian area in the calculations of the Tmax, Tmean, Tmin, precipitation and VPD 30-year climatological means and monthly means used in the timeseries plots (Figure 1a). Note that the whole land area, bounded by the coast, has been retained for the maps (Figure 1b).

## 3. Variables
- Precip	precipitation (mm, daily totals)
- Tmax		maximum temperature (°C)
- Tmean		mean temperature (°C; calculated from (Tmax + Tmin)/2)
- Tmin		minimum temperature (°C)
- vpd15		vapour pressure deficit at 3 pm local time (kPa)

## References
- Chapman, S., Syktus, J., Trancoso, R., Thatcher, M., Toombs, N., Wong, K. K., & Takbash, A. (2023). Evaluation of Dynamically Downscaled CMIP6‐CCAM models over Australia. Earth’s Future, 11(11), e2023EF003548. https://doi.org/10.1029/2023EF003548
- Dowdy, A. J., & Catto, J. L. (2017). Extreme weather caused by concurrent cyclone, front and thunderstorm occurrences. Scientific Reports, 7, 40359. https://doi.org/10.1038/srep40359
- Evans, A., Jones, D., Lellyett, S., & Smalley, R. (2020). An enhanced gridded rainfall analysis scheme for Australia. (Bureau Research Report 41). Australia. Bureau of Meteorology. http://www.bom.gov.au/research/publications/researchreports/BRR-041.pdf
- Firth, R., Kala, J., Hudson, D., Hawke, K. A., & Marshall, A. (2024). ACCESS-S2 seasonal forecasts of rainfall and the SAM–rainfall relationship during the grain growing season in south-west Western Australia. Journal of Southern Hemisphere Earth Systems Science , 74, ES24004. https://doi.org/10.1071/ES24004
- Department of Climate Change, Energy, the Environment and Water (DCCEEW) (2012). Interim Biogeographic Regionalisation for Australia (IBRA), Version 7.1 – Bioregions and subregions dataset. https://fed.dcceew.gov.au/datasets/erin::interim-biogeographic-regionalisation-for-australia-ibra-version-7-1-subregions/about
- Jones, D. A., Wang, W., & Fawcett, R. (2009). High-quality spatial climate data-sets for Australia. Australian Meteorological and Oceanographic Journal, 58(4), 233–248. https://doi.org/10.1071/ES09032
- McKay, R. C., Boschat, G., Rudeva, I., Pepler, A. S., Purich, A., Dowdy, A. J., Hope, P. K., Gillett, Z. E., & Rauniyar, S. (2023). Can southern Australian rainfall decline be explained? A review of possible drivers. Wiley Interdisciplinary Reviews: Climate Change, 14(2), e820. https://doi.org/10.1002/wcc.820
- Python Software Foundation (2025). Python 3.9.25 final. https://docs.python.org/3.9/whatsnew/changelog.html#python-3-9-23
- Thambipillai, T., Kala, J., Hawke, K. A., & di Virgilio, G. (2026). Evaluation of CMIP6 model skill in capturing the combined and independent influences of the IOD and ENSO on Australian rainfall during JJASON. Climate Dynamics, 64(1), 7. https://doi.org/10.1007/s00382-025-07929-9
- Waha, K., Clarke, J., Dayal, K., Freund, M., Heady, C., Parisi, I., & Vogel, E. (2022). Past and future rainfall changes in the Australian midlatitudes and implications for agriculture. Climatic Change, 170(3–4). https://doi.org/10.1007/s10584-021-03301-y

# Workflow and Scripts

## 1. Creation of the IBRA7 mask


### Scripts
- 1a_create_ibra7_swwaregion_shp.py     (summary note tba)
- 1b_create_ibra7_swwamask_clean_shp.py (summary note tba)
- 1c_create_ibra7_swwamask_clean_nc.py  (summary note tba)
- 1d_bounds_agcd_anomaly_swwa.py        (summary note tba)
- 1e_create_ibra7_coast.py              (summary note tba)
- 1f_clean_ibra7_coast.py               (summary note tba)
- 1g_plot_ibra7_swwamask.py             (summary note tba)

## 2. Data preparation
### Workflow


### Raw data (Murdoch University only access)
ARDC Nectar cloud

```
/pvol/AGCD/v1-0-3/
    |-- vapourpres_h15/mean/r005/01day/agcd_v1_vapourpres_h15_mean_r005_daily_2024.nc (1971-2024 daily vapour pressure deficit at 3 pm LST data)
    |--
```
### Scripts
- 2a_calc_mask_agcd_mth_mean_clim_tp.py             (summary note tba)
- 2b_calc_mask_agcd_mth_mean_clim_tmax.py           (summary note tba)
- 2c_calc_mask_agcd_mth_mean_clim_tmin.py           (summary note tba)
- 2d_calc_mask_agcd_mth_mean_clim_vpd09.py          (summary note tba)
- 2e_calc_mask_agcd_mth_mean_clim_vpd15.py          (summary note tba)
- 2f_calc_mask_agcd_mth_mean_clim_tmean.py          (summary note tba)
- 3a_calc_agcd_swwa_mth_mean_clim_precip.py         (summary note tba)
- 3b_calc_agcd_swwa_mth_mean_clim_tmax.py           (summary note tba)
- 3b_calc_agcd_swwa_mth_mean_clim_tmax_tmin_temp.py (summary note tba)

## 3. Creation of the timeseries figures
### Workflow


### Scripts
- plot_agcd_anomalies_year_all_choice_timeseries.py         (summary note tba)
- plot_agcd_anomalies_year_all_timeseries.py                (summary note tba)
- plot_agcd_anomalies_year_precip_tmax_timeseries.py		(interim timeseries plot, precip-tmax only)
- plot_agcd_anomalies_year_precip_tmax_tmin_timeseries.py	(interim timeseries plot, precip-tmax-tmin only)
- plot_agcd_anomalies_year_precip_tmax_vpd15_timeseries.py	(interim timeseries plot, precip-tmax-vpd15 only)


## 4. Creation of the anomaly map figures
### Data preparation Workflow
This section describes the workflow used to generate monthly climatology () and anomaly .nc files for the SWWA region using AGCD datasets. These outputs are used as inputs for subsequent map visualisation scripts.

#### Data preparation script
- 3_calc_agcd_swwa_mth_mean_clim_allvar.py

1. Input Data
The analysis uses Australian Gridded Climate Data (AGCD) v1.0.3:
```
| *Variable*        | *Temporal resolution | *Path*                                             |
| precip            | monthly              | /pvol/AGCD/v1-0-3/precip/mean/r005/01month/        |
| Tmax              | monthly              | /pvol/AGCD/v1-0-3/tmax/mean/r005/01month/          |
| Tmin              | monthly              | /pvol/AGCD/v1-0-3/tmin/mean/r005/01month/          |
| vapour pressure   | monthly              | /pvol/AGCD/v1-0-3/vapourpres_h15/mean/r005/01day/  |

```
Notes:
```
- The VPD dataset (vapourpres_h15) is provided at daily resolution and is aggregated to monthly means during processing.
The variable names used within NetCDF files differ from folder names:
 - tmin, tmax, precip
 - vapourpres (for VPD input)
```
2. Spatial Subsetting
```
All variables are subset to the South-West Western Australia (SWWA) domain:
 - Latitude:  -37.0 to -27.7  
 - Longitude: 113.3 to 120.2

This produces a consistent grid across all variables: (time, lat, lon)
```
3. Monthly Data Preparation
```
For monthly datasets (tmin, tmax, precip)
 - Data are used directly as monthly values.
```
For vapour pressure (VPD proxy)
 - Daily data are aggregated to monthly means: monthly = daily.resample(time="1M").mean()

4. Climatology Calculation
```
Monthly climatologies are computed for three standard periods:
- 1961–1990
- 1971–2000 (baseline)
- 1995–2024

For each period: climatology(month, lat, lon) = mean over all years for each calendar month
 - This produces a dataset with dimensions: (month, lat, lon)
 - Climatologies are saved as: outputs_maps/swwa_<var>_clim_<period>.nc
```
5. Target Period Extraction
```
Monthly data are extracted for the analysis period:
 - Years: 2023–2024  
 - Months: January–December

 - This produces a dataset with dimensions: (time, lat, lon)
 - Monthly files are saved as: outputs_maps/swwa_<var>_monthly_2023_2024.nc
```
6. Anomaly Calculation
```
Anomalies are calculated relative to the 1971–2000 baseline climatology.

For each grid cell and time step: anomaly = observed_value − climatological_mean_for_that_month
 - Implemented as: anom = target.groupby("time.month") - baseline
 - This ensures January values are compared to January climatology, February values to February climatology, etc.
 - This produces a dataset with dimensions: (time, lat, lon)
 - Anomaly files saved as: outputs_maps/swwa_<var>_anom_2023_2024.nc
```
7. Output Files
```
For each variable, the following files are produced:
swwa_<var>_monthly_2023_2024.nc      # raw monthly data
swwa_<var>_anom_2023_2024.nc         # anomalies vs 1971–2000
swwa_<var>_clim_1961_1990.nc         # climatology
swwa_<var>_clim_1971_2000.nc         # baseline climatology
swwa_<var>_clim_1995_2024.nc         # recent climatology
```

## Anomaly map plots creation workflow

### Scripts
- plot_agcd_anomalies_year_precip_maps_panel_noscale.py         (interim precip map plot to ascertain colour scale for final plot, month/year choice)
- plot_agcd_anomalies_year_precip_maps_panel_scale_landonly.py  (final precip map plot, set scale, month/year choice, masked to land only)
- plot_agcd_anomalies_year_precip_maps_panel_scale.py           (interim precip map plot, set scale, month/year choice, no land mask)
- plot_agcd_anomalies_year_tmax_maps_panel_noscale.py		    (interim tmax map plot to ascertain colour scale for final plot, no land mask)
- plot_agcd_anomalies_year_tmax_maps_panel_scale_landonly.py	(final tmax map plot, set scale, month/year choice, masked to land only)
- plot_agcd_anomalies_year_tmin_maps_panel_noscale.py		    (interim tmin map plot to ascertain colour scale for final plot, no land mask)
- plot_agcd_anomalies_year_tmin_maps_panel_scale_landonly.py	(final tmin map plot, set scale, month/year choice, masked to land only)
- plot_agcd_anomalies_year_vpd15_maps_panel_noscale.py		    (interim vpd15 map plot to ascertain colour scale for final plot, no land mask)
- plot_agcd_anomalies_year_vpd15_maps_panel_scale_landonly.py	(final vpd15 map plot, set scale, month/year choice, masked to land only)
