import os
import sys
import traceback
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem, QApplication
from PyQt6.QtGui import QTextCursor
from cuwalid.dryp.main_DRYP import run_DRYP
from shapely.geometry import mapping

class DataProcessor:
    def __init__(self, ui):
        self.ui = ui
        self.json_input = None

    def load_raster(self):
        filename, _ = QFileDialog.getOpenFileName(self.ui, "Open Raster File", "", "ASCII Files (*.asc)")
        if filename:
            self.ui.show_loading("Loading raster file...")
            self.ui.status_bar.showMessage(f"Loading raster: {filename}")
            self.ui.raster_file_label.setText(f"Loaded: {filename.split('/')[-1]}")  # Update label
            self.ui.raster_checkbox.setEnabled(True)
            self.ui.final_plot_button.setEnabled(True)
            QTimer.singleShot(100, lambda: self.process_raster_with_loading(filename))

    def process_raster_with_loading(self, file_path):
        try:
            with rasterio.open(file_path) as src:
                data = src.read(1)
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
            self.ui.raster_data = (data, extent)
            self.ui.status_bar.showMessage(f"Raster loaded successfully: {file_path}")
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error loading raster: {e}")
        finally:
            self.ui.hide_loading()

    def load_shapefile(self):
        filename, _ = QFileDialog.getOpenFileName(self.ui, "Open Shapefile", "", "Shapefiles (*.shp)")
        if filename:
            self.ui.show_loading("Loading shapefile...")
            self.ui.status_bar.showMessage(f"Loading Shapefile: {filename}")
            self.ui.shapefile_file_label.setText(f"Loaded: {filename.split('/')[-1]}")  # Update label
            self.ui.shapefile_checkbox.setEnabled(True)
            self.ui.final_plot_button.setEnabled(True)
            QTimer.singleShot(100, lambda: self.process_shapefile_with_loading(filename))

    def load_xy(self):
        filename, _ = QFileDialog.getOpenFileName(self.ui, "Open XY Data", "", "CSV Files (*.csv)")
        if filename:
            self.ui.show_loading("Loading XY data...")
            self.ui.status_bar.showMessage(f"Loading XY Data: {filename}")
            self.ui.xy_file_label.setText(f"Loaded: {filename.split('/')[-1]}")  # Update label
            self.ui.xy_checkbox.setEnabled(True)
            self.ui.final_plot_button.setEnabled(True)
            QTimer.singleShot(100, lambda: self.process_xy_with_loading(filename))

    def process_xy_with_loading(self, filename):
        try:
            # Read the CSV file
            df = pd.read_csv(filename)

            # Ensure 'North' and 'East' columns exist
            if {"North", "East"}.issubset(df.columns):
                self.ui.xy_data = df  # Store in UI for later use
                
                # Check for a third column (excluding 'North' and 'East')
                extra_cols = [col for col in df.columns if col not in {"North", "East"}]
                label_column = extra_cols[0] if extra_cols else None  # Use the first extra column if available

                self.ui.xy_labels = label_column
                
                self.ui.status_bar.showMessage(f"XY Data loaded successfully: {filename}")
            else:
                self.ui.status_bar.showMessage("Error: CSV must contain 'North' and 'East' columns.")
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error loading XY data: {e}")
        finally:
            self.ui.hide_loading()

    def process_shapefile_with_loading(self, filename):
        try:
            # Reading shapefile directly, no file locking by default
            gdf = gpd.read_file(filename)
            self.ui.shapefile_data = gdf
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
            self.ui.netcdf_file_label.setText(f"Loaded: {filename.split('/')[-1]}")  # Update label
            QTimer.singleShot(100, lambda: self.process_netcdf_with_loading(filename))

    def process_netcdf_with_loading(self, filename):
        try:
            with xr.open_dataset(filename) as ds:
                # Fully load into memory and detach from file
                loaded_ds = ds.load()

            self.ui.netcdf_dataset = loaded_ds  # Now it's memory-only, file can be closed
            self.ui.netcdf_path = filename  
            
            numeric_vars = [
                var for var in loaded_ds.data_vars 
                if loaded_ds[var].ndim in [2, 3] 
                and np.issubdtype(loaded_ds[var].dtype, np.number)
            ]

            if numeric_vars:
                self.ui.netcdf_var_selector.clear()
                self.ui.netcdf_var_selector.addItems(numeric_vars)
                self.ui.netcdf_var_selector.setEnabled(True)
                self.ui.plot_netcdf_button.setEnabled(True)
                self.ui.status_bar.showMessage(f"NetCDF loaded successfully: {filename}")
            else:
                self.ui.status_bar.showMessage("No plottable numeric data found in NetCDF file.")
                self.ui.plot_netcdf_button.setEnabled(False)

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
        self.json_input = filename
        self.ui.status_bar.showMessage(f"JSON file loaded successfully: {filename}")
        self.ui.hide_loading()

    def run_model(self):
        if self.json_input:
            self.ui.show_loading("Running model...")
            self.ui.status_bar.showMessage("Running model simulation...")

            # Create the logger (only one instance)
            self.logger = QTextEditLogger(self.ui.model_output)

            # Create and start the model thread, passing the logger
            self.model_thread = ModelRunnerThread(self.json_input)
            self.model_thread.output_signal.connect(self.logger.log)  # Log progress and other output
            self.model_thread.error_signal.connect(self.logger.log)  # Log errors as well
            self.model_thread.finished.connect(self.finish_model_run)
            self.model_thread.start()  # Start the model thread

        else:
            self.ui.status_bar.showMessage("Choose an input file first")


    def finish_model_run(self):
        self.ui.status_bar.showMessage("Model simulation completed")
        self.ui.hide_loading()

    def load_csv(self, dataset_num):
        file_path, _ = QFileDialog.getOpenFileName(self.ui, "Load CSV File", "", "CSV Files (*.csv)")

        if file_path:
            data = pd.read_csv(file_path)
            
            # Remove 'Date' column if present
            columns = [col for col in data.columns if col.lower() != "date"]
            file_name = os.path.basename(file_path)
            
            if dataset_num == 1:
                self.ui.csv_file_label_1.setText(file_name)  # Store file path
                self.ui.csv_var_selector_1.clear()
                
                # Add items with checkboxes
                for i, column in enumerate(columns):
                    item = QListWidgetItem(column)
                    if i > 3:
                        item.setCheckState(Qt.CheckState.Unchecked)  # unchecked
                    else:
                        item.setCheckState(Qt.CheckState.Checked)  # checked
                    self.ui.csv_var_selector_1.addItem(item)
                
                self.ui.csv_var_selector_1.setEnabled(True)
                self.ui.y_axis_label_1.setEnabled(True)  # Enable Y-axis title input
                self.ui.select_all_csv1_checkbox.setEnabled(True)
                
                # Store the DataFrame in csv_dataframe_1
                self.ui.csv_dataframe_1 = data
            else:
                self.ui.csv_file_label_2.setText(file_name)  # Store file path
                self.ui.csv_var_selector_2.clear()
                
                # Add items with checkboxes
                for i, column in enumerate(columns):
                    item = QListWidgetItem(column)
                    if i > 3:
                        item.setCheckState(Qt.CheckState.Unchecked)  # unchecked
                    else:
                        item.setCheckState(Qt.CheckState.Checked)  # checked
                    self.ui.csv_var_selector_2.addItem(item)
                
                self.ui.csv_var_selector_2.setEnabled(True)
                self.ui.y_axis_label_2.setEnabled(True)  # Enable Y-axis title input
                self.ui.select_all_csv2_checkbox.setEnabled(True)
                
                # Store the DataFrame in csv_dataframe_2
                self.ui.csv_dataframe_2 = data

            # Enable plot button if at least one dataset is loaded
            if self.ui.csv_file_label_1.text() != "No file loaded" or self.ui.csv_file_label_2.text() != "No file loaded":
                self.ui.plot_csv_button.setEnabled(True)

    def extract_point_data(self):
        try:
            self.ui.show_loading("Extracting point data from NetCDF...")

            points_df = self.ui.points_csv_data
            selected_indices = [
                i for i in range(self.ui.point_selector_list.count())
                if self.ui.point_selector_list.item(i).checkState() == Qt.CheckState.Checked
            ]

            if not selected_indices:
                self.ui.status_bar.showMessage("No points selected.")
                return

            selected_points = []
            for idx in selected_indices:
                row = points_df.iloc[idx]
                x = row['East']
                y = row['North']
                label = row.get('Label', f"P{idx}")
                selected_points.append((x, y, label))

            variable_name = self.ui.netcdf_var_selector.currentText()
            self.extract_netcdf_points(variable_name, selected_points)

        except Exception as e:
            self.ui.status_bar.showMessage(f"Error extracting point data: {e}")
        finally:
            self.ui.hide_loading()



    def extract_netcdf_points(self, variable_name, selected_points):
        try:
            self.ui.show_loading("Extracting point data from NetCDF...")
            dataset = self.ui.netcdf_dataset  # Assumes it's already loaded
            df = pd.DataFrame()
            df['Date'] = dataset['time'].values

            lon = dataset['lon'].values
            lat = dataset['lat'].values
            var = dataset[variable_name]

            for i, (x, y, label) in enumerate(selected_points):  # (East, North, OptionalLabel)
                ds_point = var.sel(lon=x, lat=y, method='nearest')
                column_name = f"{variable_name}_{label or i}"
                df[column_name] = ds_point.values

            # Save or update UI
            out_path, _ = QFileDialog.getSaveFileName(self.ui, "Save Extracted Data", "", "CSV Files (*.csv)")
            if out_path:
                df.to_csv(out_path, index=False)
                self.ui.status_bar.showMessage(f"Point data saved to: {out_path}")
            else:
                self.ui.status_bar.showMessage("Point extraction canceled by user.")
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error extracting NetCDF point data: {e}")
        finally:
            self.ui.hide_loading()

    def extract_netcdf_region(self, variable_name):
        # Define the custom projection (same as used in your working script)
        custom_crs = "+proj=laea +lat_0=5 +lon_0=20 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"

        try:
            self.ui.show_loading("Extracting region data from NetCDF...")

            # Get the shapefile data from the UI. Force the CRS to be custom_crs without reprojecting.
            gdf = self.ui.shapefile_data
            if gdf is None or gdf.empty:
                self.ui.status_bar.showMessage("No shapefile loaded or shapefile is empty.")
                return

            # FORCE the shapefile's CRS to your custom projection (just like your working script)
            gdf = gdf.set_crs(custom_crs, allow_override=True)

            # Define a helper to read the correct variable from NetCDF
            def read_dataset(fname, var_name='tht'):
                if var_name == 'fch':
                    fname_rp = fname.split('.')[0] + "rp.nc"
                    data = xr.open_dataset(fname_rp)[var_name]
                elif var_name == 'dch':
                    fname_rp = fname.split('.')[0] + "rp.nc"
                    data = xr.open_dataset(fname)['rch'] - xr.open_dataset(fname_rp)['fch']
                else:
                    data = xr.open_dataset(fname)[var_name]
                return data

            # Define a helper to extract average time series over a polygon
            def extract_TS_dataset(data, gdf_geom, crs):
                # Set the spatial dimensions for rioxarray
                data = data.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=False)
                # Write the CRS (forcing it to use our custom projection)
                data = data.rio.write_crs(crs, inplace=False)
                
                # --- Optional Debug Print ---
                # print("Dataset bounds:", data.rio.bounds())
                # print("Polygon bounds:", gdf_geom.bounds)
                # -------------------------------

                # Clip to the polygon
                zone_data = data.rio.clip([mapping(gdf_geom)], crs=crs, drop=True)
                # Return the average value over the clipped zone
                return zone_data.mean(dim=("lat", "lon"), skipna=True).squeeze().values

            # Get the NetCDF file path and the pre-loaded dataset
            nc_path = self.ui.netcdf_path
            base_ds = self.ui.netcdf_dataset 
            df = pd.DataFrame()
            df['Date'] = base_ds['time'].values

            # Loop through each polygon in the shapefile
            for idx, geom in enumerate(gdf.geometry):
                print(f"Processing region {idx}...")
                # Read the dataset for the variable of interest
                data = read_dataset(nc_path, var_name=variable_name)
                # Extract the time series using the polygon and custom CRS
                ts = extract_TS_dataset(data, geom, custom_crs)
                df[f"{variable_name}_region_{idx}"] = ts

            # Save the results
            out_path, _ = QFileDialog.getSaveFileName(
                self.ui, "Save Region-Averaged Data", "", "CSV Files (*.csv)"
            )
            if out_path:
                df.to_csv(out_path, index=False)
                self.ui.status_bar.showMessage(f"Region data saved to: {out_path}")
            else:
                self.ui.status_bar.showMessage("Region extraction canceled.")

        except Exception as e:
            tb = traceback.format_exc()
            self.ui.status_bar.showMessage(f"Error extracting region data: {e}")
            print(tb)
        finally:
            self.ui.hide_loading()



    def extract_region_data(self):
        try:
            if self.ui.shapefile_data is None:
                self.ui.status_bar.showMessage("No shapefile loaded.")
                return

            variable_name = self.ui.netcdf_var_selector.currentText()
            self.extract_netcdf_region(variable_name)

        except Exception as e:
            self.ui.status_bar.showMessage(f"Error extracting region data: {e}")


    def upload_extract_points_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self.ui, "Load Points CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return

        try:
            points_df = pd.read_csv(file_path)

            if 'East' not in points_df.columns or 'North' not in points_df.columns:
                self.ui.status_bar.showMessage("CSV must contain 'East' and 'North' columns.")
                return

            # Store loaded CSV in UI
            self.ui.points_csv_data = points_df

            # Populate the list widget for point selection
            self.ui.point_selector_list.clear()
            for i, row in points_df.iterrows():
                label = row.get('Label', f"Point {i}")
                item = QListWidgetItem(str(label))
                item.setCheckState(Qt.CheckState.Unchecked)
                self.ui.point_selector_list.addItem(item)

            self.ui.point_selector_list.setEnabled(True)
            self.ui.select_all_points_checkbox.setEnabled(True)
            self.ui.status_bar.showMessage("Points CSV loaded. Select points to extract.")

        except Exception as e:
            self.ui.status_bar.showMessage(f"Error loading points CSV: {e}")

    def upload_extract_shapefile(self):
        file_path, _ = QFileDialog.getOpenFileName(self.ui, "Load Shapefile", "", "Shapefiles (*.shp)")
        if not file_path:
            return

        try:
            gdf = gpd.read_file(file_path)
            self.ui.shapefile_data = gdf
            self.ui.status_bar.showMessage("Shapefile loaded. Ready to extract.")
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error loading shapefile: {e}")





