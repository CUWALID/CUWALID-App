import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QToolBox, QListWidget, QLineEdit, QCheckBox, QFrame, QPushButton, QLabel, QVBoxLayout, QWidget, QGridLayout, QGroupBox, QStatusBar, QComboBox, QTabWidget, QStyle, QHBoxLayout, QSizePolicy, QProgressBar)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QIcon, QDesktopServices
from PyQt6.QtWidgets import QApplication, QTextEdit
from data_processing import DataProcessor
from plotting_utils import Plotter
from constants import APP_STYLESHEET, APP_VERSION

class CuwalidAPP(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_processor = DataProcessor(self)
        self.plotter = Plotter(self)

        self.csv_dataframe_1= None
        self.csv_dataframe_2= None

        self.initUI()


    def initUI(self):
        self.setWindowTitle("CUWALID Hydrological Model Helper")
        self.setGeometry(100, 100, 900, 800)
        self.setStyleSheet(APP_STYLESHEET)

        if getattr(sys, 'frozen', False):  # Check if the app is running as a bundled executable
            # Get the correct path to the icon within the bundled app
            icon_path = os.path.join(sys._MEIPASS, 'images', "cuwalid_icon.ico")
        else:
            # Running from source (development mode)
            icon_path = os.path.join('images', "cuwalid_icon.ico")

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Icon file not found at: {icon_path}")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.add_logo_banner())
        
        tabs_container = QWidget()
        tabs_layout = QVBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(20, 20, 20, 20)
        
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.model_tab = QWidget()
        self.visualization_tab = QWidget()
        self.tabs.addTab(self.visualization_tab, "Visualisation")
        self.tabs.addTab(self.model_tab, "Run DRYP")
        
        self.init_visualization_tab()
        self.init_model_tab()
        
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


    def init_model_tab(self):
        layout = QVBoxLayout()

        self.load_json_button = QPushButton("Load JSON Input")
        self.load_json_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.load_json_button.clicked.connect(self.data_processor.load_json)
        layout.addWidget(self.load_json_button)

        self.run_model_button = QPushButton("Run DRYP")
        pixmapi = getattr(QStyle.StandardPixmap, "SP_MediaPlay")
        icon = self.style().standardIcon(pixmapi)
        self.run_model_button.setIcon(icon)
        self.run_model_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.run_model_button.clicked.connect(self.data_processor.run_model)
        layout.addWidget(self.run_model_button)

        # Add QTextEdit for model output
        self.model_output = QTextEdit()
        self.model_output.setReadOnly(True)
        self.model_output.setStyleSheet("background-color: black; color: lightgreen;")
        layout.addWidget(self.model_output)

        layout.addStretch()
        self.model_tab.setLayout(layout)

    def init_visualization_tab(self):

        
        main_layout = QVBoxLayout()
        self.visual_toolbox = QToolBox()

        # --- Load Files Group (Raster, Shapefile, XY Data) ---
        file_group = QGroupBox()  # Wrap in QGroupBox
        file_group_layout = QGridLayout()

        # Raster
        self.load_raster_button = QPushButton("Load Raster File (.asc or .tif)")
        self.load_raster_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_raster_button.clicked.connect(self.data_processor.load_raster)
        self.raster_file_label = QLabel("No file loaded")  
        self.raster_checkbox = QCheckBox("Plot Raster")
        self.raster_checkbox.setEnabled(False)

        file_group_layout.addWidget(self.load_raster_button, 0, 0)
        file_group_layout.addWidget(self.raster_file_label, 1, 0)
        file_group_layout.addWidget(self.raster_checkbox, 2, 0)

        # Shapefile
        self.load_shapefile_button = QPushButton("Load Shapefile (.shp)")
        self.load_shapefile_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_shapefile_button.clicked.connect(self.data_processor.load_shapefile)
        self.shapefile_file_label = QLabel("No file loaded")  
        self.shapefile_checkbox = QCheckBox("Plot Shapefile")
        self.shapefile_checkbox.setEnabled(False)

        file_group_layout.addWidget(self.load_shapefile_button, 0, 1)
        file_group_layout.addWidget(self.shapefile_file_label, 1, 1)
        file_group_layout.addWidget(self.shapefile_checkbox, 2, 1)

        # XY Data
        self.load_xy_button = QPushButton("Load XY Data (.csv)")
        self.load_xy_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_xy_button.clicked.connect(self.data_processor.load_xy)
        self.xy_file_label = QLabel("No file loaded")  
        self.xy_checkbox = QCheckBox("Plot XY Data")
        self.xy_checkbox.setEnabled(False)

        file_group_layout.addWidget(self.load_xy_button, 0, 2)
        file_group_layout.addWidget(self.xy_file_label, 1, 2)
        file_group_layout.addWidget(self.xy_checkbox, 2, 2)

        self.final_plot_button = QPushButton("Plot Selected Files")
        self.final_plot_button.setEnabled(False)
        self.final_plot_button.setObjectName("plot-button")
        self.final_plot_button.setProperty("class", "plot-button")
        self.final_plot_button.clicked.connect(self.plotter.plot_selected_files)
        file_group_layout.addWidget(self.final_plot_button, 3, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        file_group.setLayout(file_group_layout)
        self.visual_toolbox.addItem(file_group, "Plot Raster Maps")

        # --- NetCDF Group ---
        netcdf_group = QGroupBox()
        netcdf_layout = QVBoxLayout()

        # Load NetCDF Button (Full Width)
        self.load_netcdf_button = QPushButton("Load NetCDF File")
        self.load_netcdf_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_netcdf_button.clicked.connect(self.data_processor.load_netcdf)
        netcdf_layout.addWidget(self.load_netcdf_button)

        # No file loaded label (span entire width)
        self.netcdf_file_label = QLabel("No file loaded")
        self.netcdf_file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        netcdf_layout.addWidget(self.netcdf_file_label)

        # Shared NetCDF variable selector
        netcdf_layout.addWidget(QLabel("NetCDF Variable:"))
        self.netcdf_var_selector = QComboBox()
        self.netcdf_var_selector.setEnabled(False)
        netcdf_layout.addWidget(self.netcdf_var_selector)

        # Create tab widget for NetCDF functionalities
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # ---------- TAB 1: Plotting ----------
        plot_tab = QWidget()
        plot_layout = QVBoxLayout()

        # --- Plot button ---
        self.plot_netcdf_button = QPushButton("Plot NetCDF")
        self.plot_netcdf_button.setEnabled(False)
        self.plot_netcdf_button.clicked.connect(self.plotter.plot_netcdf_variable)
        self.plot_netcdf_button.setObjectName("plot-button")
        self.plot_netcdf_button.setProperty("class", "plot-button")
        plot_layout.addWidget(self.plot_netcdf_button)

        plot_tab.setLayout(plot_layout)
        self.tab_widget.addTab(plot_tab, "Plotting")

        # ---------- TAB 2: Extract Region ----------
        extract_region_tab = QWidget()
        region_layout = QVBoxLayout()

        self.upload_shapefile_button = QPushButton("Upload Shapefile for Region")
        self.upload_shapefile_button.clicked.connect(self.data_processor.upload_extract_shapefile)
        region_layout.addWidget(self.upload_shapefile_button)

        self.extract_region_button = QPushButton("Extract Data")
        self.extract_region_button.clicked.connect(self.data_processor.extract_region_data)
        self.extract_region_button.setObjectName("plot-button")
        self.extract_region_button.setProperty("class", "plot-button")
        region_layout.addWidget(self.extract_region_button)

        extract_region_tab.setLayout(region_layout)
        self.tab_widget.addTab(extract_region_tab, "Extract Region")

        # ---------- TAB 3: Extract Point ----------
        extract_point_tab = QWidget()
        point_layout = QVBoxLayout()

        # Horizontal layout for upload button + list
        horizontal_row = QHBoxLayout()

        self.upload_point_csv_button = QPushButton("Upload CSV for Points")
        self.upload_point_csv_button.clicked.connect(self.data_processor.upload_extract_points_csv)
        horizontal_row.addWidget(self.upload_point_csv_button)

        self.point_selector_list = QListWidget()
        self.point_selector_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.point_selector_list.setEnabled(False)
        self.point_selector_list.setMaximumHeight(120)
        horizontal_row.addWidget(self.point_selector_list)

        # Add label above for clarity
        point_label_layout = QHBoxLayout()
        point_label = QLabel("Upload and Select Points from CSV:")
        self.select_all_points_checkbox = QCheckBox("Select All")
        self.select_all_points_checkbox.setEnabled(False)
        self.select_all_points_checkbox.stateChanged.connect(self.toggle_all_points)
        point_label_layout.addWidget(point_label)
        point_label_layout.addStretch()
        point_label_layout.addWidget(self.select_all_points_checkbox)
        point_layout.addLayout(point_label_layout)

        point_layout.addLayout(horizontal_row)

        self.extract_point_button = QPushButton("Extract Data")
        self.extract_point_button.clicked.connect(self.data_processor.extract_point_data)
        self.extract_point_button.setObjectName("plot-button")
        self.extract_point_button.setProperty("class", "plot-button")
        point_layout.addWidget(self.extract_point_button)

        extract_point_tab.setLayout(point_layout)
        self.tab_widget.addTab(extract_point_tab, "Extract Point")

        # Add the tab widget to the main NetCDF layout
        netcdf_layout.addWidget(self.tab_widget)


        # Finalize group box
        netcdf_group.setLayout(netcdf_layout)
        self.visual_toolbox.addItem(netcdf_group, "NetCDF Datasets")


        # --- CSV Group ---
        csv_group = QGroupBox()  # Wrap in QGroupBox
        csv_layout = QGridLayout()

        # Dataset 1
        self.load_csv_button_1 = QPushButton("Load CSV 1")
        self.load_csv_button_1.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_csv_button_1.clicked.connect(lambda: self.data_processor.load_csv(1))
        self.csv_file_label_1 = QLabel("No file loaded")

        self.csv_var_selector_1 = QListWidget()
        self.csv_var_selector_1.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.csv_var_selector_1.setEnabled(False)
        self.csv_var_selector_1.setMaximumHeight(100)

        self.y_axis_label_1 = QLineEdit()
        self.y_axis_label_1.setPlaceholderText("Enter Y-axis title for Dataset 1")
        self.y_axis_label_1.setEnabled(False)

        csv_layout.addWidget(QLabel("Dataset 1 (Left Y-axis)"), 0, 0, Qt.AlignmentFlag.AlignCenter)
        csv_layout.addWidget(self.load_csv_button_1, 1, 0)
        csv_layout.addWidget(self.csv_file_label_1, 2, 0)
        csv_label_1_layout = QHBoxLayout()
        csv_label_1 = QLabel("Select CSV variables:")
        self.select_all_csv1_checkbox = QCheckBox("Select All")
        self.select_all_csv1_checkbox.setEnabled(False)
        self.select_all_csv1_checkbox.stateChanged.connect(self.toggle_all_csv1)
        csv_label_1_layout.addWidget(csv_label_1)
        csv_label_1_layout.addStretch()
        csv_label_1_layout.addWidget(self.select_all_csv1_checkbox)
        csv_layout.addLayout(csv_label_1_layout, 3, 0)
        csv_layout.addWidget(self.csv_var_selector_1, 4, 0)
        csv_layout.addWidget(self.y_axis_label_1, 6, 0)

        # Dataset 2
        self.load_csv_button_2 = QPushButton("Load CSV 2")
        self.load_csv_button_2.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_csv_button_2.clicked.connect(lambda: self.data_processor.load_csv(2))
        self.csv_file_label_2 = QLabel("No file loaded")

        self.csv_var_selector_2 = QListWidget()
        self.csv_var_selector_2.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.csv_var_selector_2.setEnabled(False)
        self.csv_var_selector_2.setMaximumHeight(100)

        self.y_axis_label_2 = QLineEdit()
        self.y_axis_label_2.setPlaceholderText("Enter Y-axis title for Dataset 2")
        self.y_axis_label_2.setEnabled(False)

        csv_layout.addWidget(QLabel("Dataset 2 (Right Y-axis)"), 0, 1, Qt.AlignmentFlag.AlignCenter)
        csv_layout.addWidget(self.load_csv_button_2, 1, 1)
        csv_layout.addWidget(self.csv_file_label_2, 2, 1)
        csv_label_2_layout = QHBoxLayout()
        csv_label_2 = QLabel("Select CSV variables:")
        self.select_all_csv2_checkbox = QCheckBox("Select All")
        self.select_all_csv2_checkbox.setEnabled(False)
        self.select_all_csv2_checkbox.stateChanged.connect(self.toggle_all_csv2)
        csv_label_2_layout.addWidget(csv_label_2)
        csv_label_2_layout.addStretch()
        csv_label_2_layout.addWidget(self.select_all_csv2_checkbox)
        csv_layout.addLayout(csv_label_2_layout, 3, 1)
        csv_layout.addWidget(self.csv_var_selector_2, 4, 1)
        csv_layout.addWidget(self.y_axis_label_2, 6, 1)

        self.plot_csv_button = QPushButton("Plot timeseries CSV")
        self.plot_csv_button.setEnabled(False)
        self.plot_csv_button.setObjectName("plot-button")
        self.plot_csv_button.setProperty("class", "plot-button")
        self.plot_csv_button.clicked.connect(self.plotter.plot_csv_variable)

        csv_layout.addWidget(self.plot_csv_button, 7, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        csv_group.setLayout(csv_layout)
        self.visual_toolbox.addItem(csv_group, "Plot Timeseries CSV Data")

        # --- Add to main layout ---
        main_layout.addWidget(self.visual_toolbox)
        main_layout.addStretch()
        self.visualization_tab.setLayout(main_layout)


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

    def add_logo_banner(self):
        banner_widget = QWidget()
        banner_widget.setStyleSheet("background-color: #1a1a1a;")

        banner_layout = QHBoxLayout(banner_widget)
        banner_layout.setContentsMargins(20, 10, 20, 10)

        # Left: Logo
        self.logo_label = QLabel()

        if getattr(sys, 'frozen', False):
            logo_path = os.path.join(sys._MEIPASS, 'images', 'CUWALID_Logo_LS_Tag_dark.png')
        else:
            logo_path = os.path.join('images', 'CUWALID_Logo_LS_Tag_dark.png')

        try:
            logo_pixmap = QPixmap(logo_path)
            if logo_pixmap.height() > 70:
                logo_pixmap = logo_pixmap.scaledToHeight(70, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(logo_pixmap)
            self.logo_label.setStyleSheet("padding: 5px;")
        except Exception as e:
            print(f"Error loading logo: {e}")

        banner_layout.addWidget(self.logo_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        banner_layout.addStretch()

        # Right: Version label, Help & Update buttons
        right_buttons_layout = QHBoxLayout()

        # Version label
        self.version_label = QLabel(APP_VERSION)
        self.version_label.setStyleSheet("color: #cccccc; font-size: 12px; padding-right: 10px;")
        right_buttons_layout.addWidget(self.version_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Help button
        help_button = QPushButton("Help")
        help_button.setCursor(Qt.CursorShape.PointingHandCursor)
        help_button.setStyleSheet("color: white; background-color: #444444; padding: 5px 10px;")
        help_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://cuwalid.github.io/tutorials/#input-helper")))
        right_buttons_layout.addWidget(help_button)

        # Update button
        update_button = QPushButton("Check for Updates")
        update_button.setCursor(Qt.CursorShape.PointingHandCursor)
        update_button.setStyleSheet("color: white; background-color: #444444; padding: 5px 10px;")
        update_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/CUWALID/CUWALID-App/releases")))
        right_buttons_layout.addWidget(update_button)

        right_container = QWidget()
        right_container.setLayout(right_buttons_layout)
        banner_layout.addWidget(right_container, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        return banner_widget

    
    def toggle_all_points(self, state):
        for i in range(self.point_selector_list.count()):
            self.point_selector_list.item(i).setCheckState(Qt.CheckState.Checked if state else Qt.CheckState.Unchecked)

    def toggle_all_csv1(self, state):
        for i in range(self.csv_var_selector_1.count()):
            self.csv_var_selector_1.item(i).setCheckState(Qt.CheckState.Checked if state else Qt.CheckState.Unchecked)

    def toggle_all_csv2(self, state):
        for i in range(self.csv_var_selector_2.count()):
            self.csv_var_selector_2.item(i).setCheckState(Qt.CheckState.Checked if state else Qt.CheckState.Unchecked)

