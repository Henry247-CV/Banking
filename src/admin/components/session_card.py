"""Session Card — UI component for displaying an active session in the admin panel."""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
import src.core.theme as theme
from src.core.language_manager import LanguageManager


class SessionCard(QFrame):
    """Card displaying details of an active session with termination controls."""
    
    # Signal emitted when admin clicks terminate: passes session ID
    terminate_requested = pyqtSignal(int)
    
    def __init__(self, session_id, username, created_at, status="ACTIVE"):
        super().__init__()
        self.session_id = session_id
        self.username = username
        self.created_at = created_at
        self.status = status
        self.lang_manager = LanguageManager()
        self._setup_ui()
        self.update_theme()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        # User Icon
        self.icon_label = QLabel("👤")
        self.icon_label.setFixedWidth(24)
        
        # Details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)
        
        self.user_label = QLabel(self.username)
        self.time_label = QLabel(self.created_at[:16] if self.created_at else "Unknown")
        
        details_layout.addWidget(self.user_label)
        details_layout.addWidget(self.time_label)
        
        # Status Badge
        self.status_label = QLabel(self.status)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFixedSize(60, 24)
        
        # Action Button
        self.terminate_btn = QPushButton(self.lang_manager.get_text("admin_end_session"))
        self.terminate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.terminate_btn.setFixedHeight(30)
        self.terminate_btn.setFixedWidth(100)
        self.terminate_btn.clicked.connect(lambda: self.terminate_requested.emit(self.session_id))
        
        layout.addWidget(self.icon_label)
        layout.addLayout(details_layout)
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(self.terminate_btn)

    def update_theme(self):
        theme.update_globals()
        
        self.setStyleSheet(f"""
            SessionCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 8px;
            }}
        """)
        
        self.icon_label.setStyleSheet("font-size: 20px; border: none; background: transparent;")
        
        self.user_label.setStyleSheet(f"""
            color: {theme.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)
        
        self.time_label.setStyleSheet(f"""
            color: {theme.TEXT_SECONDARY};
            font-size: 11px;
            border: none;
            background: transparent;
        """)
        
        # Status color
        status_color = theme.CYAN if self.status == "ACTIVE" else theme.TEXT_SECONDARY
        self.status_label.setStyleSheet(f"""
            color: {status_color};
            background-color: {theme.PANEL_BG};
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
        """)
        
        self.terminate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.RED};
                border: 1px solid {theme.RED};
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme.RED};
                color: white;
            }}
        """)
        
    def update_translations(self):
        self.terminate_btn.setText(self.lang_manager.get_text("admin_end_session"))
