import os
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
import xarray as xr
#import rasterio

def get_ts_point_from_netcdf(fname, x_coord, y_coord, field='dis'):
	# read model dataset
	data = xr.open_dataset(fname)
	data = data[field]
	time = data['time']
	# create dataframe
	df = pd.DataFrame()
	df['Date'] = time

	for i, ix_point in enumerate(x_coord):		
		# Select the grid point closest to the specified location
		ds_point = data.sel(lon=x_coord[i], lat=y_coord[i], method='nearest')
		df[field +"_"+str(i)] = ds_point.values

	return df

# filename poitns
fpoints = "/home/c1755103/WS/HAD/csv/location_points.csv"
points = pd.read_csv(fpoints)

#read netcdf file
fname = "D:/HAD_basins/basin_output/Tana_IM_sim_ini_grid.nc"

# select variable
field = ['pre', 'aet', 'tht', 'rch', 'twsc', "egw", "dis"]#tls', 'fch', 'dch']#
#field = ['dis']

# select regions
## EW Archres Post, Kenya model
## find coordinate for each coord
x_coord = points['East'].values
y_coord = points['North'].values

df = get_ts_point_from_netcdf(
	ifname,
	x_coord, y_coord,
	field=ifield)

# save pdf
fname_csv = "filename_netcdf_"+ifield+".csv"
df.to_csv(fname_csv, index=False)