from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.core.theme import *
from src.core.styles import *

from PyQt6.QtCore import Qt, pyqtSignal

class NotificationCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, title, message, timestamp, is_read=False, priority="LOW", n_type="INFO"):
        super().__init__()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_read = is_read
        self.title = title
        self.message = message
        self.timestamp = timestamp
        self.priority = priority
        self.n_type = n_type
        self.setup_ui()
        self.update_theme()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def update_theme(self):
        theme.update_globals()
        bg_color = theme.CARD_BG if self.is_read else theme.PANEL_BG
        
        type_colors = {
            "INFO": theme.CYAN,
            "WARNING": theme.ORANGE,
            "SECURITY": theme.RED,
            "MAINTENANCE": "#A78BFA",
            "PROMOTION": theme.GREEN
        }
        accent_color = type_colors.get(self.n_type, theme.CYAN)
        
        border_style = f"border-left: 4px solid {accent_color};" if not self.is_read else f"border-left: 4px solid {theme.BORDER};"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {theme.BORDER};
                border-radius: 12px;
                {border_style}
            }}
            QFrame:hover {{
                border: 1px solid {accent_color};
            }}
        """)
        self.title_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 15px; font-weight: bold; border: none; background: transparent;")
        self.time_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px; border: none; background: transparent;")
        self.msg_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 13px; border: none; background: transparent;")

        badge_style = "background-color: {color}20; color: {color}; border: 1px solid {color}40; border-radius: 4px;"
        
        priority_colors = {
            "LOW": theme.TEXT_SECONDARY,
            "MEDIUM": theme.ORANGE,
            "HIGH": "#FB923C",
            "CRITICAL": theme.RED
        }
        
        self.type_badge.setStyleSheet(badge_style.format(color=accent_color))
        self.priority_badge.setStyleSheet(badge_style.format(color=priority_colors.get(self.priority, theme.TEXT_SECONDARY)))

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)

        header_layout = QHBoxLayout()
        self.title_label = QLabel(self.title)
        
        # Badges
        self.type_badge = QLabel(self.n_type)
        self.type_badge.setMinimumSize(70, 22)
        self.type_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_badge.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        
        self.priority_badge = QLabel(self.priority)
        self.priority_badge.setMinimumSize(60, 22)
        self.priority_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.priority_badge.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        
        self.time_label = QLabel(str(self.timestamp)[:16])
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.type_badge)
        if self.priority != "LOW":
            header_layout.addWidget(self.priority_badge)
        header_layout.addStretch()
        header_layout.addWidget(self.time_label)

        self.msg_label = QLabel(self.message)
        self.msg_label.setWordWrap(True)

        layout.addLayout(header_layout)
        layout.addWidget(self.msg_label)
