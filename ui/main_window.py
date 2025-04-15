import sys
import os
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTabWidget, QStatusBar, QLabel, QProgressBar, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from constants import APP_STYLESHEET
from data_processing import DataProcessor
from plotting_utils import Plotter

from .model_tab import init_model_tab
from .visualisation_tab import init_visualization_tab
from .logo_banner import create_logo_banner


class CuwalidAPP(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_processor = DataProcessor(self)
        self.plotter = Plotter(self)

        self.csv_dataframe_1 = None
        self.csv_dataframe_2 = None
        self.xy_data = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle("CUWALID Hydrological Model Helper")
        self.setGeometry(100, 100, 900, 800)
        self.setStyleSheet(APP_STYLESHEET)

        icon_path = (
            os.path.join(sys._MEIPASS, 'images', 'cuwalid_icon.ico')
            if getattr(sys, 'frozen', False)
            else os.path.join('images', 'cuwalid_icon.ico')
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Icon file not found at: {icon_path}")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(create_logo_banner(self))

        tabs_container = QWidget()
        tabs_layout = QVBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(20, 20, 20, 20)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.visualization_tab = QWidget()
        self.model_tab = QWidget()

        self.tabs.addTab(self.visualization_tab, "Visualisation")
        self.tabs.addTab(self.model_tab, "Run DRYP")

        init_visualization_tab(self)
        init_model_tab(self)

        tabs_layout.addWidget(self.tabs)
        main_layout.addWidget(tabs_container)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { background-color: #222222; color: #cccccc; }")
        self.setStatusBar(self.status_bar)

        self.loading_label = QLabel("Loading data...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("font-weight: bold; color: #4d8f93;")
        self.loading_label.hide()
        self.status_bar.addPermanentWidget(self.loading_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.netcdf_dataset = None

    def show_loading(self, message="Loading data..."):
        self.loading_label.setText(message)
        self.loading_label.show()
        self.progress_bar.show()
        self.update_buttons_state(False)
        QApplication.processEvents()

    def hide_loading(self):
        self.loading_label.hide()
        self.progress_bar.hide()
        self.update_buttons_state(True)

    def update_buttons_state(self, enabled):
        self.load_raster_button.setEnabled(enabled)
        self.load_shapefile_button.setEnabled(enabled)
        self.load_netcdf_button.setEnabled(enabled)
        self.load_csv_button_1.setEnabled(enabled)
        self.load_csv_button_2.setEnabled(enabled)
        self.load_json_button.setEnabled(enabled)
        self.run_model_button.setEnabled(enabled)

    def toggle_all_points(self, state):
        for i in range(self.point_selector_list.count()):
            self.point_selector_list.item(i).setCheckState(Qt.CheckState.Checked if state else Qt.CheckState.Unchecked)

    def toggle_all_csv1(self, state):
        for i in range(self.csv_var_selector_1.count()):
            self.csv_var_selector_1.item(i).setCheckState(Qt.CheckState.Checked if state else Qt.CheckState.Unchecked)

    def toggle_all_csv2(self, state):
        for i in range(self.csv_var_selector_2.count()):
            self.csv_var_selector_2.item(i).setCheckState(Qt.CheckState.Checked if state else Qt.CheckState.Unchecked)
