from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import src.core.theme as theme

class ComingSoonCard(QFrame):
    """A premium placeholder card for upcoming enterprise features."""

    def __init__(self, title, description, icon="🚀"):
        super().__init__()
        self.setObjectName("ComingSoonCard")
        self.title_text = title
        self.desc_text = description
        self.icon_str = icon
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Icon
        self.icon_lbl = QLabel(self.icon_str)
        self.icon_lbl.setObjectName("ComingSoonIcon")
        self.icon_lbl.setFixedSize(40, 40)
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setFont(QFont("Segoe UI Emoji", 18))
        layout.addWidget(self.icon_lbl)

        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        self.title_lbl = QLabel(self.title_text)
        self.title_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        info_layout.addWidget(self.title_lbl)

        self.desc_lbl = QLabel(self.desc_text)
        self.desc_lbl.setFont(QFont("Segoe UI", 10))
        self.desc_lbl.setWordWrap(True)
        info_layout.addWidget(self.desc_lbl)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Badge
        self.badge_lbl = QLabel("Coming Soon")
        self.badge_lbl.setObjectName("ComingSoonBadge")
        self.badge_lbl.setFixedSize(85, 24)
        self.badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        layout.addWidget(self.badge_lbl)

    def update_translations(self, lang_manager, title_key, desc_key, badge_key="admin_coming_soon"):
        self.title_lbl.setText(lang_manager.get_text(title_key))
        self.desc_lbl.setText(lang_manager.get_text(desc_key))
        self.badge_lbl.setText(lang_manager.get_text(badge_key))

    def update_theme(self):
        theme.update_globals()
        
        self.setStyleSheet(f"""
            QFrame#ComingSoonCard {{
                background-color: {theme.CARD_BG};
                border: 1px dashed {theme.BORDER};
                border-radius: 12px;
            }}
            QFrame#ComingSoonCard:hover {{
                border-color: {theme.CYAN};
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
                border-radius: 8px;
            }}
        """)

        self.badge_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {theme.CYAN}20;
                color: {theme.CYAN};
                border: 1px solid {theme.CYAN}40;
                border-radius: 12px;
            }}
        """)
