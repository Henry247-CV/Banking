from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.core.language_manager import LanguageManager

class OverviewCard(QFrame):
    def __init__(self, title, amount, trend_text="", color=CYAN, icon="💰"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER};
                border-radius: 20px;
            }}
            QFrame:hover {{
                border: 1px solid {CYAN};
                background-color: {PANEL_BG};
            }}
        """)
        self.setup_ui(title, amount, trend_text, color, icon)

    def setup_ui(self, title, amount, trend_text, color, icon):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 20px; background: transparent; border: none;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: bold; border: none; background: transparent;")
        
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()

        amount_label = QLabel(amount)
        amount_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 24px; font-weight: 800; border: none; background: transparent;")

        layout.addLayout(header)
        layout.addWidget(amount_label)

        if trend_text:
            trend_label = QLabel(trend_text)
            trend_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold; border: none; background: transparent;")
            layout.addWidget(trend_label)

class TierOverviewCard(QFrame):
    def __init__(self, tier="STANDARD"):
        super().__init__()
        self.tier = tier.upper()
        tier_color = "#D4AF37" if self.tier == "GOLD" else (CYAN if self.tier == "DIAMOND" else TEXT_SECONDARY)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER};
                border-radius: 20px;
            }}
            QFrame:hover {{
                border: 1px solid {tier_color};
                background-color: {PANEL_BG};
            }}
        """)
        self.setup_ui(tier_color)

    def setup_ui(self, tier_color):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        header = QHBoxLayout()
        icon_lbl = QLabel("🏆")
        icon_lbl.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        title = QLabel("Current Tier")
        title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: bold; border: none; background: transparent;")
        header.addWidget(icon_lbl)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        tier_lbl = QLabel(f"{self.tier} MEMBER")
        tier_lbl.setStyleSheet(f"color: {tier_color}; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        layout.addWidget(tier_lbl)

        benefits_preview = QVBoxLayout()
        benefits_preview.setSpacing(2)
        
        if self.tier == "DIAMOND":
            b_list = ["● Priority Elite Support", "● Unlimited Limits"]
        elif self.tier == "GOLD":
            b_list = ["● Priority Support", "● High Transfer Limits"]
        else:
            b_list = ["● 24/7 Digital Support", "● Standard Limits"]

        for b in b_list:
            bl = QLabel(b)
            bl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 10px; font-weight: 600; border: none; background: transparent;")
            benefits_preview.addWidget(bl)
        
        layout.addLayout(benefits_preview)

class QuickActionButton(QPushButton):
    def __init__(self, key, icon=""):
        self.key = key
        self.icon = icon
        self.lang_manager = LanguageManager()
        super().__init__(f"{icon}  {self.lang_manager.get_text(key)}")
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {PANEL_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {CARD_BG};
                border: 1px solid {CYAN};
                color: {CYAN};
            }}
        """)
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def update_translation(self):
        self.setText(f"{self.icon}  {self.lang_manager.get_text(self.key)}")
