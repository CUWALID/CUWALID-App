import sys
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtWidgets import QLineEdit

class GeoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("CUWALID Pre-Processing Helper")
        layout = QVBoxLayout()

        # File loading section
        self.load_button = QPushButton("Load .asc File")
        self.load_button.clicked.connect(self.load_file)
        layout.addWidget(self.load_button)

        self.shapefile_button = QPushButton("Load Shapefile")
        self.shapefile_button.clicked.connect(self.load_shapefile)
        layout.addWidget(self.shapefile_button)

        self.mask_button = QPushButton("Create Mask from Shapefile")
        self.mask_button.clicked.connect(self.create_mask)
        layout.addWidget(self.mask_button)

        self.clip_button = QPushButton("Clip Raster by Mask")
        self.clip_button.clicked.connect(self.clip_raster)
        layout.addWidget(self.clip_button)

        self.plot_label = QLabel("Plot will appear here")
        layout.addWidget(self.plot_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open .asc File", "", "ASCII Files (*.asc)")
        if filename:
            self.filename = filename
            self.process_data(filename)

    def load_shapefile(self):
        shapefile, _ = QFileDialog.getOpenFileName(self, "Open Shapefile", "", "Shapefiles (*.shp)")
        if shapefile:
            self.shapefile = shapefile
            # Process shapefile if needed

    def create_mask(self):
        # Implement functionality for creating mask from shapefile
        if hasattr(self, 'filename') and hasattr(self, 'shapefile'):
            # Assume the user loaded a raster and shapefile
            print(f"Creating mask for {self.filename} with shapefile {self.shapefile}")
            # Call function to generate a mask based on shapefile and raster

    def clip_raster(self):
        # Implement raster clipping functionality using mask
        if hasattr(self, 'filename'):
            print(f"Clipping raster {self.filename} based on mask")
            # Call clipping function here
            
    def process_data(self, file_path):
        # Open and read the .asc file using rasterio
        with rasterio.open(file_path) as src:
            data = src.read(1)  # Read the first band
            extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]

        # Plot the data
        self.plot_raster(data, extent)

    def plot_raster(self, data, extent):
        # Create a plot for the raster data
        fig, ax = plt.subplots()
        cax = ax.imshow(data, cmap='terrain', extent=extent, origin="upper")
        plt.colorbar(cax)
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeoApp()
    window.show()
    sys.exit(app.exec())
