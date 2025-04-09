import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt6.QtWidgets import QSlider, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QDialog
import matplotlib.patheffects as path_effects
import pandas as pd
import itertools

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
        plt.clf()
        plt.close('all')
        if self.ui.csv_dataframe_1 is None:
            return

        df1 = self.ui.csv_dataframe_1
        df1['Date'] = pd.to_datetime(df1['Date'])

        left_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:brown', 'tab:purple']
        right_colors = ['tab:red', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']

        left_color_cycle = itertools.cycle(left_colors)
        right_color_cycle = itertools.cycle(right_colors)

        selected_vars_1 = [
            self.ui.csv_var_selector_1.item(i).text()
            for i in range(self.ui.csv_var_selector_1.count())
            if self.ui.csv_var_selector_1.item(i).checkState() == Qt.CheckState.Checked
        ]

        has_second_dataset = self.ui.csv_dataframe_2 is not None
        if has_second_dataset:
            df2 = self.ui.csv_dataframe_2
            df2['Date'] = pd.to_datetime(df2['Date'])
            
            selected_vars_2 = [
                self.ui.csv_var_selector_2.item(i).text()
                for i in range(self.ui.csv_var_selector_2.count())
                if self.ui.csv_var_selector_2.item(i).checkState() == Qt.CheckState.Checked
            ]
        else:
            selected_vars_2 = []

        if not selected_vars_1 and not selected_vars_2:
            self.ui.status_bar.showMessage("Please select at least one variable.")
            return

        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot first dataset on left y-axis
        for var in selected_vars_1:
            if var in df1.columns:
                color = next(left_color_cycle)
                ax1.plot(df1['Date'], df1[var], label=f"1: {var}", linestyle='-', color=color)

        y_label_1 = self.ui.y_axis_label_1.text() or "Dataset 1"
        ax1.set_ylabel(y_label_1)
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        ax2 = None  # Initialize ax2

        # Plot second dataset on right y-axis
        if has_second_dataset and selected_vars_2:
            ax2 = ax1.twinx()
            for var in selected_vars_2:
                if var in df2.columns:
                    color = next(right_color_cycle)
                    ax2.plot(df2['Date'], df2[var], label=f"2: {var}", linestyle='--', color=color)

            y_label_2 = self.ui.y_axis_label_2.text() or "Dataset 2"
            ax2.set_ylabel(y_label_2)
            ax2.tick_params(axis='y', labelcolor='tab:red')

        ax1.set_xlabel("Date")
        ax1.set_title("Timeseries Plot")

        # **Ensure legends are shown**
        ax1.legend(loc='upper left')  # Legend for left y-axis variables
        if ax2:
            ax2.legend(loc='upper right')  # Legend for right y-axis variables

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # Status update
        plotted_vars = ", ".join(selected_vars_1 + selected_vars_2)
        self.ui.status_bar.showMessage(f"Plotted Variables: {plotted_vars}")



    def plot_selected_files(self):
        plt.clf()
        plt.close('all')
        
        fig, ax = plt.subplots(figsize=(10, 8))  # Create a single figure and axis

        # Plot Raster if enabled
        if self.ui.raster_checkbox.isChecked() and self.ui.raster_data:
            raster_data, extent = self.ui.raster_data
            cax = ax.imshow(raster_data, cmap='terrain', extent=extent, origin="upper")
            plt.colorbar(cax, ax=ax, label="Elevation")  # Add a colorbar

        # Plot Shapefile if enabled
        if self.ui.shapefile_checkbox.isChecked() and self.ui.shapefile_data is not None:
            self.ui.shapefile_data.plot(ax=ax, edgecolor="black", facecolor="none")  # Plot borders

        # Plot XY Data if enabled
        if self.ui.xy_checkbox.isChecked() and self.ui.xy_data is not None:
            df = self.ui.xy_data
            ax.scatter(df["East"], df["North"], color='red', marker='o', label="XY Data Points")

            # If labels exist, add them to the points
            if self.ui.xy_labels:
                for i, row in df.iterrows():
                    txt = ax.text(row["East"], row["North"], str(row[self.ui.xy_labels]), 
                        fontsize=10, ha='right', va='bottom', color='white')

                    # Add a black outline around the text
                    txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), 
                                        path_effects.Normal()])

        # Set Labels and Title
        ax.set_xlabel("East (m)")
        ax.set_ylabel("North (m)")
        ax.set_title("Combined Hydrological Data Visualization")
        ax.legend()
        ax.grid(True)

        plt.show()
        self.ui.status_bar.showMessage("Plotted selected files together.")


