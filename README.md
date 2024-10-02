# SCHISM-DUCK-NC-RT

I completed the following simulations and uploaded the water elevation and wave height plots to Google Drive. 

| Model Configuration | Water Elevation | Wave Height | Directory in Hercules|
|---------------------|-----------------|-------------|-----------|
| Exp 1: SCHISM+WWM (reference) | [Link](https://drive.google.com/file/d/1n33MHJZcu_fMm1gNpaxsqTV3AVL-qtg8/view?usp=sharing) | [Link](https://drive.google.com/file/d/1gKLaCrhWWgu4PSlZj1FJF4lTCZ5Xinss/view?usp=sharing) | `/work/noaa/nosofs/mjisan/schism/schism_verification_tests/Test_WWM_Duck` |
| Exp 2: SCHISM+WWM+ATM | - | - | `/work/noaa/nosofs/mjisan/schism/schism_verification_tests/Test_WWM_Duck_ATM` |
| Exp 3: Standalone SCHISM | [Link](https://drive.google.com/file/d/1ApBnoB3-wkn5hJbB5xifKDh8HxVWHUBE/view?usp=sharing) | - | `/work/noaa/nosofs/mjisan/schism/schism_verification_tests/Test_DUCK_SCH` |
| Exp 4: Standalone SCHISM in UFS | [Link](https://drive.google.com/file/d/1OLqQNRfvI6Q1yXnooRbKqYXUCt3-EmbF/view?usp=drive_link) | - | `/work/noaa/nosofs/mjisan/ufs-weather-model/tests/stmp/mjisan/FV3_RT/RT_DUCK_NC_SCHISM_STD` |


# elev2D.th.nc

In the SCHISM Duck, NC RT case we are no longer using elev.th file. rather we will be using elev2D.th.nc 

SCHISM type 4 boundary conditions and the elev2D.th.nc file. Here are the key details about this type of boundary condition in SCHISM:

**Overview**

Type 4 boundary conditions in SCHISM are used to specify time-varying elevation at open boundaries4. The elev2D.th.nc file is one of the important input files for implementing these boundary conditions.

elev2D.th.nc File

The elev2D.th.nc file is a NetCDF file that contains the following:

Time-varying elevation data for open boundary nodes
Typically includes both tidal and sub-tidal components of water level variation5

**Key Characteristics
**Purpose: Directly specifies elevation at the ocean boundary5
Temporal Resolution: Usually hourly or sub-hourly time steps
Spatial Coverage: Values provided for each open boundary node
Format: NetCDF (Network Common Data Form)

SCHISM Required Files Table (Duck, NC RT 1994 Case)


| File Name | SCHISM Standalone | SCHISM + WWM | SCHISM + WWM + ATM |
|-----------|:-----------------:|:------------:|:------------------:|
| hgrid.gr3 | ✓ | ✓ | ✓ |
| vgrid.in | ✓ | ✓ | ✓ |
| param.nml | ✓ | ✓ | ✓ |
| bctides.in | ✓ | ✓ | ✓ |
| manning.gr3 | ✓ | ✓ | ✓ |
| elev.ic | ✓ | ✓ | ✓ |
| rough.gr3 | ✓ | ✓ | ✓ |
| elev2D.th.nc | ✓ | ✓ | ✓ |
| wwminput.nml | | ✓ | ✓ |
| wwmbnd.gr3 | | ✓ | ✓ |
| wwmbnd.XY | | ✓ | ✓ |
| windrot_geo2proj.gr3 | | ✓ | ✓ |
| sflux_air_1.0001.nc | | | ✓ |
| sflux_prc_1.0001.nc | | | ✓ |
| sflux_inputs.txt | | | ✓ |

Note: This table includes the core files typically required for each configuration. Additional files might be necessary depending on specific model setups and options chosen in the parameter files.

# Updated simulations with elev2D.th.nc file

| Model Configuration | Water Elevation | Wave Height | Directory in Hercules|
|---------------------|-----------------|-------------|-----------|
| Exp 1: SCHISM+WWM (reference) | [Link](https://drive.google.com/file/d/18gRHxzKsO1iyLROuvtO55io29yM7rfG3/view?usp=drive_link) | [Link](https://drive.google.com/file/d/1Pq8-iZryxGsdSQgXbkdereXSsBcX3eRm/view?usp=drive_link) | `/work/noaa/nosofs/mjisan/schism/schism_verification_tests/Test_WWM_Duck_Elev2D_SCH_WWM` |
| Exp 2: SCHISM+WWM+ATM | [Link](https://drive.google.com/file/d/1pL-jxQYC6Qh9Jtwo4UBfrUVgyl_3qSLv/view?usp=drive_link) | [Link](https://drive.google.com/file/d/1YpaiMf7jRh0PfHEUO8oFqvw3RxOTp3B8/view?usp=drive_link) | `/work/noaa/nosofs/mjisan/schism/schism_verification_tests/Test_WWM_Duck_Elev2D_SCH_WWM_ATM` |
| Exp 3: SCHISM+ATM | [Link](https://drive.google.com/file/d/1J1JJSXS9LXiWrYP_4Tu_jQ6Z6qsyclZN/view?usp=drive_link) | - | `/work/noaa/nosofs/mjisan/schism/schism_verification_tests/Test_WWM_Duck_Elev2D_SCH_ATM` |
| Exp 4: Standalone SCHISM | [Link](https://drive.google.com/file/d/1LtrI_gykxcsmXD7uwa8bnHpCby7_DCZW/view?usp=drive_link) | - | `/work/noaa/nosofs/mjisan/schism/schism_verification_tests/Test_WWM_Duck_Elev2D_SCH_ST` 

