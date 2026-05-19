from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.services.auth_service import AuthService

class ChangePasswordDialog(QDialog):
    def __init__(self, user_id, username, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.setWindowTitle("Change Password")
        self.setFixedSize(400, 350)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title_lbl = QLabel("🔐 Change Password")
        title_lbl.setStyleSheet(f"color: {CYAN}; font-size: 20px; font-weight: 800;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        # Current Password
        curr_box = QVBoxLayout()
        curr_box.setSpacing(8)
        curr_lbl = QLabel("Current Password")
        curr_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: 600;")
        self.curr_input = QLineEdit()
        self.curr_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.curr_input.setFixedHeight(45)
        curr_box.addWidget(curr_lbl)
        curr_box.addWidget(self.curr_input)
        layout.addLayout(curr_box)

        # New Password
        new_box = QVBoxLayout()
        new_box.setSpacing(8)
        new_lbl = QLabel("New Password")
        new_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: 600;")
        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_input.setFixedHeight(45)
        new_box.addWidget(new_lbl)
        new_box.addWidget(self.new_input)
        layout.addLayout(new_box)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(45)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Update Password")
        self.save_btn.setFixedHeight(45)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.handle_update)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def apply_styles(self):
        self.setStyleSheet(f"background-color: {BACKGROUND};")
        styles = get_styles()
        input_style = styles["LINE_EDIT_STYLE"]
        self.curr_input.setStyleSheet(input_style)
        self.new_input.setStyleSheet(input_style)
        self.cancel_btn.setStyleSheet(styles["SECONDARY_BUTTON"])
        self.save_btn.setStyleSheet(styles["PRIMARY_BUTTON"])

    def handle_update(self):
        curr_pass = self.curr_input.text()
        new_pass = self.new_input.text()

        if not curr_pass or not new_pass:
            QMessageBox.warning(self, "Validation Error", "All fields are required.")
            return

        # Simple local verify for demo (in real app, we'd check against DB here)
        # But AuthService.login_user already checks password.
        user = AuthService.login_user(self.username, curr_pass)
        if not user or "error" in user:
            QMessageBox.critical(self, "Security Error", "Current password is incorrect.")
            return

        success = AuthService.update_password(self.user_id, self.username, new_pass)
        if success:
            QMessageBox.information(self, "Success", "Password updated successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update password. Ensure it meets security requirements.")
