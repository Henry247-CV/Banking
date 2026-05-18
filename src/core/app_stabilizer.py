from PyQt6.QtCore import QObject
from src.core.safe_timer_manager import SafeTimerManager
from src.core.memory_manager import MemoryManager

class AppStabilizer(QObject):
    """Centralized hub for application lifecycle stabilization."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppStabilizer, cls).__new__(cls)
            cls._instance.timer_mgr = SafeTimerManager()
            cls._instance.memory_mgr = MemoryManager()
        return cls._instance

    def track_dialog(self, dialog):
        self.memory_mgr.register_dialog(dialog)

    def track_animation(self, animation):
        self.memory_mgr.register_animation(animation)

    def create_safe_timer(self, parent=None, interval_ms=None, callback=None, single_shot=False):
        return self.timer_mgr.create_timer(parent, interval_ms, callback, single_shot)

    def safe_shutdown(self):
        """Called immediately before app exit to prevent hanging threads and memory leaks."""
        self.timer_mgr.stop_all()
        self.memory_mgr.cleanup_all()
