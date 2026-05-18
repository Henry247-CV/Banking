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

class SecurityPinDialog(BaseDialog):
    """Modern fintech popup for entering a 6-digit security PIN."""

    def __init__(self, parent=None, title_key="enter_security_pin", desc_key="pin_desc"):
        super().__init__(parent)
        self.lang_manager = LanguageManager()
        self.title_key = title_key
        self.desc_key = desc_key
        self.pin = ""
        self.setup_ui()
        self.update_theme()

    def setup_ui(self):
        self.setFixedSize(360, 240)

        self.container_layout.setContentsMargins(24, 24, 24, 24)
        self.container_layout.setSpacing(16)

        # Header
        self.title_lbl = QLabel(self.lang_manager.get_text(self.title_key))
        self.title_lbl.setFont(QFont(Typography.FAMILY, 14, Typography.WEIGHT_BOLD))
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.desc_lbl = QLabel(self.lang_manager.get_text(self.desc_key))
        self.desc_lbl.setFont(QFont(Typography.FAMILY, 10))
        self.desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_lbl.setWordWrap(True)

        self.container_layout.addWidget(self.title_lbl)
        self.container_layout.addWidget(self.desc_lbl)

        # PIN Input
        self.pin_input = QLineEdit()
        self.pin_input.setObjectName("SecurityPinInput")
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_input.setMaxLength(6)
        self.pin_input.setPlaceholderText("••••••")
        self.pin_input.setFixedHeight(48)
        self.pin_input.setFont(QFont(Typography.FAMILY, 18, Typography.WEIGHT_BOLD))
        self.pin_input.textChanged.connect(self._on_pin_changed)
        self.container_layout.addWidget(self.pin_input)

        # Error Label
        self.error_lbl = QLabel("")
        self.error_lbl.setObjectName("SecurityPinError")
        self.error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_lbl.setFixedHeight(20)
        self.container_layout.addWidget(self.error_lbl)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.cancel_btn = BaseButton(self.lang_manager.get_text("cancel"), variant="ghost")
        self.cancel_btn.clicked.connect(self.reject)

        self.confirm_btn = BaseButton(self.lang_manager.get_text("confirm"), variant="primary")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self.accept)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.confirm_btn)
        self.container_layout.addLayout(btn_layout)

    def _on_pin_changed(self, text):
        # Only allow digits
        if not text.isdigit() and text != "":
            self.pin_input.setText(text[:-1])
        
        self.pin = self.pin_input.text()
        self.confirm_btn.setEnabled(len(self.pin) == 6)
        self.error_lbl.setText("")

    def show_error(self, msg):
        self.error_lbl.setText(msg)
        self.pin_input.clear()

    def get_pin(self):
        return self.pin

    def update_theme(self):
        super().update_theme()
        theme.update_globals()
        
        self.title_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; background: transparent; border: none;")
        self.desc_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; background: transparent; border: none;")
        
        self.pin_input.setStyleSheet(f"""
            QLineEdit#SecurityPinInput {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 2px solid {theme.BORDER};
                border-radius: 8px;
                letter-spacing: 8px;
            }}
            QLineEdit#SecurityPinInput:focus {{
                border: 2px solid {theme.CYAN};
            }}
        """)
        
        self.error_lbl.setStyleSheet(f"color: {theme.RED}; font-size: 11px; background: transparent; border: none;")
        
        self.cancel_btn.update_theme()
        self.confirm_btn.update_theme()
