from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *

class NotificationCard(QFrame):
    def __init__(self, title, message, timestamp, is_read=False):
        super().__init__()
        self.is_read = is_read
        self.title = title
        self.message = message
        self.timestamp = timestamp
        self.setup_ui()
        self.update_theme()

    def update_theme(self):
        bg_color = theme.CARD_BG if self.is_read else theme.PANEL_BG
        border_style = f"border-left: 4px solid {theme.CYAN};" if not self.is_read else f"border-left: 4px solid {theme.BORDER};"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {theme.BORDER};
                border-radius: 12px;
                {border_style}
            }}
            QFrame:hover {{
                border: 1px solid {theme.CYAN};
            }}
        """)
        self.title_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 15px; font-weight: bold; border: none; background: transparent;")
        self.time_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px; border: none; background: transparent;")
        self.msg_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 13px; border: none; background: transparent;")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)

        header_layout = QHBoxLayout()
        self.title_label = QLabel(self.title)
        
        self.time_label = QLabel(str(self.timestamp)[:16])
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.time_label)

        self.msg_label = QLabel(self.message)
        self.msg_label.setWordWrap(True)

        layout.addLayout(header_layout)
        layout.addWidget(self.msg_label)
