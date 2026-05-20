from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QDialog, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.core.language_manager import LanguageManager

class CreateSavingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = LanguageManager()
        self.setWindowTitle(self.lang_manager.get_text("create_savings_plan"))
        self.setFixedSize(400, 500)
        self.setup_ui()
        self.update_theme()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        # Title
        self.title_label = QLabel(self.lang_manager.get_text("new_savings_plan"))
        self.layout.addWidget(self.title_label)

        # Plan Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(self.lang_manager.get_text("plan_name"))
        self.layout.addWidget(self.name_input)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["FLEXIBLE", "FIXED"])
        self.layout.addWidget(self.type_combo)

        # Target Amount
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText(self.lang_manager.get_text("target_amount_placeholder"))
        self.layout.addWidget(self.amount_input)

        # Duration
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["3 Months", "6 Months", "12 Months", "24 Months"])
        self.layout.addWidget(self.duration_combo)

        # Buttons
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton(self.lang_manager.get_text("cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        self.create_btn = QPushButton(self.lang_manager.get_text("create_plan"))
        self.create_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.create_btn)
        self.layout.addLayout(btn_layout)

    def update_theme(self):
        styles = get_styles()
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        self.title_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 20px; font-weight: 800;")
        
        input_style = f"""
            QLineEdit, QComboBox {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 8px;
                padding: 10px;
            }}
        """
        self.name_input.setStyleSheet(input_style)
        self.type_combo.setStyleSheet(combo_style if 'combo_style' in locals() else input_style)
        self.amount_input.setStyleSheet(input_style)
        self.duration_combo.setStyleSheet(input_style)
        
        self.cancel_btn.setStyleSheet(styles["SECONDARY_BUTTON"])
        self.create_btn.setStyleSheet(styles["PRIMARY_BUTTON"])

    def get_data(self):
        duration_map = {"3 Months": 3, "6 Months": 6, "12 Months": 12, "24 Months": 24}
        rate_map = {"FLEXIBLE": 0.03, "FIXED": 0.06}
        
        s_type = self.type_combo.currentText()
        return {
            "plan_name": self.name_input.text(),
            "savings_type": s_type,
            "target_amount": float(self.amount_input.text() or 0),
            "duration_months": duration_map.get(self.duration_combo.currentText(), 12),
            "interest_rate": rate_map.get(s_type, 0.05)
        }
