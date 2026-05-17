from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.core.utils import safe_currency, safe_text
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager

class ProfileCard(QFrame):
    def __init__(self, full_name, username, balance, account_number, tier="STANDARD"):
        super().__init__()
        self.tier = tier.upper()
        self.full_name = full_name
        self.username = username
        self.balance = balance
        self.account_number = account_number
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setup_ui()
        self.update_theme()
        self.update_translations()

    def update_theme(self):
        styles = get_styles()
        tier_color = "#D4AF37" if self.tier == "GOLD" else (theme.CYAN if self.tier == "DIAMOND" else theme.TEXT_SECONDARY)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {theme.CARD_BG}, stop: 1 {theme.PANEL_BG}
                );
                border-radius: 24px;
                border: 1px solid {theme.BORDER};
                border-left: 6px solid {tier_color};
            }}
        """)
        self.avatar_frame.setStyleSheet(f"background-color: {theme.BACKGROUND}; border: 3px solid {theme.BORDER}; border-radius: 50px;")
        self.avatar_label.setStyleSheet(f"color: {theme.CYAN}; font-size: 40px; font-weight: 800; background: transparent; border: none;")
        self.name_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 28px; font-weight: 800; border: none; background: transparent;")
        self.acc_label.setStyleSheet(f"color: {theme.CYAN}; font-size: 15px; font-weight: 700; border: none; background: transparent;")
        self.tier_chip.setStyleSheet(f"""
            background-color: {theme.PANEL_BG};
            color: {tier_color};
            border: 1px solid {tier_color};
            border-radius: 4px;
            font-size: 10px;
            font-weight: 900;
        """)
        self.user_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 13px; font-weight: 600; border: none; background: transparent;")
        self.bal_title.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 14px; font-weight: 600; border: none; background: transparent;")
        self.bal_amount.setStyleSheet(f"color: {theme.CYAN}; font-size: 32px; font-weight: 800; border: none; background: transparent;")

    def update_translations(self):
        self.bal_title.setText(self.lang_manager.get_text("available_balance"))
        # self.acc_label.setText(f"{self.lang_manager.get_text('acc_number')}: {safe_text(self.account_number)}")
        # For simplicity, keeping it clean

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Avatar Section
        self.avatar_frame = QFrame()
        self.avatar_frame.setFixedSize(100, 100)
        avatar_layout = QVBoxLayout(self.avatar_frame)
        avatar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        display_name = safe_text(self.full_name, "User")
        self.avatar_label = QLabel(display_name[0].upper())
        avatar_layout.addWidget(self.avatar_label)

        # Info Section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        self.name_label = QLabel(display_name)
        
        acc_row = QHBoxLayout()
        self.acc_label = QLabel(f"Account ID: {safe_text(self.account_number)}")
        
        self.tier_chip = QLabel(f" {self.tier} ")
        
        acc_row.addWidget(self.acc_label)
        acc_row.addSpacing(10)
        acc_row.addWidget(self.tier_chip)
        acc_row.addStretch()

        self.user_label = QLabel(f"@{safe_text(self.username)}")

        info_layout.addWidget(self.name_label)
        info_layout.addLayout(acc_row)
        info_layout.addWidget(self.user_label)
        info_layout.addStretch()

        # Balance Section
        balance_layout = QVBoxLayout()
        balance_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)

        self.bal_title = QLabel("Available Balance")
        self.bal_amount = QLabel(safe_currency(self.balance))

        balance_layout.addWidget(self.bal_title)
        balance_layout.addWidget(self.bal_amount)

        layout.addWidget(self.avatar_frame)
        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addLayout(balance_layout)
