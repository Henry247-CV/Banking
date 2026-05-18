from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import src.core.theme as theme

class SecurityAlertCard(QFrame):
    def __init__(self, alert_type, title, description):
        super().__init__()
        self.setObjectName("SecurityAlertCard")
        self.alert_type = alert_type # CRITICAL, WARNING, INFO
        self.title_text = title
        self.desc_text = description
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 12, 16, 12)
        self.layout.setSpacing(16)

        # Icon
        self.icon_lbl = QLabel()
        self.icon_lbl.setObjectName("AlertIcon")
        self.icon_lbl.setFixedSize(32, 32)
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setFont(QFont("Segoe UI Emoji", 16))
        if self.alert_type == "CRITICAL":
            self.icon_lbl.setText("🚨")
        elif self.alert_type == "WARNING":
            self.icon_lbl.setText("⚠️")
        else:
            self.icon_lbl.setText("ℹ️")
        self.layout.addWidget(self.icon_lbl)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        self.title_lbl = QLabel(self.title_text)
        self.title_lbl.setObjectName("AlertTitle")
        title_font = QFont("Segoe UI", 11)
        title_font.setBold(True)
        self.title_lbl.setFont(title_font)
        content_layout.addWidget(self.title_lbl)

        self.desc_lbl = QLabel(self.desc_text)
        self.desc_lbl.setObjectName("AlertDesc")
        self.desc_lbl.setFont(QFont("Segoe UI", 10))
        self.desc_lbl.setWordWrap(True)
        content_layout.addWidget(self.desc_lbl)

        self.layout.addLayout(content_layout)
        self.layout.addStretch()

    def update_theme(self):
        theme.update_globals()
        
        # Border and background color based on alert type
        border_color = theme.BORDER
        bg_color = theme.CARD_BG
        
        if self.alert_type == "CRITICAL":
            border_color = theme.RED
            accent_bg = QColor(theme.RED)
            accent_bg.setAlpha(30)
            bg_color = accent_bg.name(QColor.NameFormat.HexArgb)
        elif self.alert_type == "WARNING":
            border_color = theme.ORANGE
            accent_bg = QColor(theme.ORANGE)
            accent_bg.setAlpha(30)
            bg_color = accent_bg.name(QColor.NameFormat.HexArgb)

        self.setStyleSheet(f"""
            QFrame#SecurityAlertCard {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            QLabel#AlertIcon {{
                background: transparent;
                border: none;
            }}
            QLabel#AlertTitle {{
                background: transparent;
                border: none;
                color: {theme.RED if self.alert_type == "CRITICAL" else (theme.ORANGE if self.alert_type == "WARNING" else theme.TEXT_PRIMARY)};
            }}
            QLabel#AlertDesc {{
                background: transparent;
                border: none;
                color: {theme.TEXT_PRIMARY};
            }}
        """)
