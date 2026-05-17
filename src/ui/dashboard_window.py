from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QLabel,
    QFrame,
    QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.theme import *
from src.core.styles import *
from src.core.utils import safe_text
from src.ui.components.sidebar import Sidebar
from src.ui.tabs.dashboard_tab import DashboardTab
from src.ui.tabs.account_tab import AccountTab
from src.ui.tabs.wallet_tab import WalletTab
from src.ui.tabs.transfer_tab import TransferTab
from src.ui.tabs.notification_tab import NotificationTab
from src.ui.tabs.settings_tab import SettingsTab

from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.core.styles import get_styles

class DashboardWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()

        self.setWindowTitle("Đăng Khoa Bank - Premium Desktop")
        self.resize(1240, 780)
        self.setMinimumSize(1000, 680)
        
        # Connect managers
        self.lang_manager.language_changed.connect(self.update_translations)
        self.theme_manager.theme_changed.connect(self.update_theme)

        self.setup_ui()
        self.update_theme()
        self.update_translations()

    def update_theme(self):
        styles = get_styles()
        self.setStyleSheet(styles["GLOBAL_STYLE"])
        self.header.setStyleSheet(f"background-color: {theme.BACKGROUND}; border-bottom: 1px solid {theme.BORDER};")
        self.page_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 22px; font-weight: 800; border: none; background: transparent;")
        self.username_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        self.acc_label.setStyleSheet(f"color: {theme.CYAN}; font-size: 11px; font-weight: 600; border: none; background: transparent;")
        
        # Refresh all tabs theme
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if hasattr(widget, "update_theme"):
                widget.update_theme()

    def update_translations(self):
        # Update header and titles
        index = self.stack.currentIndex()
        titles = [
            self.lang_manager.get_text("dashboard"),
            self.lang_manager.get_text("account"),
            self.lang_manager.get_text("wallet"),
            self.lang_manager.get_text("transfer"),
            self.lang_manager.get_text("notifications"),
            self.lang_manager.get_text("settings")
        ]
        self.page_title.setText(titles[index])
        
        # Update all tabs translations
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if hasattr(widget, "update_translations"):
                widget.update_translations()
        
        # Refresh sidebar
        if hasattr(self.sidebar, "update_translations"):
            self.sidebar.update_translations()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Sidebar
        self.sidebar = Sidebar()
        self.sidebar.nav_changed.connect(self.handle_nav_change)
        self.sidebar.logout_requested.connect(self.logout_requested.emit)
        self.main_layout.addWidget(self.sidebar)

        # 2. Main Content Area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Top Header
        self.header = QFrame()
        self.header.setFixedHeight(80)
        self.header.setStyleSheet(f"background-color: {BACKGROUND}; border-bottom: 1px solid {BORDER};")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(40, 0, 40, 0)

        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 22px; font-weight: 800; border: none; background: transparent;")
        
        user_info_layout = QHBoxLayout()
        user_info_layout.setSpacing(20)
        
        notify_btn = QPushButton("🔔")
        notify_btn.setFixedSize(40, 40)
        notify_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PANEL_BG};
                border: 1px solid {BORDER};
                border-radius: 20px;
                color: {TEXT_PRIMARY};
                font-size: 16px;
            }}
            QPushButton:hover {{
                border: 1px solid {CYAN};
                background-color: {CARD_BG};
            }}
        """)
        notify_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        notify_btn.clicked.connect(lambda: self.sidebar.handle_nav_click(4))
        
        user_details = QVBoxLayout()
        user_details.setSpacing(0)
        
        display_name = safe_text(self.user_data.get('full_name'), self.user_data.get('username'))
        self.username_label = QLabel(display_name)
        self.username_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        
        acc_num = safe_text(self.user_data.get('account_number'), "No Account ID")
        self.acc_label = QLabel(acc_num)
        self.acc_label.setStyleSheet(f"color: {CYAN}; font-size: 11px; font-weight: 600; border: none; background: transparent;")
        
        user_details.addWidget(self.username_label)
        user_details.addWidget(self.acc_label)
        
        avatar = QFrame()
        avatar.setFixedSize(40, 40)
        avatar.setStyleSheet(f"background-color: {CYAN}; border-radius: 20px; border: 2px solid {BORDER};")
        avatar_label = QLabel(self.user_data.get('username', "U")[0].upper())
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
        av_lay = QVBoxLayout(avatar)
        av_lay.setContentsMargins(0,0,0,0)
        av_lay.addWidget(avatar_label)

        user_info_layout.addWidget(notify_btn)
        user_info_layout.addLayout(user_details)
        user_info_layout.addWidget(avatar)

        header_layout.addWidget(self.page_title)
        header_layout.addStretch()
        header_layout.addLayout(user_info_layout)

        self.content_layout.addWidget(self.header)

        # Stacked Pages
        self.stack = QStackedWidget()
        self.dashboard_tab = DashboardTab(self.user_data)
        self.account_tab = AccountTab(self.user_data)
        self.wallet_tab = WalletTab(self.user_data)
        self.transfer_tab = TransferTab(self.user_data)
        self.notification_tab = NotificationTab(self.user_data)
        self.settings_tab = SettingsTab(self.user_data)

        self.stack.addWidget(self.dashboard_tab)
        self.stack.addWidget(self.account_tab)
        self.stack.addWidget(self.wallet_tab)
        self.stack.addWidget(self.transfer_tab)
        self.stack.addWidget(self.notification_tab)
        self.stack.addWidget(self.settings_tab)

        # Connect signals
        self.transfer_tab.balance_updated.connect(self.refresh_all_tabs)

        self.content_layout.addWidget(self.stack)
        self.main_layout.addWidget(self.content_area)

    def handle_nav_change(self, index):
        self.stack.setCurrentIndex(index)
        titles = ["Dashboard", "Account Details", "Wallet Management", "Money Transfer", "Notifications", "Settings"]
        self.page_title.setText(titles[index])
        
        current_widget = self.stack.currentWidget()
        if hasattr(current_widget, "update_ui"):
            current_widget.update_ui()
        elif hasattr(current_widget, "refresh_history"):
            current_widget.refresh_history()

        display_name = safe_text(self.user_data.get('full_name'), self.user_data.get('username'))
        self.username_label.setText(display_name)
        self.acc_label.setText(safe_text(self.user_data.get('account_number'), "No Account ID"))

    def refresh_all_tabs(self):
        """Refreshes all tabs that display user data."""
        # Refetch latest user data to get updated balance and tier
        from src.services.user_service import UserService
        latest_data = UserService.refresh_user_data(self.user_data['username'])
        if latest_data:
            self.user_data.update(latest_data)

        self.dashboard_tab.update_ui()
        self.wallet_tab.update_ui()
        self.account_tab.refresh_ui()
        self.notification_tab.update_ui()
        self.settings_tab.update_ui()
