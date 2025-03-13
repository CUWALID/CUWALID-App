import sys
import os
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QSlider, QDialog, QMainWindow, QFileDialog, QInputDialog, QPushButton, QLabel, QVBoxLayout, QWidget, QGridLayout, QGroupBox, QStatusBar, QComboBox, QTabWidget, QStyle, QHBoxLayout, QSizePolicy, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
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
        self.setGeometry(100, 100, 800, 600)  # Slightly larger default size
        
        # Set application-wide stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #2d2d2d;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #cccccc;
                padding: 8px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #555555;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c6e71;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #4d8f93;
            }
            QPushButton:pressed {
                background-color: #2a5254;
            }
            QComboBox {
                background-color: #3d3d3d;
                color: white;
                border-radius: 4px;
                padding: 6px;
                min-height: 30px;
            }
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 4px;
                background-color: #333333;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #3c6e71;
                width: 20px;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add logo banner at the top
        main_layout.addWidget(self.add_logo_banner())
        
        # Create a container for the tabs with proper margins
        tabs_container = QWidget()
        tabs_layout = QVBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)  # More modern look
        self.model_tab = QWidget()
        self.visualization_tab = QWidget()
        self.tabs.addTab(self.visualization_tab, "Visualization")
        self.tabs.addTab(self.model_tab, "Model Execution")
        
        
        # Initialize Tabs
        self.init_visualization_tab()
        self.init_model_tab()
        
        
        # Add tabs to tabs container
        tabs_layout.addWidget(self.tabs)
        
        # Add tabs container to main layout
        main_layout.addWidget(tabs_container)
        
        # Create a central widget to hold the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { background-color: #222222; color: #cccccc; }")
        self.setStatusBar(self.status_bar)
        
        # Loading indicator
        self.loading_label = QLabel("Loading data...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("font-weight: bold; color: #4d8f93;")
        self.loading_label.hide()
        self.status_bar.addPermanentWidget(self.loading_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)
        
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
        main_layout = QVBoxLayout()
        
        # Create a group box for file loading options
        file_group = QGroupBox("Data Files")
        file_layout = QGridLayout()
        
        # Add a small icon to buttons
        from PyQt6.QtGui import QIcon
        
        self.load_dem_button = QPushButton("Load DEM File (ASCII .asc)")
        self.load_dem_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_dem_button.clicked.connect(self.load_dem)
        file_layout.addWidget(self.load_dem_button, 0, 0)
        
        self.load_shapefile_button = QPushButton("Load Shapefile")
        self.load_shapefile_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_shapefile_button.clicked.connect(self.load_shapefile)
        file_layout.addWidget(self.load_shapefile_button, 0, 1)
        
        self.load_netcdf_button = QPushButton("Load NetCDF File")
        self.load_netcdf_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_netcdf_button.clicked.connect(self.load_netcdf)
        file_layout.addWidget(self.load_netcdf_button, 1, 0)
        
        # Add a label for the variable selector
        netcdf_layout = QHBoxLayout()
        netcdf_label = QLabel("NetCDF Variable:")
        netcdf_layout.addWidget(netcdf_label)
        
        self.netcdf_var_selector = QComboBox()
        self.netcdf_var_selector.currentIndexChanged.connect(self.plot_netcdf_variable)
        netcdf_layout.addWidget(self.netcdf_var_selector)
        file_layout.addLayout(netcdf_layout, 1, 1)
        self.netcdf_var_selector.setEnabled(False)
        
        self.load_output_button = QPushButton("Load CSV")
        self.load_output_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_output_button.clicked.connect(self.load_output)
        file_layout.addWidget(self.load_output_button, 2, 0, 1, 2)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        main_layout.addStretch()
        self.visualization_tab.setLayout(main_layout)
    
    def show_loading(self, message="Loading data..."):
        """Show loading indicator with custom message"""
        self.loading_label.setText(message)
        self.loading_label.show()
        self.progress_bar.show()
        self.update_buttons_state(False)  # Disable buttons while loading
        QApplication.processEvents()  # Force UI update
    
    def hide_loading(self):
        """Hide loading indicator"""
        self.loading_label.hide()
        self.progress_bar.hide()
        self.update_buttons_state(True)  # Re-enable buttons
    
    def update_buttons_state(self, enabled):
        """Enable or disable all buttons during loading"""
        # Visualization tab buttons
        self.load_dem_button.setEnabled(enabled)
        self.load_shapefile_button.setEnabled(enabled)
        self.load_netcdf_button.setEnabled(enabled)
        self.load_output_button.setEnabled(enabled)
        
        # Model tab buttons
        self.load_json_button.setEnabled(enabled)
        self.run_model_button.setEnabled(enabled)
    
    def load_dem(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open DEM File", "", "ASCII Files (*.asc)")
        if filename:
            self.show_loading("Loading DEM file...")
            self.status_bar.showMessage(f"Loading DEM: {filename}")
            
            # Using QTimer to give UI time to update before the potentially slow operation
            QTimer.singleShot(100, lambda: self.process_raster_with_loading(filename))
    
    def process_raster_with_loading(self, file_path):
        try:
            with rasterio.open(file_path) as src:
                data = src.read(1)
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
            
            self.plot_raster(data, extent)
            self.status_bar.showMessage(f"DEM loaded successfully: {file_path}")
        except Exception as e:
            self.status_bar.showMessage(f"Error loading DEM: {e}")
        finally:
            self.hide_loading()

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
        filename, _ = QFileDialog.getOpenFileName(self, "Open Shapefile", "", "Shapefiles (*.shp)")
        if filename:
            self.show_loading("Loading shapefile...")
            self.status_bar.showMessage(f"Loading Shapefile: {filename}")
            
            # Using QTimer to give UI time to update before the potentially slow operation
            QTimer.singleShot(100, lambda: self.process_shapefile_with_loading(filename))
    
    def process_shapefile_with_loading(self, filename):
        try:
            # Clear any previous plots to avoid overlap
            plt.clf()  # Clear current figure
            plt.close('all')  # Close all figures
            
            gdf = gpd.read_file(filename)
            gdf.plot()
            plt.show()  # Let the user close the shapefile plot manually
            self.status_bar.showMessage(f"Shapefile loaded successfully: {filename}")
        except Exception as e:
            self.status_bar.showMessage(f"Error loading shapefile: {e}")
        finally:
            self.hide_loading()
    
    def load_netcdf(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open NetCDF File", "", "NetCDF Files (*.nc)")
        if filename:
            self.show_loading("Loading NetCDF file...")
            self.status_bar.showMessage(f"Loading NetCDF File: {filename}")
            
            # Using QTimer to give UI time to update before the potentially slow operation
            QTimer.singleShot(100, lambda: self.process_netcdf_with_loading(filename))
    
    def process_netcdf_with_loading(self, filename):
        try:
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
                self.status_bar.showMessage(f"NetCDF loaded successfully: {filename}")
            else:
                self.status_bar.showMessage("No plottable numeric data found in NetCDF file.")
        except Exception as e:
            self.status_bar.showMessage(f"Error loading NetCDF file: {e}")
        finally:
            self.hide_loading()
    
    def plot_netcdf_variable(self):
        if self.netcdf_dataset is not None:
            var_name = self.netcdf_var_selector.currentText()
            if var_name:
                self.show_loading(f"Plotting {var_name}...")
                
                # Using QTimer to give UI time to update before the potentially slow operation
                QTimer.singleShot(100, lambda: self.process_netcdf_plot_with_loading(var_name))
    
    def process_netcdf_plot_with_loading(self, var_name):
        try:
            data = self.netcdf_dataset[var_name]

            if data.ndim == 2:
                # Directly plot 2D data
                plt.figure()
                data.plot()
                plt.show()  # Let the user close the plot manually
                self.status_bar.showMessage(f"Plotted variable: {var_name}")

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
                self.status_bar.showMessage(f"Plotted variable: {var_name}")
        except Exception as e:
            self.status_bar.showMessage(f"Error plotting NetCDF variable: {e}")
        finally:
            self.hide_loading()

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
            self.show_loading("Loading JSON file...")
            self.status_bar.showMessage(f"Loading Model Input: {filename}")
            
            # Simulate file loading (would be replaced by actual loading logic)
            QTimer.singleShot(1000, lambda: self.finish_json_loading(filename))
    
    def finish_json_loading(self, filename):
        self.status_bar.showMessage(f"JSON file loaded successfully: {filename}")
        self.hide_loading()
    
    def run_model(self):
        self.show_loading("Running model...")
        self.status_bar.showMessage("Running model simulation...")
        
        # Simulate model running (would be replaced by actual model execution)
        QTimer.singleShot(2000, self.finish_model_run)
    
    def finish_model_run(self):
        self.status_bar.showMessage("Model simulation completed")
        self.hide_loading()
    
    def load_output(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Simulation Output", "", "CSV Files (*.csv)")
        if filename:
            self.status_bar.showMessage(f"Loaded Output File: {filename}")
            self.visualize_output(filename)
    
    def visualize_output(self, file_path):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)

        # Check if the DataFrame contains the expected 'Date' column
        if 'Date' not in df.columns:
            self.status_bar.showMessage("Error: 'Date' column missing from the CSV file.")
            return

        # Convert 'Date' column to datetime for proper plotting
        df['Date'] = pd.to_datetime(df['Date'])

        # Plot each numerical column over time
        plt.figure(figsize=(10, 6))

        # Loop through the columns (ignoring 'Date')
        for column in df.columns:
            if column != 'Date':
                plt.plot(df['Date'], df[column], label=column)

        # Label the axes
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.title('Time Series Plot')

        # Add a legend to differentiate the curves
        plt.legend()

        # Show the plot
        plt.xticks(rotation=45)  # Rotate the dates for better visibility
        plt.tight_layout()  # Make sure everything fits without overlap
        plt.show()

        self.status_bar.showMessage(f"Loaded and plotted data from: {file_path}")

    def add_logo_banner(self):
        """Add company logo banner to the top of the application with better styling"""
        banner_widget = QWidget()
        banner_widget.setStyleSheet("background-color: #1a1a1a;")  # Dark background to match overall theme
        banner_widget.setFixedHeight(80)  # Slightly taller for better proportions
        
        banner_layout = QHBoxLayout(banner_widget)
        banner_layout.setContentsMargins(20, 10, 20, 10)  # More padding around the logo
        
        # Create a QLabel for the logo
        self.logo_label = QLabel()
        
        # Define the logo path depending on whether we're running from the bundled app or in development
        if getattr(sys, 'frozen', False):  # Check if the app is running as a bundled executable
            # Get the correct path to the logo within the bundled app
            logo_path = os.path.join(sys._MEIPASS, 'images', 'CUWALID_Logo_LS_Full_Colour.png')
        else:
            # Running from source (development mode)
            logo_path = 'images/CUWALID_Logo_LS_Full_Colour.png'
        
        try:
            # Load the logo image
            logo_pixmap = QPixmap(logo_path)
            
            # If logo is too large, scale it appropriately
            if logo_pixmap.height() > 60:
                logo_pixmap = logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
            
            self.logo_label.setPixmap(logo_pixmap)
            self.logo_label.setStyleSheet("padding: 5px;")
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        # Add to layout with spacers for better positioning
        banner_layout.addWidget(self.logo_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        banner_layout.addStretch()
        
        return banner_widget



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HydroApp()
    window.show()
    sys.exit(app.exec())
