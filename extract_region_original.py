import os
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
import xarray as xr
import rasterio
import rioxarray
import geopandas as gpd
from shapely.geometry import mapping

def read_dataset(fname, var_name='tht'):
    # Open the first netCDF file
    # output dataset
    if var_name == 'fch':
        fname = fname.split('.')[0] + "rp.nc"
    elif var_name == "dch":
        fnamerp = fname.split('.')[0] + "rp.nc"

    if var_name == "dch":
        data = xr.open_dataset(fname)['rch'] - xr.open_dataset(fnamerp)['fch']
    else:
        data = xr.open_dataset(fname)
        data = data[var_name]
    return data

def extract_TS_dataset(data, mask=None, gdf_shp=None, crs=None):
    if mask is not None:
        zone_data = data.where(mask)  # .sel(time=slice('start_time', 'end_time'))
    elif gdf_shp is not None:
        data.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
        zone_data = data.rio.clip([mapping(gdf_shp)], crs, drop=True)


    # aggregate data
    zone_data = zone_data.mean(dim=('lat', 'lon'), skipna=True).squeeze()
    return zone_data.values

def extract_shp_zone_TS_from_dataset(data, mask=None, gdf_shp=None, crs=None, field=['twsc']):
    # create dataframe
    df = pd.DataFrame()
    df['Date'] = data['time']
    
    # hillslope
    for ifield in field:       
        df[ifield] = extract_TS_dataset(
            data, mask=mask, gdf_shp=gdf_shp, crs=crs
        )
    return df

def extract_raster_zone_TS_from_netcdf(fname, mask, field=['twsc']):
    # create dataframe
    df = pd.DataFrame()
    df['Date'] = read_dataset(fname)['time']
    
    # hillslope
    for ifield in field:       
        df[ifield] = extract_TS_dataset(
            read_dataset(fname, var_name=ifield),
            mask
        )
    return df

def get_mask(fmask):
    # output an array
    # get a mask
    mask = rasterio.open(fmask).read(1)
    # mask values for visualization
    mask = np.array(mask, dtype=float)
    mask[mask <= 0] = np.nan
    return mask

#========================================================
# calculate aridity index
# save in only one file all variables

# Read mask
fmask = "/home/c1755103/HAD/input/HAD_mask_utm_m_no_lakes.asc"
shapefile_path = "C:/Users/leoco/Downloads/leo_test/leo_test.shp"
# select variable
field = ['pre']

# specified projection
newPP = '+proj=laea +lat_0=5 +lon_0=20 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'

# Load the shapefile
gdf = gpd.read_file(shapefile_path)
gdf = gdf.set_crs(newPP, allow_override=True)

print(f"Number of regions (polygons): {len(gdf)}")


# directory for storing results
fout = ""

fname = "C:/Users/leoco/Downloads/EW_IM_chd_Sim_169_grid.nc"

# model name
imodel = "IMERGbc_sim0"

# Loop through each polygon
dfall = pd.DataFrame()  # Initialize the dfall variable for the final results
for index, igdf in gdf.iterrows():
    igdf = igdf.geometry  # Extract polygon geometry
    region_name = igdf["BASIN_NAME"] if "BASIN_NAME" in gdf.columns else f"Region_{index}"
    print("Processing region:", region_name)
    
    # extract data as average values from zone
    if os.path.exists(fname):
        # create a new dataframe
        df = pd.DataFrame()
        first_read_df = True

        for ifield in field:  # Loop over fields like 'dch'
            ds = read_dataset(fname, var_name=ifield)
            # Ensure the NetCDF dataset has spatial coordinates
            ds = ds.rio.write_crs(newPP)  # Adjust CRS if necessary
            
            # Extract data and append to dataframe
            df = extract_shp_zone_TS_from_dataset(
                    ds, gdf_shp=igdf, field=[ifield], crs=gdf.crs
                    )
            # Append each region's data to the final DataFrame
            dfall = pd.concat([dfall, df], ignore_index=True)

# Save final results
fname_csv = fout + 'fname_netcdf_avg_' + field[0] + ".csv"  
dfall.to_csv(fname_csv, index=False)
print(f"Results saved to {fname_csv}")
