import sys
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QSlider, QDialog, QMainWindow, QFileDialog, QInputDialog, QPushButton, QLabel, QVBoxLayout, QWidget, QGridLayout, QGroupBox, QStatusBar, QComboBox, QTabWidget, QStyle, QHBoxLayout, QSizePolicy)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

# Import CUWALID DRYP components
import cuwalid.dryp.components.DRYP_watershed as ppbasin
import cuwalid.tools.DRYP_pptools as pptools
import cuwalid.tools.DRYP_rrtools as rrtools

class HydroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("CUWALID Hydrological Model Helper")
        self.setGeometry(100, 100, 700, 500)
        
        # Create Tabs
        self.tabs = QTabWidget()
        self.model_tab = QWidget()
        self.visualization_tab = QWidget()
        self.tabs.addTab(self.model_tab, "Model Execution")
        self.tabs.addTab(self.visualization_tab, "Visualization")
        
        # Initialize Tabs
        self.init_model_tab()
        self.init_visualization_tab()
        
        self.setCentralWidget(self.tabs)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.netcdf_dataset = None
    
    def init_model_tab(self):
        layout = QVBoxLayout()
        
        self.load_json_button = QPushButton("Load Model Input JSON")
        self.load_json_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.load_json_button.clicked.connect(self.load_json)
        layout.addWidget(self.load_json_button)
        
        self.run_model_button = QPushButton("Run Hydrological Model")
        pixmapi = getattr(QStyle.StandardPixmap, "SP_MediaPlay")
        icon = self.style().standardIcon(pixmapi)
        self.run_model_button.setIcon(icon)
        self.run_model_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.run_model_button.clicked.connect(self.run_model)
        layout.addWidget(self.run_model_button)
        
        layout.addStretch()
        self.model_tab.setLayout(layout)
    
    def init_visualization_tab(self):
        layout = QGridLayout()
        
        self.load_dem_button = QPushButton("Load DEM File (ASCII .asc)")
        self.load_dem_button.clicked.connect(self.load_dem)
        layout.addWidget(self.load_dem_button, 0, 0)
        
        self.load_shapefile_button = QPushButton("Load Shapefile")
        self.load_shapefile_button.clicked.connect(self.load_shapefile)
        layout.addWidget(self.load_shapefile_button, 0, 1)
        
        self.load_netcdf_button = QPushButton("Load NetCDF File")
        self.load_netcdf_button.clicked.connect(self.load_netcdf)
        layout.addWidget(self.load_netcdf_button, 1, 0)
        
        self.netcdf_var_selector = QComboBox()
        self.netcdf_var_selector.currentIndexChanged.connect(self.plot_netcdf_variable)
        layout.addWidget(self.netcdf_var_selector, 1, 1)
        self.netcdf_var_selector.setEnabled(False)
        
        self.load_output_button = QPushButton("Load CSV")
        self.load_output_button.clicked.connect(self.load_output)
        layout.addWidget(self.load_output_button, 2, 0, 1, 2)
        
        layout.setRowStretch(3, 1)
        self.visualization_tab.setLayout(layout)
    
    def load_dem(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open DEM File", "", "ASCII Files (*.asc)")
        if filename:
            self.status_bar.showMessage(f"Loaded DEM: {filename}")
            self.process_raster(filename)

    def process_raster(self, file_path):
        with rasterio.open(file_path) as src:
            data = src.read(1)
            extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
        self.plot_raster(data, extent)

    def plot_raster(self, data, extent):
        try:
            # Clear any previous plots to avoid overlap
            plt.clf()  # Clear current figure
            plt.close('all')  # Close all figures
            
            print("Plotting DEM data...")
            fig, ax = plt.subplots()
            cax = ax.imshow(data, cmap='terrain', extent=extent, origin="upper")
            plt.colorbar(cax)
            plt.show()  # This will open the plot and let the user close it manually
        except Exception as e:
            self.status_bar.showMessage(f"Error plotting DEM: {e}")
            print(f"Error plotting DEM: {e}")
    
    def load_shapefile(self):
        # Clear any previous plots to avoid overlap
        plt.clf()  # Clear current figure
        plt.close('all')  # Close all figures
        filename, _ = QFileDialog.getOpenFileName(self, "Open Shapefile", "", "Shapefiles (*.shp)")
        if filename:
            self.status_bar.showMessage(f"Loaded Shapefile: {filename}")
            gdf = gpd.read_file(filename)
            gdf.plot()
            plt.show()  # Let the user close the shapefile plot manually
    
    def load_netcdf(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open NetCDF File", "", "NetCDF Files (*.nc)")
        if filename:
            self.status_bar.showMessage(f"Loaded NetCDF File: {filename}")
            self.netcdf_dataset = xr.open_dataset(filename)
            print("NetCDF Variables:")
            print(self.netcdf_dataset)

            # Find numeric variables that are 2D (lat, lon) or 3D (time, lat, lon)
            numeric_vars = [var for var in self.netcdf_dataset.data_vars 
                            if self.netcdf_dataset[var].ndim in [2, 3] 
                            and np.issubdtype(self.netcdf_dataset[var].dtype, np.number)]

            if numeric_vars:
                self.netcdf_var_selector.clear()
                self.netcdf_var_selector.addItems(numeric_vars)
                self.netcdf_var_selector.setEnabled(True)
            else:
                self.status_bar.showMessage("No plottable numeric data found in NetCDF file.")
    
    def plot_netcdf_variable(self):
        if self.netcdf_dataset is not None:
            var_name = self.netcdf_var_selector.currentText()
            if var_name:
                data = self.netcdf_dataset[var_name]

                if data.ndim == 2:
                    # Directly plot 2D data
                    plt.figure()
                    data.plot()
                    plt.show()  # Let the user close the plot manually

                elif data.ndim == 3:
                    # Clear previous plots before creating a new one
                    plt.clf()  # Clear current figure
                    plt.close('all')  # Close all figures

                    # Create a dialog window for the slider and plot
                    self.slider_window = QDialog(self)
                    self.slider_window.setWindowTitle("Time Step Selector")
                    self.slider_window.setGeometry(100, 100, 800, 600)

                    layout = QVBoxLayout()
                    
                    # Create Matplotlib figure and axes
                    self.fig, self.ax = plt.subplots()
                    self.canvas = FigureCanvasQTAgg(self.fig)  # Embed the figure in the PyQt app
                    
                    # Plot the first frame without adding a new colorbar
                    self.img = self.ax.imshow(data.isel(time=0), cmap="viridis", origin="lower")
                    self.colorbar = self.fig.colorbar(self.img, ax=self.ax)  # Create the colorbar once

                    # Create the slider
                    self.time_slider = QSlider(Qt.Orientation.Horizontal)
                    self.time_slider.setMinimum(0)
                    self.time_slider.setMaximum(data.sizes["time"] - 1)
                    self.time_slider.setValue(0)
                    self.time_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
                    self.time_slider.setTickInterval(1)
                    self.time_slider.valueChanged.connect(lambda: self.update_netcdf_plot(data))

                    # Add widgets to layout
                    layout.addWidget(self.canvas)
                    layout.addWidget(self.time_slider)

                    self.slider_window.setLayout(layout)
                    self.slider_window.show()

    def update_netcdf_plot(self, data):
        time_index = self.time_slider.value()

        # Update the image data instead of re-creating it
        self.img.set_data(data.isel(time=time_index))

        # Update the title
        self.ax.set_title(f"Time Step: {time_index}")

        # Redraw without adding a new colorbar
        self.canvas.draw()

    def load_json(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Model Input JSON", "", "JSON Files (*.json)")
        if filename:
            self.status_bar.showMessage(f"Loaded Model Input: {filename}")
    
    def run_model(self):
        self.status_bar.showMessage("Running model... (This will be implemented)")
    
    def load_output(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Simulation Output", "", "CSV Files (*.csv)")
        if filename:
            self.status_bar.showMessage(f"Loaded Output File: {filename}")
            self.visualize_output(filename)
    
    def visualize_output(self, file_path):
        df = pd.read_csv(file_path)
        plt.figure()
        plt.plot(df.iloc[:, 0], df.iloc[:, 1], label="Simulation Output")
        plt.xlabel("Time")
        plt.ylabel("Flow")
        plt.legend()
        plt.show()  # Let the user close the output plot manually

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HydroApp()
    window.show()
    sys.exit(app.exec())
