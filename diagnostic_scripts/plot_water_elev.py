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

file_list = ['schout_elev_1.nc', 'schout_elev_2.nc', 'schout_elev_3.nc', 'schout_elev_4.nc',
             'schout_elev_5.nc', 'schout_elev_6.nc', 'schout_elev_7.nc', 'schout_elev_8.nc',
             'schout_elev_9.nc', 'schout_elev_10.nc', 'schout_elev_11.nc', 'schout_elev_12.nc',
             'schout_elev_13.nc', 'schout_elev_14.nc', 'schout_elev_15.nc', 'schout_elev_16.nc']

# Create output directory if it doesn't exist

output_dir = 'welev_maps'

os.makedirs(output_dir, exist_ok=True)

# Set the fixed colorbar range

VMIN = -1
VMAX = 3

# Define contour levels for better visualization

LEVELS = np.linspace(VMIN, VMAX, 61)  # 20 intervals between 0 and 20
print(LEVELS)
TICK_LEVELS = np.arange(VMIN, VMAX + 0.5, 0.5)

def plot_velocity(file_path, time_index, time_value):
    # Open the NetCDF file
    ds = xr.open_dataset(file_path)

    # Extract necessary variables
    x = ds.SCHISM_hgrid_node_x.values
    y = ds.SCHISM_hgrid_node_y.values
    elev = ds.elev.isel(time=time_index).values

    # Calculate wind speed magnitude
    elev = elev

    # Calculate true min/max
    elev_min = np.min(elev)
    elev_max = np.max(elev)
    print(f"Wind Speed Range: {elev_min:.2f} to {elev_max:.2f} m/s")

    # Create a regular grid for interpolation
    xi = np.linspace(x.min(), x.max(), 500)
    yi = np.linspace(y.min(), y.max(), 500)
    xi, yi = np.meshgrid(xi, yi)

    # Interpolate wind speed onto the regular grid
    zi = griddata((x, y), elev, (xi, yi), method='linear')

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

#    cbar = plt.colorbar(cf, ax=ax, orientation='vertical', pad=0.02)
#    cbar.set_label('water elevation (m)', fontsize=12)
#    cbar.ax.tick_params(labelsize=10)


    cbar = plt.colorbar(cf, ax=ax, orientation='vertical', pad=0.02, 
                       ticks=TICK_LEVELS)  # Set specific tick locations
    cbar.set_label('Water Elevation (m)', fontsize=12)
    cbar.ax.tick_params(labelsize=10)
    
    # Format colorbar tick labels to show one decimal place
    cbar.ax.set_yticklabels([f'{tick:.1f}' for tick in TICK_LEVELS])

    
    # Set title

    plt.title(f"Hurricane Sandy (2012) Water Elevation (With ATM Forcing)\n{time_value.strftime('%Y-%m-%d %H:%M')} UTC\nMax: {elev_max:.1f} m/s", 
              pad=15, fontsize=12)

    # Adjust layout

    plt.tight_layout()

    # Save the plot

    output_file = os.path.join(output_dir, f"welev_plot_{time_value.strftime('%Y%m%d_%H%M%S')}.png")
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
