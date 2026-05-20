import sys
import traceback
import os
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox
from src.core.debug_logger import DebugLogger
from src.core.global_exception_handler import GlobalCrashHandler

class GlobalExceptionHandler:
    """
    Legacy wrapper for the new GlobalCrashHandler.
    Ensures backward compatibility while upgrading to robust handling.
    """
    
    @classmethod
    def install(cls):
        GlobalCrashHandler.install()

    @classmethod
    def handle_exception(cls, exc_type, exc_value, exc_traceback):
        GlobalCrashHandler.handle_exception(exc_type, exc_value, exc_traceback)

    @classmethod
    def log_error(cls, message, context="General"):
        DebugLogger.log_error(message, context=context)

    @classmethod
    def show_safe_error_dialog(cls):
        """Deprecated: Use GlobalCrashHandler's dialog logic instead."""
        # This is kept for compatibility with existing calls but uses the improved UI
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("System Warning")
        msg_box.setText("An unexpected behavior was detected.")
        msg_box.setInformativeText("The system has logged this event and remains stable.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
