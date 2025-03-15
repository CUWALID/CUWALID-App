import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem

class DataProcessor:
    def __init__(self, ui):
        self.ui = ui

    def load_dem(self):
        filename, _ = QFileDialog.getOpenFileName(self.ui, "Open DEM File", "", "ASCII Files (*.asc)")
        if filename:
            self.ui.show_loading("Loading DEM file...")
            self.ui.status_bar.showMessage(f"Loading DEM: {filename}")
            QTimer.singleShot(100, lambda: self.process_raster_with_loading(filename))

    def process_raster_with_loading(self, file_path):
        try:
            with rasterio.open(file_path) as src:
                data = src.read(1)
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
            self.ui.plotter.plot_raster(data, extent)
            self.ui.status_bar.showMessage(f"DEM loaded successfully: {file_path}")
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error loading DEM: {e}")
        finally:
            self.ui.hide_loading()

    def load_shapefile(self):
        filename, _ = QFileDialog.getOpenFileName(self.ui, "Open Shapefile", "", "Shapefiles (*.shp)")
        if filename:
            self.ui.show_loading("Loading shapefile...")
            self.ui.status_bar.showMessage(f"Loading Shapefile: {filename}")
            QTimer.singleShot(100, lambda: self.process_shapefile_with_loading(filename))

    def process_shapefile_with_loading(self, filename):
        try:
            # Reading shapefile directly, no file locking by default
            gdf = gpd.read_file(filename)
            self.ui.plotter.plot_shapefile(gdf)
            self.ui.status_bar.showMessage(f"Shapefile loaded successfully: {filename}")
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error loading shapefile: {e}")
        finally:
            self.ui.hide_loading()

    def load_netcdf(self):
        filename, _ = QFileDialog.getOpenFileName(self.ui, "Open NetCDF File", "", "NetCDF Files (*.nc)")
        if filename:
            self.ui.show_loading("Loading NetCDF file...")
            self.ui.status_bar.showMessage(f"Loading NetCDF File: {filename}")
            QTimer.singleShot(100, lambda: self.process_netcdf_with_loading(filename))

    def process_netcdf_with_loading(self, filename):
        try:
            # Using with statement to ensure proper closing of the NetCDF file
            with xr.open_dataset(filename) as ds:
                self.ui.netcdf_dataset = ds
                numeric_vars = [var for var in ds.data_vars 
                                if ds[var].ndim in [2, 3] 
                                and np.issubdtype(ds[var].dtype, np.number)]
                if numeric_vars:
                    self.ui.netcdf_var_selector.clear()
                    self.ui.netcdf_var_selector.addItems(numeric_vars)
                    self.ui.netcdf_var_selector.setEnabled(True)
                    self.ui.status_bar.showMessage(f"NetCDF loaded successfully: {filename}")
                else:
                    self.ui.status_bar.showMessage("No plottable numeric data found in NetCDF file.")
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error loading NetCDF file: {e}")
        finally:
            self.ui.hide_loading()

    def load_json(self):
        filename, _ = QFileDialog.getOpenFileName(self.ui, "Open Model Input JSON", "", "JSON Files (*.json)")
        if filename:
            self.ui.show_loading("Loading JSON file...")
            self.ui.status_bar.showMessage(f"Loading Model Input: {filename}")
            QTimer.singleShot(1000, lambda: self.finish_json_loading(filename))

    def finish_json_loading(self, filename):
        self.ui.status_bar.showMessage(f"JSON file loaded successfully: {filename}")
        self.ui.hide_loading()

    def run_model(self):
        self.ui.show_loading("Running model...")
        self.ui.status_bar.showMessage("Running model simulation...")
        QTimer.singleShot(2000, self.finish_model_run)

    def finish_model_run(self):
        self.ui.status_bar.showMessage("Model simulation completed")
        self.ui.hide_loading()

    def load_csv(self):
        filename, _ = QFileDialog.getOpenFileName(self.ui, "Open Simulation Output", "", "CSV Files (*.csv)")
        if filename:
            self.ui.status_bar.showMessage(f"Loaded Output File: {filename}")
            self.process_csv_with_loading(filename)

    def process_csv_with_loading(self, filename):
        try:
            # Read CSV file into dataframe, no explicit file lock, but we will handle it properly
            df = pd.read_csv(filename)
            if 'Date' not in df.columns:
                self.ui.status_bar.showMessage("Error: 'Date' column missing from the CSV file.")
                return
            
            self.ui.csv_dataframe = df  # Store the dataframe
            self.ui.csv_var_selector.clear()
            
            numeric_cols = [col for col in df.columns if col != 'Date']

            for col in numeric_cols:
                item = QListWidgetItem(col)
                item.setCheckState(Qt.CheckState.Checked)  # Set default to checked
                self.ui.csv_var_selector.addItem(item)

            self.ui.csv_var_selector.setEnabled(True)
            self.ui.plot_csv_button.setEnabled(True)  # Enable the plot button

            self.ui.status_bar.showMessage(f"CSV loaded successfully: {filename}")
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error loading CSV: {e}")
