import sys
import traceback
import os
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox

class GlobalExceptionHandler:
    """Catches unhandled exceptions, logs them safely, and prevents hard crashes."""
    
    LOG_DIR = "logs"
    LOG_FILE = os.path.join(LOG_DIR, "errors.log")

    @classmethod
    def install(cls):
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        sys.excepthook = cls.handle_exception

    @classmethod
    def handle_exception(cls, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions globally."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        cls.log_error(error_msg)
        
        # Show safe user-facing dialog instead of crashing out abruptly
        cls.show_safe_error_dialog()

    @classmethod
    def log_error(cls, message):
        """Safely write error to log file."""
        try:
            with open(cls.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
                f.write(message)
                f.write("\n" + "="*50 + "\n")
        except Exception:
            pass # Silent fail if logging fails to prevent recursive crashes

    @classmethod
    def show_safe_error_dialog(cls):
        """Show a generic, professional error message to the user."""
        try:
            # We must create a new QMessageBox instance safely
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Application Error")
            msg_box.setText("An unexpected error occurred.")
            msg_box.setInformativeText("The application recovered safely. If the issue persists, please contact support.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
        except Exception:
            pass # If the UI is too broken to show a dialog, just let it pass
