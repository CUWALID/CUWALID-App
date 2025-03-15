import sys
from PyQt6.QtWidgets import QApplication
from ui_components import CuwalidAPP

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CuwalidAPP()
    window.show()
    sys.exit(app.exec())