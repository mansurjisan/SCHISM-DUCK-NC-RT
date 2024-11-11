import xarray as xr
import pandas as pd
import numpy as np
from metpy.units import units
from metpy.calc import wind_components

def read_wind_data(filename):
    """
    Read wind data from file with improved error handling and validation.
    """
    try:
        df = pd.read_csv(filename, sep='\s+', names=['date', 'time', 'speed', 'direction'])
        
        # Convert to numeric, replacing invalid values with NaN
        df['speed'] = pd.to_numeric(df['speed'], errors='coerce')
        df['direction'] = pd.to_numeric(df['direction'], errors='coerce')
        
        # Drop any rows with NaN values
        df = df.dropna()
        
        # Validate ranges
        df = df[(df['speed'] >= 0) & (df['speed'] < 100) &  # reasonable wind speed range
                (df['direction'] >= 0) & (df['direction'] <= 360)]  # valid direction range
        
        # Create datetime index
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        df = df.set_index('datetime')
        
        if df.empty:
            raise ValueError("No valid wind data after filtering")
            
        return df
        
    except Exception as e:
        raise Exception(f"Error reading wind data: {str(e)}")

def calculate_wind_components(speed, direction):
    """
    Calculate U and V components using MetPy with error handling.
    """
    try:
        speed = np.clip(speed, 0, 100) * units('m/s')  # clip to reasonable range
        direction = np.clip(direction, 0, 360) * units('degrees')
        u, v = wind_components(speed, direction)
        return float(u.magnitude), float(v.magnitude)
    except Exception as e:
        raise Exception(f"Error calculating wind components: {str(e)}")

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

def interpolate_era5_with_obs_wind(ds, wind_df, n_timesteps=None):
    """
    Interpolate ERA5 data to 30-minute intervals with fixed MSL interpolation
    """
    try:
        # Validate inputs
        if ds is None or wind_df is None or wind_df.empty:
            raise ValueError("Invalid input data")

        # Set n_timesteps if not provided
        if n_timesteps is None:
            n_timesteps = len(ds.valid_time)
        
        print(f"Processing {n_timesteps} timesteps...")

        # Limit to specified number of timesteps
        ds = ds.isel(valid_time=slice(0, n_timesteps))

        # Create new time array with 30-min intervals
        time_orig = pd.to_datetime(ds.valid_time.values, unit='s')
        time_new = pd.date_range(start=time_orig[0], end=time_orig[-1], freq='30min')

        # Process wind observations
        wind_df = process_wind_observations(wind_df)
        
        # Ensure wind observations cover the required time period
        wind_df = wind_df.reindex(pd.date_range(start=time_orig[0],
                                               end=time_orig[-1],
                                               freq='30min'))
        
        # Interpolate wind components
        wind_df = wind_df.interpolate(method='linear')

        # Convert times to unix timestamp for xarray
        time_new_unix = (time_new - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")

        # Initialize new dataset
        ds_new = xr.Dataset(
            coords={
                'valid_time': time_new_unix,
                'latitude': ds.latitude,
                'longitude': ds.longitude
            }
        )

        # Interpolate MSL using manual interpolation
        print("Interpolating msl...")
        msl_data = ds['msl'].values
        new_msl = np.zeros((len(time_new),) + msl_data.shape[1:])

        # Manual interpolation for MSL
        for i in range(len(msl_data)-1):
            idx = i * 2
            new_msl[idx] = msl_data[i]
            if idx + 1 < len(time_new):
                new_msl[idx + 1] = (msl_data[i] + msl_data[i + 1]) / 2
        if len(time_new) > 0:
            new_msl[-1] = msl_data[-1]

        # Add MSL to new dataset with proper dimensions
        ds_new['msl'] = (('valid_time', 'latitude', 'longitude'), new_msl)
        ds_new['msl'].attrs = ds['msl'].attrs

        # Create wind component arrays
        u_data = np.zeros((len(time_new),) + ds['u10'].shape[1:])
        v_data = np.zeros((len(time_new),) + ds['v10'].shape[1:])

        print(f"Creating new file with {len(time_new)} 30-minute timesteps")
        print(f"Available wind data has {len(wind_df)} entries")

        # Fill wind component arrays with interpolated observations
        for t in range(len(time_new)):
            u_data[t,:,:] = wind_df['u10'].iloc[t]
            v_data[t,:,:] = wind_df['v10'].iloc[t]

            if t % 10 == 0:  # Reduce output frequency
                print(f"Timestep {t+1}/{len(time_new)}")
                print(f"U10={wind_df['u10'].iloc[t]:.2f} m/s, V10={wind_df['v10'].iloc[t]:.2f} m/s")

        # Add wind components to new dataset
        ds_new['u10'] = (('valid_time', 'latitude', 'longitude'), u_data)
        ds_new['v10'] = (('valid_time', 'latitude', 'longitude'), v_data)

        # Copy variable attributes
        ds_new['u10'].attrs = ds['u10'].attrs
        ds_new['v10'].attrs = ds['v10'].attrs

        # Copy remaining variables
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

    except Exception as e:
        raise Exception(f"Error in interpolation: {str(e)}")

if __name__ == "__main__":
    try:
        print("Reading ERA5 data...")
        ds = xr.open_dataset('era5_data_20121027_20121029.nc')

        print("Reading wind observations...")
        wind_df = read_wind_data('spd_dir2.txt')

        print("Performing interpolation and wind component calculation...")
        ds_30min = interpolate_era5_with_obs_wind(ds, wind_df)

        print("Renaming valid_time to time...")
        ds_30min = ds_30min.rename({'valid_time': 'time'})

        print("Inverting latitudes...")
        ds_30min = ds_30min.reindex(latitude=ds_30min.latitude[::-1])

        # Flip data arrays along latitude dimension
        for var in ds_30min.data_vars:
            if 'latitude' in ds_30min[var].dims:
                ds_30min[var] = ds_30min[var].reindex(latitude=ds_30min.latitude)

        print("Saving interpolated data...")
        encoding = {
            'time': {'dtype': 'int64', '_FillValue': None},
            'u10': {'dtype': 'float32', '_FillValue': -9999.0},
            'v10': {'dtype': 'float32', '_FillValue': -9999.0},
            'msl': {'dtype': 'float32', '_FillValue': -9999.0}
        }

        ds_30min.to_netcdf('era5_data_30min_obs_wind_rot_fix_filled2.nc', encoding=encoding)

        print("Done!")
        print(f"Original times: {len(ds.valid_time)} points")
        print(f"Interpolated times: {len(ds_30min.time)} points")

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
