from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.admin.services.admin_user_service import AdminUserService
from src.core.utils import safe_text

class AdminEditUserDialog(QDialog):
    """Hộp thoại quản trị để chỉnh sửa thông tin người dùng."""
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setWindowTitle(f"Edit User: {user_data['username']}")
        self.setFixedSize(450, 500)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title_lbl = QLabel(f"👤 Edit User Profile: {self.user_data['username']}")
        title_lbl.setStyleSheet(f"color: {CYAN}; font-size: 18px; font-weight: 800;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        # Form Fields
        self.fields = {}
        field_data = [
            ("full_name", "Full Name", self.user_data.get('full_name', '')),
            ("phone", "Phone Number", self.user_data.get('phone', '')),
            ("email", "Email Address", self.user_data.get('email', '')),
            ("balance", "Balance (VND)", str(self.user_data.get('balance', 0))),
        ]

        for key, label, val in field_data:
            box = QVBoxLayout()
            box.setSpacing(8)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: 600;")
            
            edit = QLineEdit(safe_text(val))
            edit.setFixedHeight(40)
            
            box.addWidget(lbl)
            box.addWidget(edit)
            layout.addLayout(box)
            self.fields[key] = edit

        # Note for balance change
        balance_note = QLabel("⚠️ Note: Changing balance directly will be logged as an administrative adjustment.")
        balance_note.setStyleSheet(f"color: {ORANGE}; font-size: 11px; font-style: italic;")
        balance_note.setWordWrap(True)
        layout.addWidget(balance_note)

        layout.addStretch()

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(45)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setFixedHeight(45)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.handle_save)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def apply_styles(self):
        self.setStyleSheet(f"background-color: {BACKGROUND};")
        styles = get_styles()
        input_style = styles["LINE_EDIT_STYLE"]
        
        for edit in self.fields.values():
            edit.setStyleSheet(input_style)

        self.cancel_btn.setStyleSheet(styles["SECONDARY_BUTTON"])
        self.save_btn.setStyleSheet(styles["PRIMARY_BUTTON"])

    def handle_save(self):
        full_name = self.fields["full_name"].text().strip()
        phone = self.fields["phone"].text().strip()
        email = self.fields["email"].text().strip()
        balance_str = self.fields["balance"].text().strip()

        if not full_name or not phone:
            QMessageBox.warning(self, "Validation Error", "Full Name and Phone are required.")
            return

        try:
            balance = float(balance_str)
            if balance < 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Invalid balance amount.")
            return

        # Execute update via AdminUserService
        success, msg = AdminUserService.admin_update_user_profile(
            admin_username="admin",
            target_username=self.user_data['username'],
            full_name=full_name,
            phone=phone,
            email=email,
            balance=balance
        )

        if success:
            QMessageBox.information(self, "Success", "User profile updated successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)
