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
from src.core.utils import safe_text

class VirtualBankCard(QFrame):
    def __init__(self, full_name, account_number, tier="STANDARD"):
        super().__init__()
        # Compact Card Design
        self.setFixedSize(340, 190)
        self.tier = tier.upper()
        self.setup_ui(full_name, account_number)

    def setup_ui(self, full_name, account_number):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(0)

        # 1. Background Gradient & Glow based on tier
        if self.tier == "DIAMOND":
            bg_style = """
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #080808, stop: 0.5 #1A0B2E, stop: 1 #0F0F0F
                );
                border: 2px solid #00F2FF;
            """
            accent_color = "#00F2FF"
            text_color = "#FFFFFF"
        elif self.tier == "GOLD":
            bg_style = """
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #D4AF37, stop: 0.5 #FFD700, stop: 1 #B8860B
                );
                border: 1px solid #FFD700;
            """
            accent_color = "#FFFFFF"
            text_color = "#FFFFFF"
        else: # STANDARD
            bg_style = """
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #0F172A, stop: 1 #1E293B
                );
                border: 1px solid #334155;
            """
            accent_color = "#00F2FF"
            text_color = "#FFFFFF"

        self.setStyleSheet(f"""
            QFrame {{
                {bg_style}
                border-radius: 20px;
                color: {text_color};
            }}
        """)

        # 2. Card Header (Bank Logo)
        header = QHBoxLayout()
        brand_layout = QVBoxLayout()
        brand = QLabel("ĐĂNG KHOA BANK")
        brand.setStyleSheet(f"color: {text_color}; font-size: 14px; font-weight: 900; background: transparent; letter-spacing: 1.5px;")
        brand_sub = QLabel("DIGITAL BANKING")
        brand_sub.setStyleSheet(f"color: {accent_color if self.tier != 'GOLD' else 'rgba(255,255,255,0.7)'}; font-size: 7px; font-weight: 800; background: transparent; letter-spacing: 2px;")
        brand_layout.addWidget(brand)
        brand_layout.addWidget(brand_sub)
        
        chip = QFrame()
        chip.setFixedSize(42, 32)
        chip_color = "rgba(255, 255, 255, 0.2)" if self.tier != "GOLD" else "rgba(255, 255, 255, 0.4)"
        chip.setStyleSheet(f"background-color: {chip_color}; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);")
        
        header.addLayout(brand_layout)
        header.addStretch()
        header.addWidget(chip)

        # 3. Card Number (Masked)
        last_digits = account_number[-4:] if account_number else "0000"
        card_num = QLabel(f"****  ****  ****  {last_digits}")
        card_num.setStyleSheet(f"color: {text_color}; font-size: 20px; font-weight: 700; background: transparent; letter-spacing: 3px; margin-top: 15px;")

        # 4. Footer (Name and Tier)
        footer = QHBoxLayout()
        
        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        
        name_label = QLabel(safe_text(full_name).upper())
        name_label.setStyleSheet(f"color: {text_color}; font-size: 14px; font-weight: 800; background: transparent; letter-spacing: 0.5px;")
        
        acc_label = QLabel(account_number)
        acc_label.setStyleSheet(f"color: rgba(255,255,255,0.6); font-size: 10px; font-weight: 600; background: transparent;")

        info_col.addWidget(name_label)
        info_col.addWidget(acc_label)
        
        tier_badge = QLabel(f" {self.tier} MEMBER ")
        tier_badge_bg = "rgba(0, 242, 255, 0.15)" if self.tier != "GOLD" else "rgba(255, 255, 255, 0.2)"
        tier_badge.setStyleSheet(f"""
            background-color: {tier_badge_bg};
            color: {accent_color};
            border: 1px solid {accent_color};
            border-radius: 4px;
            font-size: 9px;
            font-weight: 900;
            padding: 3px 6px;
        """)

        footer.addLayout(info_col)
        footer.addStretch()
        footer.addWidget(tier_badge, alignment=Qt.AlignmentFlag.AlignBottom)

        layout.addLayout(header)
        layout.addStretch()
        layout.addWidget(card_num)
        layout.addStretch()
        layout.addLayout(footer)
