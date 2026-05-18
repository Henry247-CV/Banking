from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import src.core.theme as theme

class ReportPreviewCard(QFrame):
    """Enterprise-grade preview card for planned report modules."""

    STATUS_COLORS = {
        "IN DEVELOPMENT": theme.CYAN,
        "PLANNED": theme.ORANGE,
        "ENTERPRISE": "#A78BFA"
    }

    def __init__(self, title, description, status="PLANNED", icon="📊"):
        super().__init__()
        self.setObjectName("ReportPreviewCard")
        self.title_text = title
        self.desc_text = description
        self.status = status
        self.icon_str = icon
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Top row: Icon + Badge
        top_row = QHBoxLayout()
        self.icon_lbl = QLabel(self.icon_str)
        self.icon_lbl.setObjectName("ReportPreviewIcon")
        self.icon_lbl.setFixedSize(44, 44)
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setFont(QFont("Segoe UI Emoji", 20))
        top_row.addWidget(self.icon_lbl)
        top_row.addStretch()

        self.badge_lbl = QLabel(self.status)
        self.badge_lbl.setObjectName("ReportPreviewBadge")
        self.badge_lbl.setMinimumHeight(26)
        self.badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        # Padding is handled in stylesheet
        top_row.addWidget(self.badge_lbl)
        
        layout.addLayout(top_row)

        # Title
        self.title_lbl = QLabel(self.title_text)
        self.title_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(self.title_lbl)

        # Description
        self.desc_lbl = QLabel(self.desc_text)
        self.desc_lbl.setFont(QFont("Segoe UI", 10))
        self.desc_lbl.setWordWrap(True)
        layout.addWidget(self.desc_lbl)
        
        layout.addStretch()

        # Disabled Action Button
        self.action_btn = QPushButton("Preview")
        self.action_btn.setObjectName("ReportPreviewBtn")
        self.action_btn.setFixedHeight(36)
        self.action_btn.setEnabled(False)
        self.action_btn.setToolTip("Feature available in future update.")
        layout.addWidget(self.action_btn)

    def update_translations(self, lang_manager, title_key, desc_key, status_key, btn_key="admin_preview"):
        self.title_lbl.setText(lang_manager.get_text(title_key))
        self.desc_lbl.setText(lang_manager.get_text(desc_key))
        self.badge_lbl.setText(lang_manager.get_text(status_key))
        self.action_btn.setText(lang_manager.get_text(btn_key))
        self.action_btn.setToolTip(lang_manager.get_text("admin_feature_future"))

    def update_theme(self):
        theme.update_globals()
        
        accent = self.STATUS_COLORS.get(self.status, theme.CYAN)

        self.setStyleSheet(f"""
            QFrame#ReportPreviewCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 12px;
            }}
            QFrame#ReportPreviewCard:hover {{
                border-color: {accent};
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: {theme.TEXT_PRIMARY};
            }}
        """)

        self.desc_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
        
        self.icon_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {theme.PANEL_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 10px;
            }}
        """)

        self.badge_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {accent}15;
                color: {accent};
                border: 1px solid {accent}40;
                border-radius: 12px;
                padding: 0 10px;
            }}
        """)

        self.action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_SECONDARY};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                font-weight: bold;
            }}
        """)
