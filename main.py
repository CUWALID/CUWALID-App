import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui_components import CuwalidAPP

if __name__ == "__main__":
    app = QApplication(sys.argv)

    if getattr(sys, 'frozen', False):
        icon_path = os.path.join(sys._MEIPASS, 'images', "cuwalid_icon.ico")
    else:
        icon_path = os.path.join('images', "cuwalid_icon.ico")

    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = CuwalidAPP()
    window.show()
    sys.exit(app.exec())