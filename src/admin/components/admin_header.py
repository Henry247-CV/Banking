from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit,
)
from PyQt6.QtCore import Qt
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from datetime import datetime


class AdminHeader(QFrame):
    """Enterprise admin header with title, search, notifications, and admin info."""

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setObjectName("AdminHeader")
        self.setFixedHeight(70)
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 28, 0)
        layout.setSpacing(16)

        # Left: Page title
        title_section = QVBoxLayout()
        title_section.setSpacing(0)

        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("AdminHeaderTitle")
        self.page_subtitle = QLabel(self.lang_manager.get_text("admin_header_subtitle"))
        self.page_subtitle.setObjectName("AdminHeaderSubtitle")

        title_section.addWidget(self.page_title)
        title_section.addWidget(self.page_subtitle)

        layout.addLayout(title_section)
        layout.addStretch()

        # Center: Search
        self.search_input = QLineEdit()
        self.search_input.setObjectName("AdminHeaderSearch")
        self.search_input.setPlaceholderText(self.lang_manager.get_text("admin_search_placeholder"))
        self.search_input.setFixedWidth(260)
        self.search_input.setFixedHeight(36)
        layout.addWidget(self.search_input)

        layout.addStretch()

        # Right: Date + Notification + Admin
        right_section = QHBoxLayout()
        right_section.setSpacing(12)

        self.date_label = QLabel(datetime.now().strftime("%B %d, %Y"))
        self.date_label.setObjectName("AdminHeaderDate")

        self.notify_btn = QPushButton("🔔")
        self.notify_btn.setObjectName("AdminHeaderNotify")
        self.notify_btn.setFixedSize(36, 36)
        self.notify_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Admin avatar
        self.admin_avatar = QFrame()
        self.admin_avatar.setObjectName("AdminHeaderAvatar")
        self.admin_avatar.setFixedSize(36, 36)

        avatar_label = QLabel("A")
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px; border: none; background: transparent;")
        avatar_layout = QVBoxLayout(self.admin_avatar)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.addWidget(avatar_label)

        self.admin_name = QLabel("Admin")
        self.admin_name.setObjectName("AdminHeaderName")

        right_section.addWidget(self.date_label)
        right_section.addWidget(self.notify_btn)
        right_section.addWidget(self.admin_avatar)
        right_section.addWidget(self.admin_name)

        layout.addLayout(right_section)

    def set_page_title(self, title):
        """Update the displayed page title."""
        self.page_title.setText(title)

    def update_theme(self):
        theme.update_globals()

        self.setStyleSheet(f"""
            QFrame#AdminHeader {{
                background-color: {theme.BACKGROUND};
                border-bottom: 1px solid {theme.BORDER};
            }}
            QLabel#AdminHeaderTitle {{
                color: {theme.TEXT_PRIMARY};
                font-size: 18px;
                font-weight: 800;
            }}
            QLabel#AdminHeaderSubtitle {{
                color: {theme.TEXT_SECONDARY};
                font-size: 11px;
                font-weight: 500;
            }}
            QLineEdit#AdminHeaderSearch {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 12px;
            }}
            QLineEdit#AdminHeaderSearch:focus {{
                border: 1px solid {theme.CYAN};
            }}
            QLabel#AdminHeaderDate {{
                color: {theme.TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton#AdminHeaderNotify {{
                background-color: {theme.PANEL_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 18px;
                font-size: 14px;
                color: {theme.TEXT_PRIMARY};
            }}
            QPushButton#AdminHeaderNotify:hover {{
                border: 1px solid {theme.CYAN};
                background-color: {theme.CARD_BG};
                color: {theme.CYAN};
            }}
            QFrame#AdminHeaderAvatar {{
                background-color: {theme.CYAN};
                border-radius: 18px;
            }}
            QLabel#AdminHeaderName {{
                color: {theme.TEXT_PRIMARY};
                font-size: 13px;
                font-weight: 600;
            }}
        """)

    def update_translations(self):
        self.page_subtitle.setText(self.lang_manager.get_text("admin_header_subtitle"))
        self.search_input.setPlaceholderText(
            self.lang_manager.get_text("admin_search_placeholder")
        )
        # Update date format based on locale if needed
        self.date_label.setText(datetime.now().strftime("%B %d, %Y"))
