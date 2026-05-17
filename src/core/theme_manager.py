from PyQt6.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        super().__init__()
        self.current_theme = "dark"
        
        self.themes = {
            "dark": {
                "BACKGROUND": "#07111F",
                "SIDEBAR_BG": "#0B1727",
                "PANEL_BG": "#101B2E",
                "CARD_BG": "#132238",
                "TEXT_PRIMARY": "#FFFFFF",
                "TEXT_SECONDARY": "#9BB0C7",
                "BORDER": "#22324A",
                "CYAN": "#1EC8FF",
                "CYAN_HOVER": "#39D5FF",
                "GREEN": "#00E676",
                "RED": "#FF5252",
                "ORANGE": "#FFB74D",
                "SHADOW": "#050B14"
            },
            "light": {
                "BACKGROUND": "#F8FAFC",
                "SIDEBAR_BG": "#FFFFFF",
                "PANEL_BG": "#F1F5F9",
                "CARD_BG": "#FFFFFF",
                "TEXT_PRIMARY": "#0F172A",
                "TEXT_SECONDARY": "#64748B",
                "BORDER": "#E2E8F0",
                "CYAN": "#0EA5E9",
                "CYAN_HOVER": "#38BDF8",
                "GREEN": "#10B981",
                "RED": "#EF4444",
                "ORANGE": "#F59E0B",
                "SHADOW": "#CBD5E1"
            }
        }
        self._initialized = True

    def set_theme(self, theme):
        if theme in self.themes and theme != self.current_theme:
            self.current_theme = theme
            self.theme_changed.emit(theme)

    def get_color(self, key):
        return self.themes[self.current_theme].get(key, "#FF00FF")

    def get_all_colors(self):
        return self.themes[self.current_theme]
