from PyQt6.QtCore import QObject

class MemoryManager(QObject):
    """Centralized registry for tracking and cleaning up heavy UI resources."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
            cls._instance.dialogs = []
            cls._instance.animations = []
        return cls._instance

    def register_dialog(self, dialog):
        """Tracks active dialogs to prevent stacking or orphan crashes."""
        self.dialogs.append(dialog)
        dialog.finished.connect(lambda: self._remove_dialog(dialog))

    def _remove_dialog(self, dialog):
        if dialog in self.dialogs:
            self.dialogs.remove(dialog)
            dialog.deleteLater() # Safely schedule cleanup

    def register_animation(self, animation):
        self.animations.append(animation)
        animation.finished.connect(lambda: self._remove_animation(animation))

    def _remove_animation(self, animation):
        if animation in self.animations:
            self.animations.remove(animation)
            animation.deleteLater()

    def close_all_dialogs(self):
        """Closes all tracked modal dialogs to prevent blocking UI on exit."""
        for dialog in self.dialogs[:]: # Copy list to avoid mutation issues
            try:
                dialog.reject()
            except RuntimeError:
                pass
        self.dialogs.clear()

    def stop_all_animations(self):
        """Stops and cleans up ongoing animations."""
        for anim in self.animations[:]:
            try:
                anim.stop()
            except RuntimeError:
                pass
        self.animations.clear()

    def cleanup_all(self):
        self.close_all_dialogs()
        self.stop_all_animations()
