from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpacerItem, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager


class AdminSidebarButton(QPushButton):
    """Compact enterprise navigation button for admin sidebar."""

    def __init__(self, key, icon, is_active=False):
        self.key = key
        self.icon = icon
        self.lang_manager = LanguageManager()
        text = f"{self.icon}  {self.lang_manager.get_text(self.key)}"
        super().__init__(text)
        self.is_active = is_active
        self.setFixedHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

    def update_translations(self):
        self.setText(f"{self.icon}  {self.lang_manager.get_text(self.key)}")

    def update_style(self):
        theme.update_globals()
        if self.is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.CYAN};
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding-left: 16px;
                    font-size: 13px;
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
                    border-radius: 8px;
                    padding-left: 16px;
                    font-size: 13px;
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


class AdminSidebar(QFrame):
    """Enterprise-style sidebar for admin panel navigation.
    
    Darker than user sidebar, compact spacing, cyan active indicator.
    """
    nav_changed = pyqtSignal(int)
    logout_requested = pyqtSignal()

    # Navigation item definitions
    NAV_ITEMS = [
        ("admin_dashboard", "📊"),
        ("admin_users", "👥"),
        ("admin_transactions", "💹"),
        ("admin_settings", "⚙️"),
    ]

    # Future placeholder items
    FUTURE_ITEMS = [
        ("admin_reports", "📋"),
        ("admin_security", "🛡️"),
    ]

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setFixedWidth(220)
        self.buttons = []
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 24, 14, 20)
        layout.setSpacing(4)

        # Brand Section — Admin badge
        brand_container = QHBoxLayout()
        brand_container.setSpacing(10)

        self.brand_logo = QFrame()
        self.brand_logo.setFixedSize(28, 28)

        self.brand_label = QLabel("DK Admin")
        brand_container.addWidget(self.brand_logo)
        brand_container.addWidget(self.brand_label)
        brand_container.addStretch()

        layout.addLayout(brand_container)
        layout.addSpacing(8)

        # Admin badge
        self.admin_badge = QLabel("CONTROL CENTER")
        self.admin_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.admin_badge)
        layout.addSpacing(20)

        # Section label
        self.nav_section_label = QLabel("NAVIGATION")
        layout.addWidget(self.nav_section_label)
        layout.addSpacing(6)

        # Navigation Buttons
        for i, (key, icon) in enumerate(self.NAV_ITEMS):
            btn = AdminSidebarButton(key, icon, is_active=(i == 0))
            btn.clicked.connect(lambda checked, index=i: self._handle_nav_click(index))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addSpacing(16)

        # Future placeholders section
        self.future_section_label = QLabel("COMING SOON")
        layout.addWidget(self.future_section_label)
        layout.addSpacing(6)

        self.future_buttons = []
        for key, icon in self.FUTURE_ITEMS:
            btn = QPushButton(f"{icon}  {self.lang_manager.get_text(key)}")
            btn.setFixedHeight(36)
            btn.setEnabled(False)
            btn.setCursor(Qt.CursorShape.ForbiddenCursor)
            layout.addWidget(btn)
            self.future_buttons.append((btn, key))

        layout.addStretch()

        # Logout
        self.logout_btn = QPushButton(f"🚪  {self.lang_manager.get_text('logout')}")
        self.logout_btn.setFixedHeight(42)
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(self.logout_btn)

    def _handle_nav_click(self, index):
        for i, btn in enumerate(self.buttons):
            btn.set_active(i == index)
        self.nav_changed.emit(index)

    def update_theme(self):
        theme.update_globals()

        # Sidebar background — darker than user sidebar for enterprise feel
        sidebar_bg = theme.SIDEBAR_BG
        if theme.ThemeManager().current_theme == "dark":
            sidebar_bg = "#060E1A"  # Even darker for admin
        
        self.setStyleSheet(f"""
            AdminSidebar {{
                background-color: {sidebar_bg};
                border: none;
                border-right: 1px solid {theme.BORDER};
            }}
        """)

        self.brand_label.setStyleSheet(f"""
            color: {theme.TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 800;
            border: none;
            background: transparent;
        """)

        self.brand_logo.setStyleSheet(f"""
            background-color: {theme.CYAN};
            border-radius: 6px;
        """)

        self.admin_badge.setStyleSheet(f"""
            color: {theme.CYAN};
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 2px;
            padding: 4px 8px;
            border: 1px solid {theme.BORDER};
            border-radius: 4px;
            background-color: {theme.PANEL_BG};
        """)

        section_style = f"""
            color: {theme.TEXT_SECONDARY};
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1.5px;
            border: none;
            background: transparent;
            padding-left: 4px;
        """
        self.nav_section_label.setStyleSheet(section_style)
        self.future_section_label.setStyleSheet(section_style)

        for btn in self.buttons:
            btn.update_style()

        # Future placeholder buttons — muted style
        for btn, key in self.future_buttons:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme.BORDER};
                    border: none;
                    border-radius: 8px;
                    padding-left: 16px;
                    font-size: 12px;
                    text-align: left;
                }}
            """)

        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.PANEL_BG};
                color: {theme.RED};
                border: 1px solid {theme.BORDER};
                border-radius: 8px;
                padding-left: 16px;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {theme.RED};
                color: white;
                border: 1px solid {theme.RED};
            }}
        """)

    def update_translations(self):
        for btn in self.buttons:
            if hasattr(btn, "update_translations"):
                btn.update_translations()
        
        self.logout_btn.setText(f"🚪  {self.lang_manager.get_text('logout')}")
        
        for btn, key in self.future_buttons:
            btn.setText(f"{btn.text().split('  ')[0]}  {self.lang_manager.get_text(key)}")
