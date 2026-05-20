from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.core.styles import get_styles

from src.admin.components.admin_sidebar import AdminSidebar
from src.admin.components.admin_header import AdminHeader
from src.admin.tabs.admin_dashboard_tab import AdminDashboardTab
from src.admin.tabs.admin_users_tab import AdminUsersTab
from src.admin.tabs.admin_transactions_tab import AdminTransactionsTab
from src.admin.tabs.admin_reports_tab import AdminReportsTab
from src.admin.tabs.admin_settings_tab import AdminSettingsTab


class AdminWindow(QMainWindow):
    """Main admin panel window with sidebar + header + stacked content.
    
    Layout:
    ┌──────────┬───────────────────────────────┐
    │ Sidebar  │ Header                        │
    │          ├───────────────────────────────┤
    │          │                               │
    │          │ Dashboard / Users / etc.      │
    │          │                               │
    └──────────┴───────────────────────────────┘
    """
    logout_requested = pyqtSignal()

    # Page title keys for each tab
    TAB_TITLE_KEYS = [
        "admin_dashboard",
        "admin_users",
        "admin_transactions",
        "admin_reports",
        "admin_settings",
    ]

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()

        self.setObjectName("AdminWindow")
        self.setWindowTitle("Đăng Khoa Bank Admin")
        self.resize(1280, 800)
        self.setMinimumSize(1000, 680)

        # Connect global managers for live synchronization
        self.lang_manager.language_changed.connect(self.update_translations)
        self.theme_manager.theme_changed.connect(self.update_theme)

        self._setup_ui()
        self.update_theme()
        self.update_translations()

    def _setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("AdminCentralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Admin Sidebar
        self.sidebar = AdminSidebar()
        self.sidebar.setObjectName("AdminSidebar")
        self.sidebar.nav_changed.connect(self._handle_nav_change)
        self.sidebar.logout_requested.connect(self._handle_logout)
        main_layout.addWidget(self.sidebar)

        # 2. Content Area (Header + Stacked Pages)
        content_area = QWidget()
        content_area.setObjectName("AdminContentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Admin Header
        self.header = AdminHeader()
        self.header.setObjectName("AdminHeader")
        content_layout.addWidget(self.header)

        # Stacked Widget for tabs
        self.stack = QStackedWidget()
        self.stack.setObjectName("AdminStack")
        self.dashboard_tab = AdminDashboardTab()
        self.users_tab = AdminUsersTab()
        self.transactions_tab = AdminTransactionsTab()
        self.reports_tab = AdminReportsTab()
        self.settings_tab = AdminSettingsTab()

        self.stack.addWidget(self.dashboard_tab)
        self.stack.addWidget(self.users_tab)
        self.stack.addWidget(self.transactions_tab)
        self.stack.addWidget(self.reports_tab)
        self.stack.addWidget(self.settings_tab)

        # Connect settings signals
        self.settings_tab.logout_btn.clicked.connect(self._handle_logout)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_area)

    def _handle_nav_change(self, index):
        """Switch stacked widget page and update header title."""
        self.stack.setCurrentIndex(index)

        # Update header title
        title_key = self.TAB_TITLE_KEYS[index]
        self.header.set_page_title(self.lang_manager.get_text(title_key))

        # Refresh current tab data
        current_widget = self.stack.currentWidget()
        if hasattr(current_widget, "update_ui"):
            current_widget.update_ui()
        elif hasattr(current_widget, "load_data"):
            current_widget.load_data()

    def _handle_logout(self):
        """Emit logout and close admin window."""
        self.logout_requested.emit()
        self.close()

    def update_theme(self, _theme_name=None):
        """Refresh all admin panel themes using centralized design system."""
        styles = get_styles()
        self.setStyleSheet(styles["GLOBAL_STYLE"])

        self.sidebar.update_theme()
        self.header.update_theme()

        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if hasattr(widget, "update_theme"):
                widget.update_theme()

    def update_translations(self, _lang=None):
        """Refresh all admin panel translations instantly."""
        self.sidebar.update_translations()
        self.header.update_translations()

        # Update header title for current tab
        current_index = self.stack.currentIndex()
        if current_index >= 0:
            title_key = self.TAB_TITLE_KEYS[current_index]
            self.header.set_page_title(self.lang_manager.get_text(title_key))

        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if hasattr(widget, "update_translations"):
                widget.update_translations()
