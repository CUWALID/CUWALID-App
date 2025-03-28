import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QListWidget, QCheckBox, QFrame, QPushButton, QLabel, QVBoxLayout, QWidget, QGridLayout, QGroupBox, QStatusBar, QComboBox, QTabWidget, QStyle, QHBoxLayout, QSizePolicy, QProgressBar, QDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QApplication, QTextEdit
from data_processing import DataProcessor
from plotting_utils import Plotter
from constants import APP_STYLESHEET

class CuwalidAPP(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_processor = DataProcessor(self)
        self.plotter = Plotter(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("CUWALID Hydrological Model Helper")
        self.setGeometry(100, 100, 800, 600)
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
        file_layout = QGridLayout()

        # --- Load Files Group (Raster, Shapefile, XY Data) ---
        file_group = QGroupBox("Load Files and Plot")
        file_group_layout = QGridLayout()

        # Raster File
        self.load_raster_button = QPushButton("Load Raster File (.asc or .tif)")
        self.load_raster_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_raster_button.clicked.connect(self.data_processor.load_raster)
        self.raster_file_label = QLabel("No file loaded")  
        self.raster_checkbox = QCheckBox("Plot Raster")
        self.raster_checkbox.setEnabled(False)  # Initially disabled

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

        # Final Plot Button (inside the Load Files group)
        self.final_plot_button = QPushButton("Plot Selected Files")
        self.final_plot_button.setEnabled(False)
        self.final_plot_button.clicked.connect(self.plotter.plot_selected_files)
        file_group_layout.addWidget(self.final_plot_button, 3, 0, 1, 3)  # Span across all columns

        file_group.setLayout(file_group_layout)
        file_layout.addWidget(file_group, 0, 0, 1, 3)  # Span 3 columns

        # --- Separator Line ---
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        file_layout.addWidget(line1, 1, 0, 1, 3)

        # --- NetCDF Group (without checkboxes) ---
        netcdf_group = QGroupBox("NetCDF Selection")
        netcdf_layout = QVBoxLayout()

        self.load_netcdf_button = QPushButton("Load NetCDF File")
        self.load_netcdf_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_netcdf_button.clicked.connect(self.data_processor.load_netcdf)
        self.netcdf_file_label = QLabel("No file loaded")  

        self.netcdf_var_selector = QComboBox()
        self.netcdf_var_selector.currentIndexChanged.connect(self.plotter.plot_netcdf_variable)
        self.netcdf_var_selector.setEnabled(False)

        netcdf_layout.addWidget(self.load_netcdf_button)
        netcdf_layout.addWidget(self.netcdf_file_label)
        netcdf_layout.addWidget(QLabel("NetCDF Variable:"))
        netcdf_layout.addWidget(self.netcdf_var_selector)
        netcdf_group.setLayout(netcdf_layout)

        file_layout.addWidget(netcdf_group, 2, 0, 1, 3)

        # --- Separator Line ---
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        file_layout.addWidget(line2, 3, 0, 1, 3)

       # --- CSV Group (without checkboxes) ---
        csv_group = QGroupBox("CSV Data Selection")
        csv_layout = QVBoxLayout()

        # Button to load CSV file
        self.load_csv_button = QPushButton("Load CSV File (.csv)")
        self.load_csv_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_csv_button.clicked.connect(self.data_processor.load_csv)

        # Label for CSV file
        self.csv_file_label = QLabel("No file loaded")  

        # List of variables from CSV to select for plotting
        self.csv_var_selector = QListWidget()
        self.csv_var_selector.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.csv_var_selector.setEnabled(False)  # Initially disabled
        self.csv_var_selector.setMaximumHeight(100)

        # Plot button for CSV
        self.plot_csv_button = QPushButton("Plot CSV Data")
        self.plot_csv_button.setEnabled(False)  # Initially disabled
        self.plot_csv_button.clicked.connect(self.plotter.plot_csv_variable)

        # Add all widgets to CSV layout
        csv_layout.addWidget(self.load_csv_button)
        csv_layout.addWidget(self.csv_file_label)
        csv_layout.addWidget(QLabel("CSV Variables:"))
        csv_layout.addWidget(self.csv_var_selector)
        csv_layout.addWidget(self.plot_csv_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the layout for the CSV group
        csv_group.setLayout(csv_layout)

        # Add CSV group to the main layout (spanning 3 columns)
        file_layout.addWidget(csv_group, 4, 0, 1, 3)


        # --- Apply Layout ---
        main_layout.addLayout(file_layout)
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
        self.load_csv_button.setEnabled(enabled)
        self.load_json_button.setEnabled(enabled)
        self.run_model_button.setEnabled(enabled)

    def add_logo_banner(self):
        banner_widget = QWidget()
        banner_widget.setStyleSheet("background-color: #1a1a1a;")
        banner_widget.setFixedHeight(80)
        
        banner_layout = QHBoxLayout(banner_widget)
        banner_layout.setContentsMargins(20, 10, 20, 10)
        
        self.logo_label = QLabel()
        
        if getattr(sys, 'frozen', False):
            logo_path = os.path.join(sys._MEIPASS, 'images', 'CUWALID_Logo_LS_Full_Colour.png')
        else:
            logo_path = 'images/CUWALID_Logo_LS_Full_Colour.png'
        
        try:
            logo_pixmap = QPixmap(logo_path)
            if logo_pixmap.height() > 60:
                logo_pixmap = logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(logo_pixmap)
            self.logo_label.setStyleSheet("padding: 5px;")
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        banner_layout.addWidget(self.logo_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        banner_layout.addStretch()
        
        return banner_widget