class ModelRunnerThread(QThread):
    output_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, input_json):
        super().__init__()
        self.input_json = input_json

    def run(self):
        try:
            # Redirect standard output to capture messages
            sys.stdout = self
            sys.stderr = self

            # Run the model
            run_DRYP(self.input_json)

        except Exception as e:
            error_message = f"Error running model: {e}\n{traceback.format_exc()}"
            self.error_signal.emit(error_message)  # Send error message to UI
            #sys.__stderr__.write(error_message)  # Print to terminal

        finally:
            if sys.__stdout__ is not None:
                sys.stdout = sys.__stdout__
            if sys.__stderr__ is not None:
                sys.stderr = sys.__stderr__


    def write(self, message):
        """Emit output messages to the UI and print to terminal."""
        if message.strip():
            self.output_signal.emit(message)  # Emit message to UI
            if sys.__stdout__ is not None:  # Prevent NoneType error
                sys.__stdout__.write(message)

    def flush(self):
        """Ensure flushing works properly."""
        if sys.__stdout__ is not None:
            sys.__stdout__.flush()


class QTextEditLogger(QObject):
    update_signal = pyqtSignal(str)

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.update_signal.connect(self.log)  # Correct function name

    def log(self, message):
        """Append messages to the QTextEdit widget in a thread-safe way."""
        self.text_widget.moveCursor(QTextCursor.MoveOperation.End)
        self.text_widget.insertPlainText(message + "\n")  # Ensure new line
        self.text_widget.ensureCursorVisible()
        QApplication.processEvents()  # Force UI refresh

    def write(self, message):
        """Allows QTextEditLogger to be used as a file-like object."""
        if message.strip():  # Avoid empty messages
            self.update_signal.emit(message)  # Send message to UI
        # Write to the terminal as well, if available
        try:
            sys.__stdout__.write(message)  # Ensure we write to the terminal
            sys.__stdout__.flush()  # Flush output to the terminal
        except Exception as e:
            # In case the terminal isn't available, we handle the exception gracefully
            pass

    def flush(self):
        """Ensure that stdout flushes correctly."""
        try:
            sys.__stdout__.flush()  # Force flushing the output
        except Exception as e:
            # In case flushing fails, just handle the exception
            pass

