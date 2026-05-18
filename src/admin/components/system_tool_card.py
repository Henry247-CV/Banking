from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import src.core.theme as theme

class SystemToolCard(QFrame):
    """Card for executing a specific system utility action."""
    action_requested = pyqtSignal()

    def __init__(self, title, description, icon_str, btn_text, is_danger=False):
        super().__init__()
        self.setObjectName("SystemToolCard")
        self.title_text = title
        self.desc_text = description
        self.icon_str = icon_str
        self.btn_text = btn_text
        self.is_danger = is_danger
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        # Icon
        self.icon_lbl = QLabel(self.icon_str)
        self.icon_lbl.setObjectName("SystemToolIcon")
        self.icon_lbl.setFixedSize(36, 36)
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setFont(QFont("Segoe UI Emoji", 16))
        layout.addWidget(self.icon_lbl)

        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.title_lbl = QLabel(self.title_text)
        self.title_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        info_layout.addWidget(self.title_lbl)

        self.desc_lbl = QLabel(self.desc_text)
        self.desc_lbl.setFont(QFont("Segoe UI", 9))
        self.desc_lbl.setWordWrap(True)
        info_layout.addWidget(self.desc_lbl)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Action Button
        self.action_btn = QPushButton(self.btn_text)
        self.action_btn.setObjectName("SystemToolBtn")
        self.action_btn.setFixedSize(120, 32)
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_btn.clicked.connect(self.action_requested.emit)
        layout.addWidget(self.action_btn)

    def update_translations(self, lang_manager, title_key, desc_key, btn_key):
        self.title_lbl.setText(lang_manager.get_text(title_key))
        self.desc_lbl.setText(lang_manager.get_text(desc_key))
        self.action_btn.setText(lang_manager.get_text(btn_key))

    def update_theme(self):
        theme.update_globals()
        
        accent = theme.RED if self.is_danger else theme.CYAN
        
        self.setStyleSheet(f"""
            QFrame#SystemToolCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 8px;
            }}
            QFrame#SystemToolCard:hover {{
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
                border-radius: 6px;
            }}
        """)

        if self.is_danger:
            self.action_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme.RED};
                    border: 1px solid {theme.RED};
                    border-radius: 6px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {theme.RED};
                    color: white;
                }}
            """)
        else:
            self.action_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.PANEL_BG};
                    color: {theme.TEXT_PRIMARY};
                    border: 1px solid {theme.BORDER};
                    border-radius: 6px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border-color: {theme.CYAN};
                    color: {theme.CYAN};
                }}
            """)
