from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.theme import *
from src.core.styles import *

from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager

class SidebarButton(QPushButton):
    def __init__(self, key, icon, is_active=False):
        self.key = key
        self.icon = icon
        self.lang_manager = LanguageManager()
        text = f"{self.icon}  {self.lang_manager.get_text(self.key)}"
        super().__init__(text)
        self.is_active = is_active
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

    def update_translations(self):
        self.setText(f"{self.icon}  {self.lang_manager.get_text(self.key)}")

    def update_style(self):
        if self.is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.CYAN};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding-left: 20px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: left;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme.TEXT_SECONDARY};
                    border: none;
                    border-radius: 12px;
                    padding-left: 20px;
                    font-size: 14px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {theme.PANEL_BG};
                    color: {theme.TEXT_PRIMARY};
                }}
            """)

    def set_active(self, active):
        self.is_active = active
        self.update_style()

class Sidebar(QFrame):
    nav_changed = pyqtSignal(int)
    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.setFixedWidth(240)
        self.buttons = []
        self.setup_ui()
        self.update_theme()

    def update_theme(self):
        self.setStyleSheet(f"background-color: {theme.SIDEBAR_BG}; border: none; border-right: 1px solid {theme.BORDER};")
        self.brand_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: 800; border: none;")
        self.brand_logo.setStyleSheet(f"background-color: {theme.CYAN}; border-radius: 8px;")
        
        for btn in self.buttons:
            if hasattr(btn, "update_style"):
                btn.update_style()
        
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.PANEL_BG};
                color: {theme.RED};
                border: 1px solid {theme.BORDER};
                border-radius: 12px;
                padding-left: 20px;
                font-size: 14px;
                text-align: left;
                min-height: 48px;
            }}
            QPushButton:hover {{
                background-color: {theme.RED};
                color: white;
            }}
        """)

    def update_translations(self):
        for btn in self.buttons:
            if hasattr(btn, "update_translations"):
                btn.update_translations()
        
        self.logout_btn.setText(f"🚪  {self.lang_manager.get_text('logout')}")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 20, 30)
        layout.setSpacing(8)

        # Brand Section
        brand_container = QHBoxLayout()
        self.brand_logo = QFrame()
        self.brand_logo.setFixedSize(32, 32)
        
        self.brand_label = QLabel("Đăng Khoa")
        
        brand_container.addWidget(self.brand_logo)
        brand_container.addWidget(self.brand_label)
        brand_container.addStretch()
        
        layout.addLayout(brand_container)
        layout.addSpacing(40)

        # Navigation Buttons
        nav_items = [
            ("dashboard", "🏠"),
            ("account", "👤"),
            ("wallet", "💳"),
            ("transfer", "💸"),
            ("notifications", "🔔"),
            ("settings", "⚙️")
        ]

        for i, (key, icon) in enumerate(nav_items):
            btn = SidebarButton(key, icon, is_active=(i == 0))
            btn.clicked.connect(lambda checked, index=i: self.handle_nav_click(index))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch()

        # Logout Button
        self.logout_btn = SidebarButton("logout", "🚪")
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(self.logout_btn)

    def handle_nav_click(self, index):
        for i, btn in enumerate(self.buttons):
            btn.set_active(i == index)
        self.nav_changed.emit(index)
