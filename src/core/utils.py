import os
import time
from pathlib import Path

def safe_currency(amount):
    """Safely formats a number into VND currency format."""
    try:
        if amount is None:
            return "0 VND"
        return "{:,.0f} VND".format(float(amount))
    except (ValueError, TypeError):
        return "0 VND"

def safe_text(text, default="N/A"):
    """Safely returns text or a default value if None or empty."""
    if text is None or str(text).strip() == "":
        return default
    return str(text).strip()

def safe_int(value, default=0):
    """Safely converts a value to an integer."""
    try:
        if value is None:
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_delete_temp_file(file_path):
    """Safely removes a temporary file if it exists."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False

def cleanup_leftover_files(minutes=30):
    """Deletes old verification and activation files from Desktop."""
    try:
        desktop_path = Path.home() / "Desktop"
        now = time.time()
        cutoff = now - (minutes * 60)
        
        patterns = ["verification_*.txt", "activation_*.txt"]
        for pattern in patterns:
            for file_path in desktop_path.glob(pattern):
                if file_path.stat().st_mtime < cutoff:
                    try:
                        file_path.unlink()
                    except Exception:
                        pass
    except Exception:
        pass
