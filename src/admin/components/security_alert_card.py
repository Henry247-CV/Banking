"""Security Alert Card — UI component for displaying security warnings."""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
import src.core.theme as theme

class SecurityAlertCard(QFrame):
    """Card displaying a security alert (Warning or Critical)."""
    
    def __init__(self, alert_type, title, desc):
        super().__init__()
        self.alert_type = alert_type
        self.title_text = title
        self.desc_text = desc
        self._setup_ui()
        self.update_theme()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        # Icon
        self.icon_label = QLabel()
        if self.alert_type == "CRITICAL":
            self.icon_label.setText("⛔")
        else:
            self.icon_label.setText("⚠")
        self.icon_label.setFixedWidth(24)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        self.title_label = QLabel(self.title_text)
        self.desc_label = QLabel(self.desc_text)
        self.desc_label.setWordWrap(True)
        
        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.desc_label)
        
        layout.addWidget(self.icon_label)
        layout.addLayout(content_layout)
        layout.addStretch()

    def update_theme(self):
        theme.update_globals()
        
        border_color = theme.RED if self.alert_type == "CRITICAL" else theme.ORANGE
        
        self.setStyleSheet(f"""
            SecurityAlertCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-left: 4px solid {border_color};
                border-radius: 8px;
            }}
        """)
        
        self.icon_label.setStyleSheet(f"""
            font-size: 20px;
            border: none;
            background: transparent;
        """)
        
        self.title_label.setStyleSheet(f"""
            color: {border_color};
            font-size: 14px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)
        
        self.desc_label.setStyleSheet(f"""
            color: {theme.TEXT_SECONDARY};
            font-size: 12px;
            border: none;
            background: transparent;
        """)
