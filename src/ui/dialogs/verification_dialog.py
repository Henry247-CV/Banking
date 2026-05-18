from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.core.utils import safe_delete_temp_file

class VerificationDialog(QDialog):
    def __init__(self, expected_code, file_path=None, parent=None):
        super().__init__(parent)
        self.expected_code = expected_code
        self.file_path = file_path
        self.verified = False

        self.setWindowTitle("Đăng Khoa Bank - 2FA Verification")
        self.setFixedSize(420, 260)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main Container (Card Style)
        container = QFrame()
        container.setStyleSheet(CARD_STYLE)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(15)

        title = QLabel("Đăng Khoa Bank Verification")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {TEXT_PRIMARY};")

        subtitle = QLabel("Please check the TXT file opened on your Desktop.")
        subtitle.setStyleSheet(f"font-size: 13px; color: {CYAN}; font-weight: bold;")
        subtitle.setWordWrap(True)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("000000")
        self.code_input.setMaxLength(6)
        self.code_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.code_input.setStyleSheet(LINE_EDIT_STYLE + "font-size: 24px; letter-spacing: 5px;")

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {RED}; font-size: 12px;")
        self.error_label.hide()

        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(SECONDARY_BUTTON)
        cancel_btn.clicked.connect(self.reject)
        
        verify_btn = QPushButton("Verify")
        verify_btn.setStyleSheet(PRIMARY_BUTTON)
        verify_btn.clicked.connect(self.check_code)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(verify_btn)

        container_layout.addWidget(title)
        container_layout.addWidget(subtitle)
        container_layout.addWidget(self.code_input)
        container_layout.addWidget(self.error_label)
        container_layout.addStretch()
        container_layout.addLayout(btn_layout)

        layout.addWidget(container)

    def check_code(self):
        input_code = self.code_input.text().strip()
        if input_code == self.expected_code:
            self.verified = True
            # Delete the temporary file
            if self.file_path:
                safe_delete_temp_file(self.file_path)
                QMessageBox.information(self, "Verification Successful", "Verification successful.\nTemporary verification file removed.")
            self.accept()
        else:
            self.error_label.setText("Invalid verification code.")
            self.error_label.show()
            self.code_input.setStyleSheet(LINE_EDIT_STYLE + f"border: 1px solid {RED}; font-size: 24px; letter-spacing: 5px;")
