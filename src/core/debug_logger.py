import logging
import os
import traceback
from datetime import datetime

class DebugLogger:
    """Enhanced logging system for Đăng Khoa Bank."""
    
    LOG_DIR = "logs"
    ERROR_LOG = os.path.join(LOG_DIR, "error.log")
    DEBUG_MODE = True

    @classmethod
    def setup(cls):
        """Initialize the logging environment."""
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)
        
        # Configure standard logging
        logging.basicConfig(
            filename=cls.ERROR_LOG,
            level=logging.DEBUG if cls.DEBUG_MODE else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )

    @classmethod
    def log_exception(cls, exc_type, exc_value, exc_traceback, context="Unhandled Exception"):
        """Log a full traceback with context."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tb_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = "".join(tb_list)
        
        log_entry = (
            f"\n{'='*60}\n"
            f"TIMESTAMP: {timestamp}\n"
            f"CONTEXT:   {context}\n"
            f"TYPE:      {exc_type.__name__}\n"
            f"MESSAGE:   {exc_value}\n"
            f"{'-'*60}\n"
            f"TRACEBACK:\n{tb_text}"
            f"{'='*60}\n"
        )
        
        # Write to file directly for reliability during crashes
        try:
            with open(cls.ERROR_LOG, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"CRITICAL: Failed to write to log file: {e}")

        # Always print to console in debug mode
        if cls.DEBUG_MODE:
            print(f"\n[CRASH DETECTED] {context}")
            print(tb_text)

    @classmethod
    def log_error(cls, message, context="General Error"):
        """Log a general error message."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{context}] ERROR: {message}\n"
        
        try:
            with open(cls.ERROR_LOG, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass

        if cls.DEBUG_MODE:
            print(f"[ERROR] {context}: {message}")

    @classmethod
    def log_sqlite_error(cls, error, query=None, params=None, context="DATABASE"):
        """Specialized logging for database failures."""
        msg = f"SQLite Error: {str(error)}"
        if query:
            msg += f"\nQuery: {query}"
        if params:
            msg += f"\nParams: {params}"
        cls.log_error(msg, context=context)
