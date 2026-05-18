from PyQt6.QtCore import QObject, QTimer

class SafeTimerManager(QObject):
    """Centralized manager to track and clean up QTimers safely."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SafeTimerManager, cls).__new__(cls)
            cls._instance.timers = []
        return cls._instance

    def create_timer(self, parent=None, interval_ms=None, callback=None, single_shot=False):
        """Creates a safe timer registered with the manager."""
        timer = QTimer(parent)
        if single_shot:
            timer.setSingleShot(True)
        if callback:
            timer.timeout.connect(callback)
        if interval_ms is not None:
            timer.setInterval(interval_ms)
            
        self.timers.append(timer)
        
        # Auto-remove from tracking if it's destroyed
        timer.destroyed.connect(lambda: self._remove_timer(timer))
        return timer

    def _remove_timer(self, timer):
        if timer in self.timers:
            self.timers.remove(timer)

    def stop_all(self):
        """Safely stops all registered timers to prevent memory leaks/background crashes."""
        for timer in self.timers:
            try:
                if timer.isActive():
                    timer.stop()
            except RuntimeError:
                pass # Timer might already be deleted in C++
        self.timers.clear()
