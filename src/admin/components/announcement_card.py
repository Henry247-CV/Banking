from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import src.core.theme as theme

class AnnouncementCard(QFrame):
    """Modern announcement card for admin dashboard display."""

    TYPE_COLORS = {
        "INFO": "#00D1FF",
        "WARNING": "#FFB74D",
        "SECURITY": "#EF4444",
        "MAINTENANCE": "#A78BFA",
        "PROMOTION": "#00E676"
    }

    PRIORITY_COLORS = {
        "LOW": "#9BB0C7",
        "MEDIUM": "#FFB74D",
        "HIGH": "#FB923C",
        "CRITICAL": "#EF4444"
    }

    def __init__(self, title, n_type, priority, time_str, message=""):
        super().__init__()
        self.setObjectName("AnnouncementCard")
        self.title_text = title
        self.n_type = n_type
        self.priority = priority
        self.time_str = time_str
        self.message = message
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Header: Title + Type + Priority
        header = QHBoxLayout()
        header.setSpacing(8)

        self.title_lbl = QLabel(self.title_text)
        title_font = QFont("Segoe UI", 11)
        title_font.setBold(True)
        self.title_lbl.setFont(title_font)
        header.addWidget(self.title_lbl)
        header.addStretch()

        # Badges
        self.type_badge = QLabel(self.n_type)
        self.type_badge.setMinimumSize(90, 24)
        self.type_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_badge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        header.addWidget(self.type_badge)

        self.priority_badge = QLabel(self.priority)
        self.priority_badge.setMinimumSize(70, 24)
        self.priority_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.priority_badge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        header.addWidget(self.priority_badge)

        layout.addLayout(header)

        # Message (if any)
        if self.message:
            self.msg_lbl = QLabel(self.message)
            self.msg_lbl.setWordWrap(True)
            self.msg_lbl.setFont(QFont("Segoe UI", 10))
            layout.addWidget(self.msg_lbl)

        # Footer: Time
        self.time_lbl = QLabel(self.time_str)
        self.time_lbl.setFont(QFont("Segoe UI", 8))
        layout.addWidget(self.time_lbl)

    def update_theme(self):
        theme.update_globals()
        
        type_color = self.TYPE_COLORS.get(self.n_type, theme.CYAN)
        priority_color = self.PRIORITY_COLORS.get(self.priority, theme.TEXT_SECONDARY)

        self.setStyleSheet(f"""
            QFrame#AnnouncementCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-left: 4px solid {type_color};
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: {theme.TEXT_PRIMARY};
            }}
        """)

        self.type_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {type_color}20;
                color: {type_color};
                border: 1px solid {type_color}40;
                border-radius: 4px;
            }}
        """)

        self.priority_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {priority_color}20;
                color: {priority_color};
                border: 1px solid {priority_color}40;
                border-radius: 4px;
            }}
        """)

        self.time_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
        if hasattr(self, 'msg_lbl'):
            self.msg_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
