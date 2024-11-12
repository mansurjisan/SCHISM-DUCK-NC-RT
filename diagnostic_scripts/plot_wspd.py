import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import numpy as np
from scipy.interpolate import griddata
import os
import pandas as pd
import geocat.viz as gv

# List of NetCDF files

file_list = ['schout_wind_1.nc', 'schout_wind_2.nc', 'schout_wind_3.nc', 'schout_wind_4.nc',
             'schout_wind_5.nc', 'schout_wind_6.nc', 'schout_wind_7.nc', 'schout_wind_8.nc',
             'schout_wind_9.nc', 'schout_wind_10.nc', 'schout_wind_11.nc', 'schout_wind_12.nc',
             'schout_wind_13.nc', 'schout_wind_14.nc', 'schout_wind_15.nc', 'schout_wind_16.nc']

# Create output directory if it doesn't exist

output_dir = 'wspd_maps'

os.makedirs(output_dir, exist_ok=True)

# Set the fixed colorbar range

VMIN = 0
VMAX = 20

# Define contour levels for better visualization

LEVELS = np.linspace(VMIN, VMAX, 21)  # 20 intervals between 0 and 20

def plot_velocity(file_path, time_index, time_value):
    # Open the NetCDF file
    ds = xr.open_dataset(file_path)

    # Extract necessary variables
    x = ds.SCHISM_hgrid_node_x.values
    y = ds.SCHISM_hgrid_node_y.values
    wind = ds.wind_speed.isel(time=time_index).values

    # Calculate wind speed magnitude
    wind_speed = np.sqrt(wind[:, 0]**2 + wind[:, 1]**2)

    # Calculate true min/max
    speed_min = np.min(wind_speed)
    speed_max = np.max(wind_speed)
    print(f"Wind Speed Range: {speed_min:.2f} to {speed_max:.2f} m/s")

    # Create a regular grid for interpolation
    xi = np.linspace(x.min(), x.max(), 500)
    yi = np.linspace(y.min(), y.max(), 500)
    xi, yi = np.meshgrid(xi, yi)

    # Interpolate wind speed onto the regular grid
    zi = griddata((x, y), wind_speed, (xi, yi), method='linear')

    # Create figure and axes
    fig = plt.figure(figsize=(12, 8))
    projection = ccrs.PlateCarree()
    ax = plt.axes(projection=projection)

    # Set map extent with some padding
    padding = 0  # degrees
    ax.set_extent([
        x.min() - padding,
        x.max() + padding,
        y.min() - padding,
        y.max() + padding
    ])

    # Create filled contour plot
    cf = ax.contourf(xi, yi, zi,
                     levels=LEVELS,
                     transform=projection,
                     cmap='jet',
                     extend='max')

    # Add contour lines for better detail
    cs = ax.contour(xi, yi, zi,
                    levels=LEVELS[::2],  # Use fewer levels for contour lines
                    colors='black',
                    linewidths=0.5,
                    alpha=0.3,
                    transform=projection)

    # Add map features
    # Explicitly set axis labels with larger font size
    ax.text(-0.15, 0.5, 'Latitude', va='center', ha='center',
            rotation='vertical', transform=ax.transAxes, fontsize=12)
    ax.text(0.5, -0.05, 'Longitude', va='center', ha='center',
            transform=ax.transAxes, fontsize=12)


#    ax.coastlines(linewidth=0.5)
#    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
#    ax.add_feature(cfeature.STATES, linewidth=0.3)

    gl = ax.gridlines(draw_labels=True)
    gl.xlines = False  # Hide vertical gridlines
    gl.ylines = False  # Hide horizontal gridlines
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 12}
    gl.ylabel_style = {'size': 12}

    
    # Add colorbar

    cbar = plt.colorbar(cf, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label('Wind Speed (m/s)', fontsize=12)
    cbar.ax.tick_params(labelsize=10)

    # Set title

    plt.title(f"Hurricane Sandy (2012) Surface Wind Speed\n{time_value.strftime('%Y-%m-%d %H:%M')} UTC\nMax: {speed_max:.1f} m/s", 
              pad=15, fontsize=12)

    # Adjust layout

    plt.tight_layout()

    # Save the plot

    output_file = os.path.join(output_dir, f"wspd_plot_{time_value.strftime('%Y%m%d_%H%M%S')}.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    ds.close()

# Process files
for file_index, file_path in enumerate(file_list):
    print(f"\nProcessing {file_path}...")

    # Open the NetCDF file
    ds = xr.open_dataset(file_path)
    time_values = pd.to_datetime(ds.time.values)
    ds.close()

    # Process every timestep
    for time_index in range(len(time_values)):
        time_value = time_values[time_index]
        print(f"Processing time step {time_index + 1}: {time_value}")
        plot_velocity(file_path, time_index, time_value)

print("\nAnalysis complete. Check the 'wspd_maps' directory for output plots.")
