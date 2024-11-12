#water elevation plotting code
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset, num2date
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import os

# List of NetCDF files
#file_list = ['schout_1.nc', 'schout_2.nc', 'schout_3.nc', 'schout_4.nc', 'schout_5.nc', 'schout_6.nc', 'schout_7.nc', 'schout_8.nc']
file_list = ['out2d_1.nc', 'out2d_2.nc', 'out2d_3.nc', 'out2d_4.nc', 'out2d_5.nc', 'out2d_6.nc', 'out2d_7.nc', 'out2d_8.nc']

# Create output directory if it doesn't exist
output_dir = 'elevation_maps'
os.makedirs(output_dir, exist_ok=True)

# Define contour levels from 0 to 1 with 50 levels for smoothness
contour_levels = np.linspace(0, 1, 50)

# Define colorbar ticks from 0 to 1 with 0.1 spacing
colorbar_ticks = np.arange(0, 1.1, 0.1)

# Loop over each file
for file_index, file_path in enumerate(file_list):
    print(f"Processing {file_path}...")

    # Open the NetCDF file
    dataset = Dataset(file_path, 'r')

    # Extract time, longitude, latitude, and elevation data
    time = dataset.variables['time'][:]
    time_units = dataset.variables['time'].units
    time_values = num2date(time, units=time_units)

    lon = dataset.variables['SCHISM_hgrid_node_x'][:]
    lat = dataset.variables['SCHISM_hgrid_node_y'][:]
    elevation = dataset.variables['elevation'][:]

    print(np.min(elevation))
    print(np.max(elevation))
    
    # Loop over all time steps in the file
    for time_index, time_value in enumerate(time_values):
        # Print the current time value
        print(f"Processing file {file_index + 1}, time step {time_index + 1}: {time_value.strftime('%Y-%m-%d %H:%M:%S')}")

        # Extract elevation for the current time step
        elevation_at_time = elevation[time_index, :]

        # Set up the plot with a geographical projection
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})

        # Plot the water elevation using tricontourf, with a fixed colorbar range from 0 to 1
        cs = ax.tricontourf(lon, lat, elevation_at_time, levels=contour_levels, cmap='jet',
                            vmin=0, vmax=1, transform=ccrs.PlateCarree())

        # Add coastlines, borders, and land features
#        ax.add_feature(cfeature.COASTLINE)
#        ax.add_feature(cfeature.BORDERS)
#        ax.add_feature(cfeature.LAND, facecolor='lightgray')

        # Add colorbar with fixed ticks from 0 to 1 with 0.1 spacing
        cbar = plt.colorbar(cs, ax=ax, orientation='vertical', pad=0.02, aspect=30, ticks=colorbar_ticks)
        cbar.set_label('Water Elevation (m)')

        # Format the longitude and latitude labels without gridlines
        ax.set_xticks(np.linspace(min(lon), max(lon), 5), crs=ccrs.PlateCarree())
        ax.set_yticks(np.linspace(min(lat), max(lat), 5), crs=ccrs.PlateCarree())
        ax.xaxis.set_major_formatter(LongitudeFormatter())
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        ax.tick_params(labelsize=10)

        # Set titles and labels
        ax.set_title(f"Water Elevation (SCHISM Standalone) at {time_value.strftime('%Y-%m-%d %H:%M:%S')}", fontsize=14)

        # Set extent based on your lat/lon ranges
        ax.set_extent([min(lon), max(lon), min(lat), max(lat)])

        # Save the plot to a file
        output_file = os.path.join(output_dir, f'elevation_map_file{file_index+1}_time{time_index+1}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')

        # Close the plot to free up memory
        plt.close()

    # Close the dataset
    dataset.close()

print("Elevation maps generated for all files and time steps.")
