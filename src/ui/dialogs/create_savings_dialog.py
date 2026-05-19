from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QDoubleSpinBox, QFrame
)
from PyQt6.QtCore import Qt
from src.core import theme
from src.core.language_manager import LanguageManager
from src.models.savings_model import SavingsType
from src.services.savings_service import SavingsService

class CreateSavingsDialog(QDialog):
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.lang_manager = LanguageManager()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(self.lang_manager.get_text("create_savings"))
        self.setFixedWidth(400)
        self.setStyleSheet(f"background-color: {theme.PANEL_BG};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel(self.lang_manager.get_text("create_new_plan"))
        title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Plan Name
        layout.addWidget(QLabel(self.lang_manager.get_text("plan_name"), styleSheet=f"color: {theme.TEXT_SECONDARY};"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. New Car, Emergency Fund")
        self.name_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.name_input)

        # Type
        layout.addWidget(QLabel(self.lang_manager.get_text("savings_type"), styleSheet=f"color: {theme.TEXT_SECONDARY};"))
        self.type_combo = QComboBox()
        self.type_combo.addItem(self.lang_manager.get_text("flexible_savings"), SavingsType.FLEXIBLE)
        self.type_combo.addItem(self.lang_manager.get_text("fixed_savings"), SavingsType.FIXED)
        self.type_combo.setStyleSheet(self.get_input_style())
        layout.addWidget(self.type_combo)

        # Target Amount
        layout.addWidget(QLabel(self.lang_manager.get_text("target_amount"), styleSheet=f"color: {theme.TEXT_SECONDARY};"))
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(1000000, 1000000000)
        self.amount_input.setSingleStep(1000000)
        self.amount_input.setValue(10000000)
        self.amount_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.amount_input)

        # Duration
        layout.addWidget(QLabel(self.lang_manager.get_text("duration"), styleSheet=f"color: {theme.TEXT_SECONDARY};"))
        self.duration_combo = QComboBox()
        for m in [3, 6, 12, 24, 36]:
            self.duration_combo.addItem(f"{m} Months", m)
        self.duration_combo.setStyleSheet(self.get_input_style())
        layout.addWidget(self.duration_combo)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton(self.lang_manager.get_text("cancel"))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; border: none; font-weight: bold;")
        
        confirm_btn = QPushButton(self.lang_manager.get_text("confirm"))
        confirm_btn.clicked.connect(self.handle_create)
        confirm_btn.setStyleSheet(f"""
            background-color: {theme.CYAN};
            color: white;
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: bold;
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(confirm_btn)
        layout.addLayout(btn_layout)

    def get_input_style(self):
        return f"""
            background-color: {theme.SIDEBAR_BG};
            color: {theme.TEXT_PRIMARY};
            border: 1px solid {theme.BORDER};
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
        """

    def handle_create(self):
        name = self.name_input.text()
        if not name: return
        
        plan_type = self.type_combo.currentData()
        target = self.amount_input.value()
        duration = self.duration_combo.currentData()
        
        success, msg = SavingsService.create_plan(self.username, name, plan_type, target, duration)
        if success:
            self.accept()
        else:
            # Show error (simplified)
            print(msg)
