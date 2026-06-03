


# Directory Structure

|-- Dieoff_2024
	|-- figs		(all graph outputs)
	|-- mask		(coast and IBRA masks)
	|-- outputs		(all data outputs)
	|-- outputs_maps	(all map outputs)
	|-- scripts		(all calculation, plotting scripts)

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
- 1a_create_ibra7_swwaregion_shp.py
- 1b_create_ibra7_swwamask_clean_shp.py
- 1c_create_ibra7_swwamask_clean_nc.py
- 1d_bounds_agcd_anomaly_swwa.py
- 1e_create_ibra7_coast.py
- 1f_clean_ibra7_coast.py
- 1g_plot_ibra7_swwamask.py

## 2. Data preparation

### Scripts
- 2a_calc_mask_agcd_mth_mean_clim_tp.py
- 2b_calc_mask_agcd_mth_mean_clim_tmax.py
- 2c_calc_mask_agcd_mth_mean_clim_tmin.py
- 2d_calc_mask_agcd_mth_mean_clim_vpd09.py
- 2e_calc_mask_agcd_mth_mean_clim_vpd15.py
- 2f_calc_mask_agcd_mth_mean_clim_tmean.py
- 3a_calc_agcd_swwa_mth_mean_clim_precip.py
- 3b_calc_agcd_swwa_mth_mean_clim_tmax.py
- 3b_calc_agcd_swwa_mth_mean_clim_tmax_tmin_temp.py

## 3. Creation of the figures

### Scripts
- plot_agcd_anomalies_year_all_choice_timeseries.py
- plot_agcd_anomalies_year_all_timeseries.py
- plot_agcd_anomalies_year_precip_maps_panel_noscale.py		(interim precip map plot to ascertain colour scale for final plot, month/year choice)
- plot_agcd_anomalies_year_precip_maps_panel_scale_landonly.py	(final precip map plot, set scale, month/year choice, masked to land only)
- plot_agcd_anomalies_year_precip_maps_panel_scale.py		(interim precip map plot, set scale, month/year choice, no land mask)
- plot_agcd_anomalies_year_precip_maps.py			(???)
- plot_agcd_anomalies_year_precip_tmax_timeseries.py		(interim timeseries plot, precip-tmax only)
- plot_agcd_anomalies_year_precip_tmax_tmin_timeseries.py	(interim timeseries plot, precip-tmax-tmin only)
- plot_agcd_anomalies_year_precip_tmax_vpd15_timeseries.py	(interim timeseries plot, precip-tmax-vpd15 only)
- plot_agcd_anomalies_year_tmax_maps_panel_noscale.py		(interim tmax map plot to ascertain colour scale for final plot)
- plot_agcd_anomalies_year_tmax_maps_panel_scale_landonly.py	(final tmax map plot, set scale, month/year choice, masked to land only)
- plot_agcd_anomalies_year_tmean_maps_panel_noscale.py		(interim tmean map plot to ascertain colour scale for final plot)
- plot_agcd_anomalies_year_tmean_maps_panel_scale_landonly.py	(final tmean map plot, set scale, month/year choice, masked to land only)
- plot_agcd_anomalies_year_tmin_maps_panel_noscale.py		(interim tmin map plot to ascertain colour scale for final plot)
- plot_agcd_anomalies_year_tmin_maps_panel_scale_landonly.py	(final tmin map plot, set scale, month/year choice, masked to land only)
- plot_agcd_anomalies_year_vpd15_maps_panel_noscale.py		(interim tmin map plot to ascertain colour scale for final plot)
- plot_agcd_anomalies_year_vpd15_maps_panel_scale_landonly.py	(final tmin map plot, set scale, month/year choice, masked to land only)



















