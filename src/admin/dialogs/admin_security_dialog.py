from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.core.language_manager import LanguageManager
import src.core.theme as theme
from src.design.component_factory import BaseDialog, BaseButton
from src.design.design_tokens import Typography

class AdminSecurityDialog(BaseDialog):
    """Admin confirmation dialog requiring admin password for sensitive actions."""

    def __init__(self, parent=None, action_desc="perform a sensitive action"):
        super().__init__(parent)
        self.lang_manager = LanguageManager()
        self.action_desc = action_desc
        self.password = ""
        self.setup_ui()
        self.update_theme()

    def setup_ui(self):
        self.setFixedSize(380, 240)

        self.container_layout.setContentsMargins(24, 24, 24, 24)
        self.container_layout.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        icon_lbl = QLabel("🛡️")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 16))
        
        self.title_lbl = QLabel("Admin Security Lock")
        self.title_lbl.setFont(QFont(Typography.FAMILY, 12, Typography.WEIGHT_BOLD))
        header_row.addWidget(icon_lbl)
        header_row.addWidget(self.title_lbl)
        header_row.addStretch()
        self.container_layout.addLayout(header_row)
        
        self.desc_lbl = QLabel(f"Please enter your admin password to {self.action_desc}.")
        self.desc_lbl.setFont(QFont(Typography.FAMILY, 10))
        self.desc_lbl.setWordWrap(True)
        self.container_layout.addWidget(self.desc_lbl)

        # Password Input
        self.pwd_input = QLineEdit()
        self.pwd_input.setObjectName("AdminSecurityInput")
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Admin Password")
        self.pwd_input.setFixedHeight(40)
        self.pwd_input.textChanged.connect(self._on_pwd_changed)
        self.container_layout.addWidget(self.pwd_input)

        # Error Label
        self.error_lbl = QLabel("")
        self.error_lbl.setObjectName("AdminSecurityError")
        self.error_lbl.setFixedHeight(18)
        self.container_layout.addWidget(self.error_lbl)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.cancel_btn = BaseButton("Cancel", variant="ghost")
        self.cancel_btn.clicked.connect(self.reject)

        self.confirm_btn = BaseButton("Authorize Action", variant="danger")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self.accept)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.confirm_btn)
        self.container_layout.addLayout(btn_layout)

    def _on_pwd_changed(self, text):
        self.password = text
        self.confirm_btn.setEnabled(len(self.password) > 0)
        self.error_lbl.setText("")

    def show_error(self, msg):
        self.error_lbl.setText(msg)
        self.pwd_input.clear()

    def get_password(self):
        return self.password

    def update_theme(self):
        super().update_theme()
        theme.update_globals()
        
        self.container.setStyleSheet(self.container.styleSheet() + f"""
            QFrame#BaseDialogContainer {{
                border-top: 4px solid {theme.RED};
            }}
        """)
        
        self.title_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; background: transparent; border: none;")
        self.desc_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; background: transparent; border: none;")
        
        self.pwd_input.setStyleSheet(f"""
            QLineEdit#AdminSecurityInput {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                padding: 0 12px;
            }}
            QLineEdit#AdminSecurityInput:focus {{
                border: 1px solid {theme.CYAN};
            }}
        """)
        
        self.error_lbl.setStyleSheet(f"color: {theme.RED}; font-size: 11px; background: transparent; border: none;")
        
        self.cancel_btn.update_theme()
        self.confirm_btn.update_theme()
