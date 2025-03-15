import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt6.QtWidgets import QSlider, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QDialog
import pandas as pd

class Plotter:
    def __init__(self, ui):
        self.ui = ui

    def plot_raster(self, data, extent):
        try:
            plt.clf()
            plt.close('all')
            fig, ax = plt.subplots()
            cax = ax.imshow(data, cmap='terrain', extent=extent, origin="upper")
            plt.colorbar(cax)
            plt.show()
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error plotting DEM: {e}")
            print(f"Error plotting DEM: {e}")

    def plot_shapefile(self, gdf):
        try:
            plt.clf()
            plt.close('all')
            gdf.plot()
            plt.show()
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error plotting shapefile: {e}")

    def plot_netcdf_variable(self):
        if self.ui.netcdf_dataset is not None:
            var_name = self.ui.netcdf_var_selector.currentText()
            if var_name:
                self.ui.show_loading(f"Plotting {var_name}...")
                QTimer.singleShot(100, lambda: self.process_netcdf_plot_with_loading(var_name))

    def process_netcdf_plot_with_loading(self, var_name):
        try:
            data = self.ui.netcdf_dataset[var_name]
            if data.ndim == 2:
                plt.figure()
                data.plot()
                plt.show()
                self.ui.status_bar.showMessage(f"Plotted variable: {var_name}")
            elif data.ndim == 3:
                plt.clf()
                plt.close('all')
                self.slider_window = QDialog(self.ui)
                self.slider_window.setWindowTitle("Time Step Selector")
                self.slider_window.setGeometry(100, 100, 800, 600)
                layout = QVBoxLayout()
                self.fig, self.ax = plt.subplots()
                self.canvas = FigureCanvasQTAgg(self.fig)
                self.img = self.ax.imshow(data.isel(time=0), cmap="viridis", origin="lower")
                self.colorbar = self.fig.colorbar(self.img, ax=self.ax)
                self.time_slider = QSlider(Qt.Orientation.Horizontal)
                self.time_slider.setMinimum(0)
                self.time_slider.setMaximum(data.sizes["time"] - 1)
                self.time_slider.setValue(0)
                self.time_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
                self.time_slider.setTickInterval(1)
                self.time_slider.valueChanged.connect(lambda: self.update_netcdf_plot(data))
                layout.addWidget(self.canvas)
                layout.addWidget(self.time_slider)
                self.slider_window.setLayout(layout)
                self.slider_window.show()
                self.ui.status_bar.showMessage(f"Plotted variable: {var_name}")
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error plotting NetCDF variable: {e}")
        finally:
            self.ui.hide_loading()

    def update_netcdf_plot(self, data):
        time_index = self.time_slider.value()
        self.img.set_data(data.isel(time=time_index))
        self.ax.set_title(f"Time Step: {time_index}")
        self.canvas.draw()

    def visualize_output(self, file_path):
        plt.clf()
        plt.close('all')
        df = pd.read_csv(file_path)
        if 'Date' not in df.columns:
            self.ui.status_bar.showMessage("Error: 'Date' column missing from the CSV file.")
            return
        df['Date'] = pd.to_datetime(df['Date'])
        plt.figure(figsize=(10, 6))
        for column in df.columns:
            if column != 'Date':
                plt.plot(df['Date'], df[column], label=column)
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.title('Time Series Plot')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        self.ui.status_bar.showMessage(f"Loaded and plotted data from: {file_path}")