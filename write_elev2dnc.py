"""
This script generates an elev2D.th.nc (type 4 Boundary Condition) file for SCHISM model from grid files and timeseries data.
It reads hgrid.gr3 and vgrid.in files, processes open boundary information, and uses elev.th for timeseries data.
Usage: Ensure grid files and elev.th are in the specified paths, then run the script to create elev2D.th.nc.
"""

import os
import numpy as np
from netCDF4 import Dataset
from pyschism.mesh.hgrid import Hgrid
from pyschism.mesh.vgrid import Vgrid

def create_elev2d_th_nc(filename, timeseries_data, hgrid, vgrid):
    """
    Create elev2D.th.nc file from timeseries water elevation data.
    
    :param filename: Name of the output NetCDF file
    :param timeseries_data: 2D numpy array of shape (time, 2) with time and elevation data
    :param hgrid: Hgrid object from pyschism
    :param vgrid: Vgrid object from pyschism
    """
    open_boundaries = hgrid.boundaries.open
    nOpenBndNodes = sum(len(boundary) for boundary in open_boundaries['indexes'])
    
    time_data = timeseries_data[:, 0]
    elev_data = timeseries_data[:, 1]
    
    with Dataset(filename, 'w', format='NETCDF4') as nc:
        # Define dimensions
        nc.createDimension('nComponents', 1)
        nc.createDimension('nLevels', 1)
        nc.createDimension('time', None)  # unlimited dimension
        nc.createDimension('nOpenBndNodes', nOpenBndNodes)
        nc.createDimension('one', 1)
        
        # Create variables
        nComponents = nc.createVariable('nComponents', 'f8', ('nComponents',))
        nComponents.point_spacing = "even"
        nComponents.axis = "X"
        
        nLevels = nc.createVariable('nLevels', 'f8', ('nLevels',))
        nLevels.point_spacing = "even"
        nLevels.axis = "Y"
        
        time = nc.createVariable('time', 'f8', ('time',))
        time[:] = time_data
        
        time_series = nc.createVariable('time_series', 'f4', ('time', 'nOpenBndNodes', 'nLevels', 'nComponents'))
        for t in range(len(time_data)):
            time_series[t, :, 0, 0] = elev_data[t]
        
        time_step = nc.createVariable('time_step', 'f4', ('one',))
        time_step[:] = time_data[1] - time_data[0]  # uniform time step
        
        # Add global attributes
        nc.Conventions = "CF-1.6"
        nc.history = "Created by elev2D.th.nc generator script"

# Example usage
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fixed_files_dir = os.path.join(script_dir, 'fixed_files')
    
    hgrid_path = os.path.join(fixed_files_dir, 'hgrid.gr3')
    vgrid_path = os.path.join(fixed_files_dir, 'vgrid.in')
    
    hgrid = Hgrid.open(hgrid_path, crs='epsg:4326')
    vgrid = Vgrid.open(vgrid_path)
    
    timeseries_data = np.loadtxt('elev.th')
    
    create_elev2d_th_nc('elev2D.th.nc', timeseries_data, hgrid, vgrid)
    print("elev2D.th.nc file created successfully.")
