import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt6.QtWidgets import QSlider, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QDialog
import pandas as pd

class Plotter:
    def __init__(self, ui):
        self.ui = ui

    def plot_raster(self):
        try:
            fig, ax = plt.subplots()
            cax = ax.imshow(self.ui.raster_data[0], cmap='terrain', extent=self.ui.raster_data[1], origin="upper")
            plt.colorbar(cax)
            plt.show()
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error plotting DEM: {e}")
            print(f"Error plotting DEM: {e}")

    def plot_shapefile(self, gdf):
        try:
            gdf.plot()
            plt.show()
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error plotting shapefile: {e}")

    def plot_xy(self, df, label_column=None):
        if df is None or df.empty:
            self.ui.status_bar.showMessage("No XY data to plot.")
            return
        
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(df["East"], df["North"], color='red', marker='o', label="XY Data Points")

            # If a third column exists, use it for labels
            if label_column:
                for i, row in df.iterrows():
                    ax.text(row["East"], row["North"], str(row[label_column]), fontsize=9, ha='right', va='bottom')

            ax.set_xlabel("East (m)")
            ax.set_ylabel("North (m)")
            ax.set_title("Scatter Plot of XY Data")
            ax.legend()
            ax.grid(True)

            plt.show()
            self.ui.status_bar.showMessage("XY data plotted successfully.")
        except Exception as e:
            self.ui.status_bar.showMessage(f"Error plotting XY data: {e}")

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

    def plot_csv_variable(self):
        if self.ui.csv_dataframe is None:
            return

        df = self.ui.csv_dataframe
        df['Date'] = pd.to_datetime(df['Date'])

        # Get checked items instead of selected ones
        selected_vars = []
        for index in range(self.ui.csv_var_selector.count()):
            item = self.ui.csv_var_selector.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                selected_vars.append(item.text())

        if not selected_vars:
            self.ui.status_bar.showMessage("Please select at least one variable.")
            return

        plt.clf()
        plt.close('all')
        plt.figure(figsize=(10, 6))

        for var in selected_vars:
            if var in df.columns:
                plt.plot(df['Date'], df[var], label=var)

        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.title("Time Series Plot")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        self.ui.status_bar.showMessage(f"Plotted CSV Variable(s): {', '.join(selected_vars)}")

    def plot_selected_files(self):
        plt.clf()
        plt.close('all')
        if self.ui.raster_checkbox.isChecked():
            self.plot_raster(self.ui.raster_data)

        if self.ui.shapefile_checkbox.isChecked():
            self.plot_shapefile(self.ui.shapefile_data)

        if self.ui.xy_checkbox.isChecked():
            self.plot_xy(self.ui.xy_data, self.ui.xy_labels)


        self.ui.status_bar.showMessage("Plotted selected files.")






