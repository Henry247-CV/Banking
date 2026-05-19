from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.services.saving_service import SavingService

class CreateSavingDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("Create New Saving Goal")
        self.setFixedSize(400, 350)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title_lbl = QLabel("🎯 New Saving Goal")
        title_lbl.setStyleSheet(f"color: {CYAN}; font-size: 20px; font-weight: 800;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        # Goal Name
        name_box = QVBoxLayout()
        name_box.setSpacing(8)
        name_lbl = QLabel("What are you saving for?")
        name_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: 600;")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., New Car, Vacation, Emergency Fund")
        self.name_input.setFixedHeight(45)
        name_box.addWidget(name_lbl)
        name_box.addWidget(self.name_input)
        layout.addLayout(name_box)

        # Target Amount
        amount_box = QVBoxLayout()
        amount_box.setSpacing(8)
        amount_lbl = QLabel("Target Amount (VND)")
        amount_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: 600;")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        self.amount_input.setFixedHeight(45)
        amount_box.addWidget(amount_lbl)
        amount_box.addWidget(self.amount_input)
        layout.addLayout(amount_box)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(45)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)

        self.create_btn = QPushButton("Create Goal")
        self.create_btn.setFixedHeight(45)
        self.create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.create_btn.clicked.connect(self.handle_create)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.create_btn)
        layout.addLayout(btn_layout)

    def apply_styles(self):
        self.setStyleSheet(f"background-color: {BACKGROUND};")
        
        input_style = f"""
            QLineEdit {{
                background-color: {PANEL_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {CYAN};
            }}
        """
        self.name_input.setStyleSheet(input_style)
        self.amount_input.setStyleSheet(input_style)

        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PANEL_BG};
                color: {TEXT_PRIMARY};
            }}
        """)

        self.create_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CYAN};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {CYAN}CC;
            }}
        """)

    def handle_create(self):
        name = self.name_input.text().strip()
        amount_str = self.amount_input.text().strip()

        if not name or not amount_str:
            QMessageBox.warning(self, "Validation Error", "Please fill in all fields.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid target amount.")
            return

        success = SavingService.create_saving_goal(self.username, name, amount)
        if success:
            QMessageBox.information(self, "Success", f"Saving goal '{name}' created successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to create saving goal. Please try again.")
