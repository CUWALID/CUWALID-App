from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QCheckBox, QComboBox,
    QSizePolicy, QGroupBox, QScrollArea, QWidget, QToolBox, QGridLayout, QStyle, QTabWidget,
    QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

def create_file_group(parent):
    """Creates the 'Load Files' group for raster, shapefile, and XY data."""
    file_group = QGroupBox("Plot Raster Maps")
    file_group_layout = QGridLayout()

    # Raster
    parent.load_raster_button = QPushButton("Load Raster File (.asc or .tif)")
    parent.load_raster_button.setIcon(parent.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
    parent.load_raster_button.clicked.connect(parent.data_processor.load_raster)
    parent.raster_file_label = QLabel("No file loaded")
    parent.raster_checkbox = QCheckBox("Plot Raster")
    parent.raster_checkbox.setEnabled(False)

    file_group_layout.addWidget(parent.load_raster_button, 0, 0)
    file_group_layout.addWidget(parent.raster_file_label, 1, 0)
    file_group_layout.addWidget(parent.raster_checkbox, 2, 0)

    # Shapefile
    parent.load_shapefile_button = QPushButton("Load Shapefile (.shp)")
    parent.load_shapefile_button.setIcon(parent.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
    parent.load_shapefile_button.clicked.connect(parent.data_processor.load_shapefile)
    parent.shapefile_file_label = QLabel("No file loaded")
    parent.shapefile_checkbox = QCheckBox("Plot Shapefile")
    parent.shapefile_checkbox.setEnabled(False)

    file_group_layout.addWidget(parent.load_shapefile_button, 0, 1)
    file_group_layout.addWidget(parent.shapefile_file_label, 1, 1)
    file_group_layout.addWidget(parent.shapefile_checkbox, 2, 1)

    # XY Data
    parent.load_xy_button = QPushButton("Load XY Data (.csv)")
    parent.load_xy_button.setIcon(parent.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
    parent.load_xy_button.clicked.connect(parent.data_processor.load_xy)
    parent.xy_file_label = QLabel("No file loaded")
    parent.xy_checkbox = QCheckBox("Plot XY Data")
    parent.xy_checkbox.setEnabled(False)

    file_group_layout.addWidget(parent.load_xy_button, 0, 2)
    file_group_layout.addWidget(parent.xy_file_label, 1, 2)
    file_group_layout.addWidget(parent.xy_checkbox, 2, 2)

    parent.final_plot_button = QPushButton("Plot Selected Files")
    parent.final_plot_button.setEnabled(False)
    parent.final_plot_button.setObjectName("plot-button")
    parent.final_plot_button.setProperty("class", "plot-button")
    parent.final_plot_button.clicked.connect(parent.plotter.plot_selected_files)
    file_group_layout.addWidget(parent.final_plot_button, 3, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

    file_group.setLayout(file_group_layout)
    return file_group


def create_netcdf_group(parent):
    """Creates the 'NetCDF Datasets' group with tabs for plotting and data extraction."""
    netcdf_group = QGroupBox("NetCDF Datasets")
    netcdf_layout = QVBoxLayout()

    # Load NetCDF Button
    parent.load_netcdf_button = QPushButton("Load NetCDF File")
    parent.load_netcdf_button.setIcon(parent.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
    parent.load_netcdf_button.clicked.connect(parent.data_processor.load_netcdf)
    netcdf_layout.addWidget(parent.load_netcdf_button)

    # No file loaded label
    parent.netcdf_file_label = QLabel("No file loaded")
    parent.netcdf_file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    netcdf_layout.addWidget(parent.netcdf_file_label)

    # NetCDF variable selector
    netcdf_layout.addWidget(QLabel("NetCDF Variable:"))
    parent.netcdf_var_selector = QComboBox()
    parent.netcdf_var_selector.setEnabled(False)
    netcdf_layout.addWidget(parent.netcdf_var_selector)

    # Tab widget
    parent.tab_widget = QTabWidget()
    parent.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

    # Plotting tab
    plot_tab = QWidget()
    plot_layout = QVBoxLayout()
    parent.plot_netcdf_button = QPushButton("Plot NetCDF")
    parent.plot_netcdf_button.setEnabled(False)
    parent.plot_netcdf_button.clicked.connect(parent.plotter.plot_netcdf_variable)
    parent.plot_netcdf_button.setObjectName("plot-button")
    parent.plot_netcdf_button.setProperty("class", "plot-button")
    plot_layout.addWidget(parent.plot_netcdf_button)
    plot_tab.setLayout(plot_layout)
    parent.tab_widget.addTab(plot_tab, "Plotting")

    # Extract Region tab
    extract_region_tab = QWidget()
    region_layout = QVBoxLayout()
    parent.upload_shapefile_button = QPushButton("Upload Shapefile for Region")
    parent.upload_shapefile_button.clicked.connect(parent.data_processor.upload_extract_shapefile)
    region_layout.addWidget(parent.upload_shapefile_button)
    parent.extract_region_button = QPushButton("Extract Data")
    parent.extract_region_button.clicked.connect(parent.data_processor.extract_region_data)
    parent.extract_region_button.setObjectName("plot-button")
    parent.extract_region_button.setProperty("class", "plot-button")
    region_layout.addWidget(parent.extract_region_button)
    extract_region_tab.setLayout(region_layout)
    parent.tab_widget.addTab(extract_region_tab, "Extract Region")

    # Extract Point tab
    extract_point_tab = QWidget()
    point_layout = QVBoxLayout()
    horizontal_row = QHBoxLayout()
    parent.upload_point_csv_button = QPushButton("Upload CSV for Points")
    parent.upload_point_csv_button.clicked.connect(parent.data_processor.upload_extract_points_csv)
    horizontal_row.addWidget(parent.upload_point_csv_button)
    parent.point_selector_list = QListWidget()
    parent.point_selector_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
    parent.point_selector_list.setEnabled(False)
    parent.point_selector_list.setMaximumHeight(120)
    horizontal_row.addWidget(parent.point_selector_list)

    point_label_layout = QHBoxLayout()
    point_label = QLabel("Upload and Select Points from CSV:")
    parent.select_all_points_checkbox = QCheckBox("Select All")
    parent.select_all_points_checkbox.setEnabled(False)
    parent.select_all_points_checkbox.stateChanged.connect(parent.toggle_all_points)
    point_label_layout.addWidget(point_label)
    point_label_layout.addStretch()
    point_label_layout.addWidget(parent.select_all_points_checkbox)
    point_layout.addLayout(point_label_layout)

    point_layout.addLayout(horizontal_row)
    parent.extract_point_button = QPushButton("Extract Data")
    parent.extract_point_button.clicked.connect(parent.data_processor.extract_point_data)
    parent.extract_point_button.setObjectName("plot-button")
    parent.extract_point_button.setProperty("class", "plot-button")
    point_layout.addWidget(parent.extract_point_button)
    extract_point_tab.setLayout(point_layout)
    parent.tab_widget.addTab(extract_point_tab, "Extract Point")

    netcdf_layout.addWidget(parent.tab_widget)
    netcdf_group.setLayout(netcdf_layout)
    return netcdf_group


def create_csv_group(parent):
    """Creates the 'Plot Timeseries CSV Data' group for loading and plotting CSV data."""
    csv_group = QGroupBox("Plot Timeseries CSV Data")
    csv_layout = QGridLayout()

    # Dataset 1
    parent.load_csv_button_1 = QPushButton("Load CSV 1")
    parent.load_csv_button_1.setIcon(parent.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
    parent.load_csv_button_1.clicked.connect(lambda: parent.data_processor.load_csv(1))
    parent.csv_file_label_1 = QLabel("No file loaded")
    parent.csv_var_selector_1 = QListWidget()
    parent.csv_var_selector_1.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
    parent.csv_var_selector_1.setEnabled(False)
    parent.csv_var_selector_1.setMaximumHeight(100)
    parent.y_axis_label_1 = QLineEdit()
    parent.y_axis_label_1.setPlaceholderText("Enter Y-axis title for Dataset 1")
    parent.y_axis_label_1.setEnabled(False)

    csv_layout.addWidget(QLabel("Dataset 1 (Left Y-axis)"), 0, 0, Qt.AlignmentFlag.AlignCenter)
    csv_layout.addWidget(parent.load_csv_button_1, 1, 0)
    csv_layout.addWidget(parent.csv_file_label_1, 2, 0)
    csv_label_1_layout = QHBoxLayout()
    csv_label_1 = QLabel("Select CSV variables:")
    parent.select_all_csv1_checkbox = QCheckBox("Select All")
    parent.select_all_csv1_checkbox.setEnabled(False)
    parent.select_all_csv1_checkbox.stateChanged.connect(parent.toggle_all_csv1)
    csv_label_1_layout.addWidget(csv_label_1)
    csv_label_1_layout.addStretch()
    csv_label_1_layout.addWidget(parent.select_all_csv1_checkbox)
    csv_layout.addLayout(csv_label_1_layout, 3, 0)
    csv_layout.addWidget(parent.csv_var_selector_1, 4, 0)
    csv_layout.addWidget(parent.y_axis_label_1, 6, 0)

    # Dataset 2
    parent.load_csv_button_2 = QPushButton("Load CSV 2")
    parent.load_csv_button_2.setIcon(parent.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
    parent.load_csv_button_2.clicked.connect(lambda: parent.data_processor.load_csv(2))
    parent.csv_file_label_2 = QLabel("No file loaded")
    parent.csv_var_selector_2 = QListWidget()
    parent.csv_var_selector_2.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
    parent.csv_var_selector_2.setEnabled(False)
    parent.csv_var_selector_2.setMaximumHeight(100)
    parent.y_axis_label_2 = QLineEdit()
    parent.y_axis_label_2.setPlaceholderText("Enter Y-axis title for Dataset 2")
    parent.y_axis_label_2.setEnabled(False)

    csv_layout.addWidget(QLabel("Dataset 2 (Right Y-axis)"), 0, 1, Qt.AlignmentFlag.AlignCenter)
    csv_layout.addWidget(parent.load_csv_button_2, 1, 1)
    csv_layout.addWidget(parent.csv_file_label_2, 2, 1)
    csv_label_2_layout = QHBoxLayout()
    csv_label_2 = QLabel("Select CSV variables:")
    parent.select_all_csv2_checkbox = QCheckBox("Select All")
    parent.select_all_csv2_checkbox.setEnabled(False)
    parent.select_all_csv2_checkbox.stateChanged.connect(parent.toggle_all_csv2)
    csv_label_2_layout.addWidget(csv_label_2)
    csv_label_2_layout.addStretch()
    csv_label_2_layout.addWidget(parent.select_all_csv2_checkbox)
    csv_layout.addLayout(csv_label_2_layout, 3, 1)
    csv_layout.addWidget(parent.csv_var_selector_2, 4, 1)
    csv_layout.addWidget(parent.y_axis_label_2, 6, 1)

    parent.plot_csv_button = QPushButton("Plot timeseries CSV")
    parent.plot_csv_button.setEnabled(False)
    parent.plot_csv_button.setObjectName("plot-button")
    parent.plot_csv_button.setProperty("class", "plot-button")
    parent.plot_csv_button.clicked.connect(parent.plotter.plot_csv_variable)

    csv_layout.addWidget(parent.plot_csv_button, 7, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

    csv_group.setLayout(csv_layout)
    return csv_group

def init_visualization_tab(parent):
    """Initializes the visualization tab of the main window."""
    main_layout = QVBoxLayout()
    parent.visual_toolbox = QToolBox()

    file_group = create_file_group(parent)
    netcdf_group = create_netcdf_group(parent)
    csv_group = create_csv_group(parent)

    parent.visual_toolbox.addItem(file_group, "Plot Raster Maps")
    parent.visual_toolbox.addItem(netcdf_group, "NetCDF Datasets")
    parent.visual_toolbox.addItem(csv_group, "Plot Timeseries CSV Data")

    # Set icons for the QToolBox items
    parent.visual_toolbox.setItemIcon(0, parent.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarUnshadeButton))
    parent.visual_toolbox.setItemIcon(1, parent.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
    parent.visual_toolbox.setItemIcon(2, parent.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def update_toolbox_icons(index):
        for i in range(parent.visual_toolbox.count()):
            if i == index:
                if parent.visual_toolbox.widget(i).isVisible():
                    parent.visual_toolbox.setItemIcon(i, parent.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarUnshadeButton)) # right arrow when open
                else:
                    parent.visual_toolbox.setItemIcon(i, parent.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarUnshadeButton))#down arrow when closed
            else:
                if parent.visual_toolbox.widget(i).isVisible():
                    parent.visual_toolbox.setItemIcon(i, parent.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarUnshadeButton))
                else:
                     parent.visual_toolbox.setItemIcon(i, parent.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    parent.visual_toolbox.currentChanged.connect(update_toolbox_icons)
    update_toolbox_icons(parent.visual_toolbox.currentIndex())

    main_layout.addWidget(parent.visual_toolbox)
    main_layout.addStretch()
    parent.visualization_tab.setLayout(main_layout)