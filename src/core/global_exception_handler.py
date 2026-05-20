import sys
import os
import traceback
from PyQt6.QtWidgets import QMessageBox, QApplication
from src.core.debug_logger import DebugLogger

class GlobalCrashHandler:
    """
    Centralized Crash Handler for Đăng Khoa Bank.
    Captures all unhandled exceptions and prevents silent failures.
    """
    
    DEBUG_MODE = True

    @classmethod
    def install(cls):
        """Install the global exception hook."""
        DebugLogger.setup()
        sys.excepthook = cls.handle_exception
        print("[SYSTEM] Global Crash Handler installed.")

    @classmethod
    def handle_exception(cls, exc_type, exc_value, exc_traceback):
        """Global handler for uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # 1. Log the crash with full traceback
        DebugLogger.log_exception(exc_type, exc_value, exc_traceback)

        # 2. Show developer-friendly diagnostics or safe user popup
        cls.show_crash_dialog(exc_type, exc_value, exc_traceback)

    @classmethod
    def show_crash_dialog(cls, exc_type, exc_value, exc_traceback):
        """Displays a dialog with crash details or a safe recovery message."""
        try:
            if not QApplication.instance():
                return

            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("System Error - Đăng Khoa Bank")
            
            if cls.DEBUG_MODE:
                # Developer-friendly view
                tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                msg_box.setText(f"<b>CRITICAL ERROR: {exc_type.__name__}</b>")
                msg_box.setInformativeText(str(exc_value))
                msg_box.setDetailedText(tb_text)
            else:
                # Professional user-facing view
                msg_box.setText("A system error occurred.")
                msg_box.setInformativeText(
                    "The error has been logged safely.\nPlease retry the action.\n\n"
                    "If the issue continues, check logs/error.log"
                )

            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
        except Exception as e:
            # Fallback to console if UI is dead
            print(f"CRITICAL: Failed to show crash dialog: {e}")
            traceback.print_exc()
