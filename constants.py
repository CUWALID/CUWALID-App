APP_STYLESHEET = """
            * {
                color: white; /* Default text color for all widgets */
            }
            QMainWindow {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #2d2d2d;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #cccccc;
                padding: 8px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #555555;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c6e71;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #4d8f93;
            }
            QPushButton:pressed {
                background-color: #2a5254;
            }
            QComboBox {
                background-color: #3d3d3d;
                color: white;
                border: 1px solid #1a1a1a;
                border-radius: 4px;
                padding: 6px;
                min-height: 30px;
            }
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 4px;
                background-color: #333333;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #3c6e71;
                width: 20px;
            }
            QListWidget {
                background-color: #3d3d3d;
                border: 1px solid #1a1a1a;
                border-radius: 4px;
            }
            QFrame {
                background-color: #3d3d3d;
            }
            QGroupBox {
                border: 2px solid #2d2d2d;
                padding: 10px;
            }
        """