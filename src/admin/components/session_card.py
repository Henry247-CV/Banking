from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import src.core.theme as theme
from src.core.language_manager import LanguageManager

class SessionCard(QFrame):
    terminate_requested = pyqtSignal(int) # session_id

    def __init__(self, session_id, username, login_time):
        super().__init__()
        self.setObjectName("SessionCard")
        self.session_id = session_id
        self.username = username
        self.login_time = login_time
        self.lang_manager = LanguageManager()
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 10, 16, 10)
        self.layout.setSpacing(12)

        # Icon
        self.icon_lbl = QLabel("👤")
        self.icon_lbl.setObjectName("SessionIcon")
        self.icon_lbl.setFixedSize(28, 28)
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setFont(QFont("Segoe UI Emoji", 14))
        self.layout.addWidget(self.icon_lbl)

        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)

        self.user_lbl = QLabel(self.username)
        self.user_lbl.setObjectName("SessionUser")
        user_font = QFont("Segoe UI", 10)
        user_font.setBold(True)
        self.user_lbl.setFont(user_font)
        info_layout.addWidget(self.user_lbl)

        self.time_lbl = QLabel(f"Logged in: {self.login_time}")
        self.time_lbl.setObjectName("SessionTime")
        self.time_lbl.setFont(QFont("Segoe UI", 9))
        info_layout.addWidget(self.time_lbl)

        self.layout.addLayout(info_layout)
        self.layout.addStretch()

        # Status badge
        self.status_lbl = QLabel("ACTIVE")
        self.status_lbl.setObjectName("SessionStatusBadge")
        self.status_lbl.setMinimumSize(60, 24)
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.layout.addWidget(self.status_lbl)

        # Action button
        self.terminate_btn = QPushButton("End Session")
        self.terminate_btn.setObjectName("SessionTerminateBtn")
        self.terminate_btn.setFixedSize(100, 28)
        self.terminate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.terminate_btn.clicked.connect(lambda: self.terminate_requested.emit(self.session_id))
        self.layout.addWidget(self.terminate_btn)

    def update_theme(self):
        theme.update_globals()
        
        self.setStyleSheet(f"""
            QFrame#SessionCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: {theme.TEXT_PRIMARY};
            }}
            QLabel#SessionTime {{
                color: {theme.TEXT_SECONDARY};
            }}
            QLabel#SessionStatusBadge {{
                background-color: {theme.GREEN}20;
                color: {theme.GREEN};
                border: 1px solid {theme.GREEN}40;
                border-radius: 10px;
            }}
            QPushButton#SessionTerminateBtn {{
                background-color: transparent;
                color: {theme.RED};
                border: 1px solid {theme.RED};
                border-radius: 6px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton#SessionTerminateBtn:hover {{
                background-color: {theme.RED};
                color: white;
            }}
        """)

    def update_translations(self):
        self.terminate_btn.setText(self.lang_manager.get_text("admin_end_session"))
        # We might need to update the time label prefix if we had translation for "Logged in"
