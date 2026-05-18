from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import src.core.theme as theme

class NotificationHistoryCard(QFrame):
    """Modern row-style card for notification history management."""
    delete_requested = pyqtSignal(int) # notif_id

    def __init__(self, notif_id, title, n_type, priority, target, time_str):
        super().__init__()
        self.setObjectName("NotificationHistoryCard")
        self.notif_id = notif_id
        self.title_text = title
        self.n_type = n_type
        self.priority = priority
        self.target = target
        self.time_str = time_str
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.title_lbl = QLabel(self.title_text)
        self.title_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        info_layout.addWidget(self.title_lbl)

        sub_info = QHBoxLayout()
        sub_info.setSpacing(10)
        
        self.target_lbl = QLabel(f"Target: {self.target}")
        self.target_lbl.setFont(QFont("Segoe UI", 8))
        sub_info.addWidget(self.target_lbl)

        self.time_lbl = QLabel(self.time_str)
        self.time_lbl.setFont(QFont("Segoe UI", 8))
        sub_info.addWidget(self.time_lbl)
        
        sub_info.addStretch()
        info_layout.addLayout(sub_info)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Badges
        self.type_badge = self._create_badge(self.n_type)
        layout.addWidget(self.type_badge)

        self.priority_badge = self._create_badge(self.priority)
        layout.addWidget(self.priority_badge)

        # Actions
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.notif_id))
        layout.addWidget(self.delete_btn)

    def _create_badge(self, text):
        lbl = QLabel(text)
        lbl.setMinimumSize(85, 24)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        return lbl

    def update_theme(self):
        theme.update_globals()
        
        self.setStyleSheet(f"""
            QFrame#NotificationHistoryCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: {theme.TEXT_PRIMARY};
            }}
        """)

        self.target_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
        self.time_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")

        # Color badges (Simplified for history row)
        badge_style = "background-color: {color}20; color: {color}; border: 1px solid {color}40; border-radius: 4px;"
        
        self.type_badge.setStyleSheet(badge_style.format(color=theme.CYAN))
        self.priority_badge.setStyleSheet(badge_style.format(color=theme.ORANGE))

        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.PANEL_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme.RED}20;
                border-color: {theme.RED};
            }}
        """)
