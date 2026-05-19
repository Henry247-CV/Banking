from PyQt6.QtGui import QFont, QFontDatabase
import sys

class FontManager:
    """Quản lý phông chữ tập trung cho ứng dụng."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        self._initialized = True
        
        # Tải phông chữ tùy chỉnh nếu có (ví dụ: Inter)
        # QFontDatabase.addApplicationFont("path/to/Inter.ttf")
        
        # Xác định họ phông chữ ưa thích
        self.preferred_family = "Segoe UI"
        if sys.platform == "darwin":
            self.preferred_family = "SF Pro Display"
        elif sys.platform == "linux":
            self.preferred_family = "Ubuntu"

    def get_font(self, size=12, weight=QFont.Weight.Normal, bold=False):
        font = QFont(self.preferred_family, size)
        if bold:
            font.setBold(True)
        else:
            font.setWeight(weight)
        return font

    def get_title_font(self):
        return self.get_font(18, QFont.Weight.Bold, True)

    def get_card_title_font(self):
        return self.get_font(14, QFont.Weight.Bold, True)

    def get_label_font(self):
        return self.get_font(12, QFont.Weight.Medium)

    def get_chart_font(self):
        return self.get_font(10)

    def get_table_font(self):
        return self.get_font(12)
