import xarray as xr
file_path = "elev2D.th.nc"
ds = xr.open_dataset(file_path)
print(ds)
tt1 = ds.time_series.isel(nOpenBndNodes=0, nLevels=0, nComponents=0)
print(f"Variable: tt1")
print(f"Type: {tt1.dtype}")
print(f"Total Size: {tt1.nbytes} bytes")
print(f"Number of Dimensions: {tt1.ndim}")
print(f"Dimensions and sizes: {tt1.dims}")
print(f"Coordinates: time: [{tt1.time.min().values}..{tt1.time.max().values}]")

# Loop through and print the values with their corresponding index
for idx, value in enumerate(tt1.values):
    print(f"({idx}) {value}")

