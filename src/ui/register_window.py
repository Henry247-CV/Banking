from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QFrame,
    QMessageBox,
    QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.theme import *
from src.core.styles import *
from src.services.auth_service import AuthService
from src.ui.dialogs.activation_dialog import ActivationDialog
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager

class RegisterWindow(QWidget):
    switch_to_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.auth_service = AuthService()
        
        self.setWindowTitle("Đăng Khoa Bank - Register")
        self.resize(1200, 720)
        self.setMinimumSize(1000, 650)
        
        self.setup_ui()
        self.update_theme()
        self.update_translations()

    def update_theme(self):
        styles = get_styles()
        self.setStyleSheet(styles["GLOBAL_STYLE"])
        self.branding_container.setStyleSheet(f"""
            QFrame#branding_section {{
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {theme.SIDEBAR_BG}, stop: 1 {theme.BACKGROUND}
                );
                border-right: 1px solid {theme.BORDER};
            }}
        """)
        self.logo_placeholder.setStyleSheet(f"background-color: {theme.CYAN}; border-radius: 40px;")
        self.branding_title.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {theme.TEXT_PRIMARY};")
        self.branding_subtitle.setStyleSheet(f"font-size: 20px; color: {theme.TEXT_SECONDARY};")
        self.branding_desc.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 14px;")
        
        self.card.setStyleSheet(styles["CARD_STYLE"])
        self.title_lbl.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {theme.TEXT_PRIMARY}; border: none; background: transparent;")
        self.subtitle_lbl.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_SECONDARY}; border: none; background: transparent;")
        
        self.full_name.setStyleSheet(styles["LINE_EDIT_STYLE"])
        self.username.setStyleSheet(styles["LINE_EDIT_STYLE"])
        self.email.setStyleSheet(styles["LINE_EDIT_STYLE"])
        self.phone.setStyleSheet(styles["LINE_EDIT_STYLE"])
        self.cccd.setStyleSheet(styles["LINE_EDIT_STYLE"])
        self.password.setStyleSheet(styles["LINE_EDIT_STYLE"])
        self.confirm_password.setStyleSheet(styles["LINE_EDIT_STYLE"])
        
        self.register_btn.setStyleSheet(styles["PRIMARY_BUTTON"])
        self.login_link.setStyleSheet(f"color: {theme.CYAN}; border: none; font-size: 13px; background: transparent;")

    def update_translations(self):
        self.branding_subtitle.setText(self.lang_manager.get_text("modern_platform"))
        self.title_lbl.setText(self.lang_manager.get_text("register"))
        self.full_name.setPlaceholderText(self.lang_manager.get_text("full_name"))
        self.username.setPlaceholderText(self.lang_manager.get_text("username"))
        self.email.setPlaceholderText(self.lang_manager.get_text("email"))
        self.phone.setPlaceholderText(self.lang_manager.get_text("phone"))
        self.cccd.setPlaceholderText(self.lang_manager.get_text("cccd"))
        self.password.setPlaceholderText(self.lang_manager.get_text("password"))
        self.confirm_password.setPlaceholderText(self.lang_manager.get_text("change_password")) # Reuse or add new
        self.register_btn.setText(self.lang_manager.get_text("register"))
        self.login_link.setText("Already have an account? Login") # Add to trans if needed

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Branding
        self.branding_container = QFrame()
        self.branding_container.setObjectName("branding_section")
        branding_layout = QVBoxLayout(self.branding_container)
        branding_layout.setContentsMargins(60, 60, 60, 60)
        branding_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignCenter)

        self.logo_placeholder = QFrame()
        self.logo_placeholder.setFixedSize(80, 80)
        self.branding_title = QLabel("Đăng Khoa Bank")
        self.branding_subtitle = QLabel("")
        self.branding_subtitle.setWordWrap(True)
        self.branding_desc = QLabel("Secure • Fast • Modern")

        branding_layout.addWidget(self.logo_placeholder)
        branding_layout.addSpacing(40)
        branding_layout.addWidget(self.branding_title)
        branding_layout.addWidget(self.branding_subtitle)
        branding_layout.addSpacing(20)
        branding_layout.addWidget(self.branding_desc)
        branding_layout.addStretch()

        # 2. Register
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.card = QFrame()
        self.card.setFixedWidth(480)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(12)

        self.title_lbl = QLabel("")
        self.subtitle_lbl = QLabel("Activation code TXT file will be generated.")
        
        self.full_name = QLineEdit()
        self.username = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.cccd = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {RED}; font-size: 12px; border: none; background: transparent;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        self.register_btn = QPushButton("")
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_btn.clicked.connect(self.handle_registration_attempt)

        self.login_link = QPushButton("")
        self.login_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_link.clicked.connect(self.switch_to_login.emit)

        card_layout.addWidget(self.title_lbl)
        card_layout.addWidget(self.subtitle_lbl)
        card_layout.addSpacing(5)
        card_layout.addWidget(self.full_name)
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.email)
        card_layout.addWidget(self.phone)
        card_layout.addWidget(self.cccd)
        card_layout.addWidget(self.password)
        card_layout.addWidget(self.confirm_password)
        card_layout.addWidget(self.error_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.register_btn)
        card_layout.addWidget(self.login_link)

        container_layout.addWidget(self.card)
        self.scroll.setWidget(container)
        self.main_layout.addWidget(self.branding_container, 55)
        self.main_layout.addWidget(self.scroll, 45)

    def handle_registration_attempt(self):
        full_name = self.full_name.text().strip()
        username = self.username.text().strip()
        email = self.email.text().strip()
        phone = self.phone.text().strip()
        cccd = self.cccd.text().strip()
        password = self.password.text().strip()
        confirm_password = self.confirm_password.text().strip()

        # Validation
        if not all([full_name, username, phone, cccd, password, confirm_password]):
            self.show_error(self.lang_manager.get_text("required_fields"))
            return

        if not phone.isdigit():
            self.show_error("Phone number must be numeric.")
            return

        if not cccd.isdigit():
            self.show_error("CCCD must be numeric.")
            return

        if len(password) < 6:
            self.show_error("Password must be at least 6 characters.")
            return

        if password != confirm_password:
            self.show_error("Passwords do not match.")
            return

        if self.auth_service.is_username_taken(username):
            self.show_error("Username is already taken.")
            return

        if self.auth_service.is_cccd_taken(cccd):
            self.show_error("CCCD is already registered.")
            return

        # Generate activation code and TXT
        code, file_path = self.auth_service.generate_activation_code()
        
        # Show activation dialog
        dialog = ActivationDialog(code, file_path, self)
        if dialog.exec():
            # If code verified, perform database insertion
            if self.auth_service.register_user(username, password, full_name, phone, cccd, email):
                QMessageBox.information(
                    self, 
                    "Đăng Khoa Bank", 
                    "Account activated and created successfully!\nWelcome to Đăng Khoa Bank."
                )
                self.switch_to_login.emit()
            else:
                self.show_error("An error occurred during account creation.")
        else:
            # User cancelled activation
            pass

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
