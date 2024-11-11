# Interpolating Observed Wind Data into ERA5 Grid

## Prerequisites

```python
import xarray as xr
import pandas as pd
import numpy as np
from metpy.units import units   # I used metpy functions to calculate wind components from the provided wind speed and directions. I am not sure whether we can use wind speed and direction directly as input parameters in CDEPS. 
from metpy.calc import wind_components
```

Required input files:
- ERA5 netCDF file (e.g., 'era5_data_201210_sandy.nc')   . This is the original ERA5 data for Hurricane Sandy over which I interpolated the observed data. 

- Observed wind data file (space-separated text file with columns: date, time, speed, direction)

## Step 1: Reading and Validating Wind Observations

The script starts by reading and validating the observed wind data:

```python
def read_wind_data(filename):

    """
    Read wind data from observed wind speed and direction text file.
    """
    # space-separated file with columns: date, time, speed, direction

    df = pd.read_csv(filename, sep='\s+', names=['date', 'time', 'speed', 'direction'])
    
    # Convert to numeric, replacing invalid values with NaN

    df['speed'] = pd.to_numeric(df['speed'], errors='coerce')
    df['direction'] = pd.to_numeric(df['direction'], errors='coerce')
    
    # Remove invalid entries

    df = df.dropna()
    
    # Sanity check 

    df = df[(df['speed'] >= 0) & (df['speed'] < 100) &  # reasonable wind speed range
            (df['direction'] >= 0) & (df['direction'] <= 360)]  # valid direction range
    
    # datetime index

    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    df = df.set_index('datetime')
    
    return df
```

## Step 2: Converting Wind Components 

Convert observed wind speed and direction to U and V components:

```python

def calculate_wind_components(speed, direction):

    """
    Calculate U and V components using MetPy with error handling.
    """
    speed = np.clip(speed, 0, 100) * units('m/s')  # clip to reasonable range

    direction = np.clip(direction, 0, 360) * units('degrees')

    u, v = wind_components(speed, direction)

    return float(u.magnitude), float(v.magnitude)
```
## Step 3: Processing Wind Observations

Create time series of U and V components from observations:

```python

def process_wind_observations(wind_df):
 
   """
    Process wind observations to create time series of U and V components
    """
    u_series = []
    v_series = []
    
    for idx, row in wind_df.iterrows():
        u, v = calculate_wind_components(row['speed'], row['direction'])
        u_series.append(u)
        v_series.append(v)
    
    wind_df['u10'] = u_series
    wind_df['v10'] = v_series
    
    return wind_df
```

## Step 4: Main Interpolation Process

The main interpolation function handles multiple aspects of data processing:

```python
def interpolate_era5_with_obs_wind(ds, wind_df, n_timesteps=None):


    """

    Interpolate observed wind data in to ERA5 grid with 30-minute intervals.

    """

    # 4.1: Initial Setup

    if n_timesteps is None:
        n_timesteps = len(ds.valid_time)
    
    # Limit to specified number of timesteps

    ds = ds.isel(valid_time=slice(0, n_timesteps))
    
    # 4.2: Time Handling

    # Create new time array with 30-min intervals

    time_orig = pd.to_datetime(ds.valid_time.values, unit='s')

    time_new = pd.date_range(start=time_orig[0], 
                            end=time_orig[-1], 
                            freq='30min')
    
    # Convert to unix timestamp for xarray

    time_new_unix = (time_new - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")
    
    # 4.3: Wind Observation Processing

    # Process wind observations to get U/V components

    wind_df = process_wind_observations(wind_df)
    
    # Ensure wind observations cover the required time period

    wind_df = wind_df.reindex(pd.date_range(start=time_orig[0],
                                           end=time_orig[-1],
                                           freq='30min'))
    
    # Interpolate any gaps in wind data

    wind_df = wind_df.interpolate(method='linear')
    
    # 4.4: Initialize New Dataset

    ds_new = xr.Dataset(
        coords={
            'valid_time': time_new_unix,
            'latitude': ds.latitude,
            'longitude': ds.longitude
        }
    )
    
    # 4.5: MSL Pressure Interpolation

    print("Interpolating msl...")

    msl_data = ds['msl'].values

    new_msl = np.zeros((len(time_new),) + msl_data.shape[1:])
    
    # Manual interpolation for MSL

    for i in range(len(msl_data)-1):
        idx = i * 2
        # Copy original hour value
        new_msl[idx] = msl_data[i]
        # Calculate interpolated value for 30-min mark
        if idx + 1 < len(time_new):
            new_msl[idx + 1] = (msl_data[i] + msl_data[i + 1]) / 2

    # Set final timestep

    if len(time_new) > 0:
        new_msl[-1] = msl_data[-1]
    
    # Add MSL to new dataset

    ds_new['msl'] = (('valid_time', 'latitude', 'longitude'), new_msl)
    ds_new['msl'].attrs = ds['msl'].attrs
    
    # 4.6: Wind Component Processing

    # Initialize wind component arrays

    u_data = np.zeros((len(time_new),) + ds['u10'].shape[1:])
    v_data = np.zeros((len(time_new),) + ds['v10'].shape[1:])
        
    # Fill wind component arrays with interpolated observations

    for t in range(len(time_new)):

        # Assign uniform wind field from observations

        u_data[t,:,:] = wind_df['u10'].iloc[t]
        v_data[t,:,:] = wind_df['v10'].iloc[t]
        
        if t % 10 == 0:  

            print(f"Timestep {t+1}/{len(time_new)}")
            print(f"U10={wind_df['u10'].iloc[t]:.2f} m/s, V10={wind_df['v10'].iloc[t]:.2f} m/s")
    
    # 4.7: Add Wind Components to Dataset

    ds_new['u10'] = (('valid_time', 'latitude', 'longitude'), u_data)
    ds_new['v10'] = (('valid_time', 'latitude', 'longitude'), v_data)
    
    # Copy variable attributes

    ds_new['u10'].attrs = ds['u10'].attrs
    ds_new['v10'].attrs = ds['v10'].attrs
    
    # 4.8: Copy Remaining Variables and Attributes

    # Copy any remaining variables

    for var in ds.variables:
        if var not in ['u10', 'v10', 'msl', 'valid_time', 'latitude', 'longitude']:
            ds_new[var] = ds[var]
    
    # Copy coordinate attributes

    for coord in ['latitude', 'longitude']:
        ds_new[coord].attrs = ds[coord].attrs
    
    # Set time attributes

    ds_new.valid_time.attrs = {
        'long_name': 'time',
        'standard_name': 'time',
        'units': 'seconds since 1970-01-01',
        'calendar': 'proleptic_gregorian'
    }
    
    # Copy global attributes

    ds_new.attrs = ds.attrs
    
    return ds_new
```

## Step 5: Final Processing and Output

1. Renaming valid_time to time
2. Inverting latitudes
3. Setting proper encoding for netCDF output
4. Explicit fill value specification in encoding

```python

# Rename valid_time to time

ds_30min = ds_30min.rename({'valid_time': 'time'})

# Invert latitudes

ds_30min = ds_30min.reindex(latitude=ds_30min.latitude[::-1])

# Set encoding for output

encoding = {
    'time': {'dtype': 'int64', '_FillValue': None},
    'u10': {'dtype': 'float32', '_FillValue': -9999.0},
    'v10': {'dtype': 'float32', '_FillValue': -9999.0},
    'msl': {'dtype': 'float32', '_FillValue': -9999.0}
}

# Save to netCDF
ds_30min.to_netcdf('era5_data_30min_obs_wind_rot_fix.nc', encoding=encoding)
```

