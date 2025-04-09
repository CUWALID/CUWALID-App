import os
import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from ui_components import CuwalidAPP

# Get the correct log path for error logging
def get_log_path():
    if getattr(sys, 'frozen', False):  # If compiled
        return os.path.join(os.path.dirname(sys.executable), "error_log.txt")
    else:  # Running in development mode
        return os.path.join(os.getcwd(), "error_log.txt")

def log_error(error_message):
    """Write error message to a log file."""
    log_path = get_log_path()
    try:
        with open(log_path, "w") as log_file:
            log_file.write(error_message)
    except Exception as e:
        print(f"Failed to write error log: {e}")
    print(f"\n Crash detected! Check {log_path} for details.")

def show_critical_error(message):
    """Show an error message box with a detailed error."""
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Fatal Error")
    msg_box.setText("The application encountered a critical error.")
    msg_box.setDetailedText(message)
    msg_box.exec()

# Main app logic
def main():
    app = QApplication(sys.argv)

    try:
        if getattr(sys, 'frozen', False):  # If compiled
            icon_path = os.path.join(sys._MEIPASS, 'images', "cuwalid_icon.ico")
        else:
            icon_path = os.path.join('images', "cuwalid_icon.ico")

        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        window = CuwalidAPP()
        window.show()
        sys.exit(app.exec())

    except Exception as e:
        # Catch any unhandled exception and log it
        error_message = f"Fatal Error: {e}\n{traceback.format_exc()}"
        log_error(error_message)  # Save the error to a log file
        show_critical_error(error_message)  # Show a message box with error details
        input("\nPress Enter to exit...")  # Prevent the app from closing immediately

if __name__ == "__main__":
    main()
