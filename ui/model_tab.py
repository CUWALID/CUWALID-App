from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QTextEdit, QSizePolicy, QStyle, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

def init_model_tab(parent):
    layout = QVBoxLayout()

    # Create a horizontal layout for the two buttons
    button_layout = QHBoxLayout()

    # Left button: Load JSON
    parent.load_json_button = QPushButton("Load JSON Input")
    parent.load_json_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    parent.load_json_button.clicked.connect(parent.data_processor.load_json)
    button_layout.addWidget(parent.load_json_button)

    # Right button: Input Helper (opens website)
    parent.input_helper_button = QPushButton("Input Helper")
    parent.input_helper_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    parent.input_helper_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://cuwalid.github.io/tools/input-helper/")))
    button_layout.addWidget(parent.input_helper_button)

    # Add the horizontal layout to the main layout
    layout.addLayout(button_layout)

    parent.run_model_button = QPushButton("Run DRYP")
    icon = parent.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
    parent.run_model_button.setIcon(icon)
    parent.run_model_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    parent.run_model_button.setObjectName("plot-button")
    parent.run_model_button.setProperty("class", "plot-button")
    parent.run_model_button.clicked.connect(parent.data_processor.run_model)
    layout.addWidget(parent.run_model_button)

    parent.model_output = QTextEdit()
    parent.model_output.setReadOnly(True)
    parent.model_output.setStyleSheet("background-color: black; color: lightgreen;")
    layout.addWidget(parent.model_output)

    layout.addStretch()
    parent.model_tab.setLayout(layout)
