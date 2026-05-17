from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QFrame,
    QCheckBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.theme import *
from src.core.styles import *
from src.services.auth_service import AuthService
from src.ui.dialogs.verification_dialog import VerificationDialog
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager

class LoginWindow(QWidget):
    switch_to_register = pyqtSignal()
    login_success = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.auth_service = AuthService()
        
        self.setWindowTitle("Đăng Khoa Bank - Login")
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
        
        self.card.setStyleSheet(styles["CARD_STYLE"])
        self.title_lbl.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {theme.TEXT_PRIMARY}; border: none; background: transparent;")
        self.subtitle_lbl.setStyleSheet(f"font-size: 13px; color: {theme.TEXT_SECONDARY}; border: none; background: transparent;")
        
        self.username.setStyleSheet(styles["LINE_EDIT_STYLE"])
        self.password.setStyleSheet(styles["LINE_EDIT_STYLE"])
        self.remember_me.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 13px; border: none; background: transparent;")
        self.forgot_btn.setStyleSheet(f"color: {theme.CYAN}; border: none; font-size: 13px; text-align: right; background: transparent;")
        self.login_btn.setStyleSheet(styles["PRIMARY_BUTTON"])
        self.register_btn.setStyleSheet(styles["SECONDARY_BUTTON"])

    def update_translations(self):
        self.branding_subtitle.setText(self.lang_manager.get_text("modern_platform"))
        self.title_lbl.setText(self.lang_manager.get_text("login"))
        self.subtitle_lbl.setText(self.lang_manager.get_text("access_premium"))
        self.username.setPlaceholderText(self.lang_manager.get_text("username"))
        self.password.setPlaceholderText(self.lang_manager.get_text("password"))
        self.remember_me.setText(self.lang_manager.get_text("remember_me"))
        self.forgot_btn.setText(self.lang_manager.get_text("forgot_password"))
        self.login_btn.setText(self.lang_manager.get_text("login"))
        self.register_btn.setText(self.lang_manager.get_text("create_account"))

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

        branding_layout.addWidget(self.logo_placeholder)
        branding_layout.addSpacing(40)
        branding_layout.addWidget(self.branding_title)
        branding_layout.addWidget(self.branding_subtitle)
        branding_layout.addStretch()

        # 2. Login
        self.login_section = QWidget()
        login_layout = QVBoxLayout(self.login_section)
        login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setFixedWidth(420)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        self.title_lbl = QLabel("")
        self.subtitle_lbl = QLabel("")
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {RED}; font-size: 12px; border: none; background: transparent;")
        self.error_label.hide()

        extra_layout = QHBoxLayout()
        self.remember_me = QCheckBox("")
        self.forgot_btn = QPushButton("")
        self.forgot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        extra_layout.addWidget(self.remember_me)
        extra_layout.addStretch()
        extra_layout.addWidget(self.forgot_btn)

        self.login_btn = QPushButton("")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)

        self.register_btn = QPushButton("")
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_btn.clicked.connect(self.switch_to_register.emit)

        card_layout.addWidget(self.title_lbl)
        card_layout.addWidget(self.subtitle_lbl)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.password)
        card_layout.addWidget(self.error_label)
        card_layout.addLayout(extra_layout)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_btn)
        card_layout.addWidget(self.register_btn)

        login_layout.addWidget(self.card)
        self.main_layout.addWidget(self.branding_container, 55)
        self.main_layout.addWidget(self.login_section, 45)

    def handle_login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        if not username or not password:
            self.show_error(self.lang_manager.get_text("required_fields"))
            return
        user_data = self.auth_service.login_user(username, password)
        if user_data:
            self.error_label.hide()
            code = self.auth_service.generate_verification_code()
            dialog = VerificationDialog(code, self)
            if dialog.exec():
                QMessageBox.information(self, "Đăng Khoa Bank", self.lang_manager.get_text("login_successful"))
                self.login_success.emit(user_data)
        else:
            self.show_error(self.lang_manager.get_text("invalid_credentials"))

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
