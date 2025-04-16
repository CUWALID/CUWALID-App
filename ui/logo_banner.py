import os
import sys
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QStyle
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices

from constants import APP_VERSION

def create_logo_banner(parent):
    banner_widget = QWidget()
    banner_widget.setStyleSheet("background-color: #1a1a1a;")
    banner_layout = QHBoxLayout(banner_widget)
    banner_layout.setContentsMargins(20, 10, 20, 10)

    logo_label = QLabel()
    logo_path = (
        os.path.join(sys._MEIPASS, 'images', 'CUWALID_Logo_LS_Tag_dark.png')
        if getattr(sys, 'frozen', False)
        else os.path.join('images', 'CUWALID_Logo_LS_Tag_dark.png')
    )
    try:
        logo_pixmap = QPixmap(logo_path)
        if logo_pixmap.height() > 70:
            logo_pixmap = logo_pixmap.scaledToHeight(70, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setStyleSheet("padding: 5px;")
    except Exception as e:
        print(f"Error loading logo: {e}")

    banner_layout.addWidget(logo_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    banner_layout.addStretch()

    right_buttons_layout = QHBoxLayout()
    version_label = QLabel(APP_VERSION)
    version_label.setStyleSheet("color: #cccccc; font-size: 12px; padding-right: 10px;")
    right_buttons_layout.addWidget(version_label)

    help_button = QPushButton("Help")
    help_button.setCursor(Qt.CursorShape.PointingHandCursor)
    help_button.setStyleSheet("color: white; background-color: #444444; padding: 5px 10px;")
    icon = parent.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView)
    help_button.setIcon(icon)
    help_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://cuwalid.github.io/tutorials/cuwalid-app")))
    right_buttons_layout.addWidget(help_button)

    update_button = QPushButton("Check for Updates")
    update_button.setCursor(Qt.CursorShape.PointingHandCursor)
    update_button.setStyleSheet("color: white; background-color: #444444; padding: 5px 10px;")
    icon = parent.style().standardIcon(QStyle.StandardPixmap.SP_CommandLink)
    update_button.setIcon(icon)
    update_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/CUWALID/CUWALID-App/releases")))
    right_buttons_layout.addWidget(update_button)

    right_container = QWidget()
    right_container.setLayout(right_buttons_layout)
    banner_layout.addWidget(right_container, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    return banner_widget
