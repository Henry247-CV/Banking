from PyQt6.QtCore import QThread, pyqtSignal

class SafeWorker(QThread):
    """Generic safe background worker to prevent UI freezing during heavy tasks."""
    
    finished = pyqtSignal(object) # Emits result of the task
    error = pyqtSignal(str)       # Emits error message if task fails

    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.is_cancelled = False

    def run(self):
        try:
            if self.is_cancelled:
                return
            result = self.task_func(*self.args, **self.kwargs)
            if not self.is_cancelled:
                self.finished.emit(result)
        except Exception as e:
            if not self.is_cancelled:
                self.error.emit(str(e))

    def cancel(self):
        """Signals the thread to stop if supported by the task."""
        self.is_cancelled = True
