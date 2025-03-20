import os
import subprocess
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

class DataProcessor:
    def __init__(self, ui):
        self.ui = ui
        self.json_input = None

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
            self.model_thread = ModelRunnerThread(self.json_input, self.logger)
            self.model_thread.output_signal.connect(self.logger.log)  # Log progress and other output
            #self.model_thread.error_signal.connect(self.logger.log)  # Log errors as well
            self.model_thread.finished.connect(self.finish_model_run)
            self.model_thread.start()  # Start the model thread

        else:
            self.ui.status_bar.showMessage("Choose an input file first")



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

class ModelRunnerThread(QThread):
    output_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, input_json, logger):
        super().__init__()
        self.input_json = input_json
        self.logger = logger  # Use QTextEditLogger instance

    def run(self):
        try:
            from cuwalid.dryp.main_DRYP import run_DRYP

            # Make sure sys.stdout is redirected to QTextEditLogger before model runs
            if sys.stdout is None:
                sys.stdout = self.logger
            if sys.stderr is None:
                sys.stderr = self.logger

            # Run the model (output now goes to the QTextEdit widget)
            run_DRYP(self.input_json)

        except Exception as e:
            # Catch the error and send it to the QTextEdit widget
            error_message = f"Error running model: {e}\n{traceback.format_exc()}"
            self.error_signal.emit(error_message)  # Send error message to UI

            # Optionally log the error message in a file as well (you can remove this if you don't want a log file)
            log_path = os.path.join(os.getcwd(), "error_log.txt")
            with open(log_path, "w") as log_file:
                log_file.write(error_message)

            sys.__stderr__.write(error_message)  # Also print to terminal
            sys.__stderr__.flush()

        finally:
            # Restore stdout and stderr after the model completes
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__


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



