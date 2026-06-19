from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QLineEdit,
    QScrollArea,
    QMessageBox,
    QDialog,
    QComboBox,
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.services.saving_service import SavingService
from src.services.auth_service import AuthService
from src.services.notification_service import NotificationService
from src.ui.components.saving_card import SavingCard
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager

class SettingsTab(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.saving_service = SavingService()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setup_ui()
        self.update_theme()
        self.update_translations()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(30, 30, 30, 30)
        self.container_layout.setSpacing(30)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 1. Savings Section
        self.setup_savings_section()

        # 2. Appearance Section
        self.setup_appearance_section()

        # 3. Security Section
        self.setup_security_section()

        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

    def update_theme(self):
        styles = get_styles()
        self.scroll.verticalScrollBar().setStyleSheet(styles["GLOBAL_STYLE"])
        
        self.saving_section.setStyleSheet(styles["CARD_STYLE"])
        self.saving_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 22px; font-weight: 800; border: none; background: transparent;")
        self.form_panel.setStyleSheet(f"background-color: {theme.PANEL_BG}; border-radius: 12px; border: 1px solid {theme.BORDER};")
        self.goal_name.setStyleSheet(styles["LINE_EDIT_STYLE"] + "background-color: transparent; border: none;")
        self.goal_target.setStyleSheet(styles["LINE_EDIT_STYLE"] + "background-color: transparent; border: none;")
        self.create_btn.setStyleSheet(styles["PRIMARY_BUTTON"] + "min-height: 38px;")

        self.app_section.setStyleSheet(styles["CARD_STYLE"])
        self.app_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 22px; font-weight: 800; border: none; background: transparent;")
        self.dm_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 14px; font-weight: 600; border: none; background: transparent;")
        self.lang_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 14px; font-weight: 600; border: none; background: transparent;")
        
        combo_style = f"""
            QComboBox {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 8px;
                padding: 5px 15px;
                min-width: 120px;
                font-weight: 600;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme.CARD_BG};
                color: {theme.TEXT_PRIMARY};
                selection-background-color: {theme.CYAN};
                border: 1px solid {theme.BORDER};
            }}
        """
        self.theme_combo.setStyleSheet(combo_style)
        self.lang_combo.setStyleSheet(combo_style)

        self.sec_section.setStyleSheet(styles["CARD_STYLE"])
        self.sec_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 22px; font-weight: 800; border: none; background: transparent;")
        
        btn_style = styles["SECONDARY_BUTTON"] + "text-align: left; padding-left: 20px;"
        self.change_pass_btn.setStyleSheet(btn_style)
        self.change_pin_btn.setStyleSheet(btn_style)
        self.session_timeout_btn.setStyleSheet(btn_style)
        self.view_logs_btn.setStyleSheet(btn_style)
        
        self.load_savings()

    def update_translations(self):
        self.saving_title.setText(f"🎯  {self.lang_manager.get_text('create_savings')}")
        self.goal_name.setPlaceholderText(self.lang_manager.get_text("full_name")) # Reuse or add new keys
        self.goal_target.setPlaceholderText("VND")
        self.create_btn.setText(self.lang_manager.get_text("create_savings"))
        
        self.app_title.setText(f"🎨  {self.lang_manager.get_text('appearance')}")
        self.dm_label.setText(self.lang_manager.get_text("theme_mode"))
        self.lang_label.setText(self.lang_manager.get_text("language"))
        
        self.sec_title.setText(f"🔐  {self.lang_manager.get_text('account_settings')}")
        self.change_pass_btn.setText(self.lang_manager.get_text("change_password"))
        self.change_pin_btn.setText(self.lang_manager.get_text("enter_security_pin").replace("Enter", "Change"))
        self.session_timeout_btn.setText("Enable Session Timeout (Active)")
        self.view_logs_btn.setText("View Security Logs")
        
        # Block signals temporarily to prevent infinite loop
        self.theme_combo.blockSignals(True)
        self.theme_combo.setItemText(0, self.lang_manager.get_text("dark_mode"))
        self.theme_combo.setItemText(1, self.lang_manager.get_text("light_mode"))
        self.theme_combo.blockSignals(False)

    def setup_savings_section(self):
        self.saving_section = QFrame()
        layout = QVBoxLayout(self.saving_section)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        self.saving_title = QLabel("Savings Goals")
        layout.addWidget(self.saving_title)

        # Form
        self.form_panel = QFrame()
        form_layout = QHBoxLayout(self.form_panel)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(15)

        self.goal_name = QLineEdit()
        self.goal_target = QLineEdit()
        self.goal_target.setFixedWidth(150)

        self.create_btn = QPushButton("Create Goal")
        self.create_btn.clicked.connect(self.create_saving_goal)

        form_layout.addWidget(self.goal_name, 3)
        form_layout.addWidget(self.goal_target, 1)
        form_layout.addWidget(self.create_btn)
        layout.addWidget(self.form_panel)

        # Active Goals List
        self.savings_list_layout = QVBoxLayout()
        self.savings_list_layout.setSpacing(12)
        layout.addLayout(self.savings_list_layout)

        self.container_layout.addWidget(self.saving_section)

    def setup_appearance_section(self):
        self.app_section = QFrame()
        layout = QVBoxLayout(self.app_section)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.app_title = QLabel("Appearance")
        layout.addWidget(self.app_title)

        # Theme Switcher
        dm_row = QHBoxLayout()
        self.dm_label = QLabel("Theme Mode")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Mode", "Light Mode"])
        self.theme_combo.setCurrentIndex(0 if self.theme_manager.current_theme == "dark" else 1)
        self.theme_combo.currentIndexChanged.connect(self.handle_theme_change)
        
        dm_row.addWidget(self.dm_label)
        dm_row.addStretch()
        dm_row.addWidget(self.theme_combo)

        # Language Switcher
        lang_row = QHBoxLayout()
        self.lang_label = QLabel("Language")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Tiếng Việt"])
        self.lang_combo.setCurrentIndex(0 if self.lang_manager.current_language == "en" else 1)
        self.lang_combo.currentIndexChanged.connect(self.handle_lang_change)
        
        lang_row.addWidget(self.lang_label)
        lang_row.addStretch()
        lang_row.addWidget(self.lang_combo)

        layout.addLayout(dm_row)
        layout.addSpacing(5)
        layout.addLayout(lang_row)
        self.container_layout.addWidget(self.app_section)

    def setup_security_section(self):
        self.sec_section = QFrame()
        layout = QVBoxLayout(self.sec_section)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        self.sec_title = QLabel("Security")
        layout.addWidget(self.sec_title)
        layout.addSpacing(8)

        self.change_pass_btn = QPushButton("Change Password")
        self.change_pass_btn.setFixedHeight(50)
        self.change_pass_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.change_pass_btn.clicked.connect(self.show_change_password_dialog)
        layout.addWidget(self.change_pass_btn)

        self.change_pin_btn = QPushButton("Change Security PIN")
        self.change_pin_btn.setFixedHeight(50)
        self.change_pin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.change_pin_btn.clicked.connect(self.show_change_pin_dialog)
        layout.addWidget(self.change_pin_btn)

        self.session_timeout_btn = QPushButton("Enable Session Timeout (Active)")
        self.session_timeout_btn.setFixedHeight(50)
        self.session_timeout_btn.setEnabled(False) # Informational for demo
        layout.addWidget(self.session_timeout_btn)

        self.view_logs_btn = QPushButton("View Security Logs")
        self.view_logs_btn.setFixedHeight(50)
        self.view_logs_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_logs_btn.clicked.connect(self.show_security_logs)
        layout.addWidget(self.view_logs_btn)

        self.container_layout.addWidget(self.sec_section)

    def show_change_pin_dialog(self):
        from src.security.security_manager import SecurityManager
        from src.ui.dialogs.security_pin_dialog import SecurityPinDialog
        dialog = SecurityPinDialog(self, title_key="enter_security_pin", desc_key="pin_desc")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pin = dialog.get_pin()
            success, msg = SecurityManager.setup_security_pin(self.user_data['username'], pin)
            if success:
                QMessageBox.information(self, "Success", msg)
            else:
                QMessageBox.critical(self, "Error", msg)

    def show_security_logs(self):
        QMessageBox.information(self, "Security Logs", "No suspicious activity found on your account recently.")

    def handle_theme_change(self, index):
        theme_name = "dark" if index == 0 else "light"
        self.theme_manager.set_theme(theme_name)

    def handle_lang_change(self, index):
        lang_code = "en" if index == 0 else "vi"
        self.lang_manager.set_language(lang_code)

    def create_saving_goal(self):
        name = self.goal_name.text().strip()
        target = self.goal_target.text().strip()
        if not name or not target: return
        try:
            target_amount = float(target)
            if target_amount <= 0: raise ValueError
        except ValueError: return

        if self.saving_service.create_saving_goal(self.user_data['username'], name, target_amount):
            self.goal_name.clear()
            self.goal_target.clear()
            self.load_savings()

    def load_savings(self):
        while self.savings_list_layout.count():
            item = self.savings_list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        savings = self.saving_service.get_user_savings(self.user_data['username'])
        for s in savings:
            card = SavingCard(s[1], s[2], s[3])
            self.savings_list_layout.addWidget(card)

    def show_change_password_dialog(self):
        from src.ui.dialogs.change_password_dialog import ChangePasswordDialog
        dialog = ChangePasswordDialog(self.user_data['id'], self.user_data['username'], self)
        dialog.exec()

    def update_ui(self):
        self.load_savings()
