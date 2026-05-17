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

class WalletCard(QFrame):
    def __init__(self, balance, wallet_id):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {CYAN}, stop: 1 #1AA8D9
                );
                border-radius: 24px;
                color: {TEXT_PRIMARY};
            }}
        """)
        self.setFixedSize(420, 240)
        self.setup_ui(balance, wallet_id)

    def setup_ui(self, balance, wallet_id):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(10)

        header = QHBoxLayout()
        brand = QLabel("Đăng Khoa Bank")
        brand.setStyleSheet("font-size: 18px; font-weight: 900; background: transparent; letter-spacing: 1px;")
        
        chip = QFrame()
        chip.setFixedSize(45, 35)
        chip.setStyleSheet("background-color: rgba(255, 255, 255, 0.2); border-radius: 6px;")
        
        header.addWidget(brand)
        header.addStretch()
        header.addWidget(chip)

        bal_label = QLabel("CURRENT BALANCE")
        bal_label.setStyleSheet("font-size: 11px; font-weight: 700; opacity: 0.9; background: transparent; letter-spacing: 1.5px;")

        formatted_balance = "{:,.0f} VND".format(balance)
        amount = QLabel(formatted_balance)
        amount.setStyleSheet("font-size: 36px; font-weight: 800; background: transparent;")

        footer = QHBoxLayout()
        id_label = QLabel(f"●  {wallet_id}")
        id_label.setStyleSheet("font-size: 15px; font-weight: 600; background: transparent;")
        
        visa = QLabel("DEBIT")
        visa.setStyleSheet("font-size: 14px; font-weight: 800; background: transparent; font-style: italic;")

        footer.addWidget(id_label)
        footer.addStretch()
        footer.addWidget(visa)

        layout.addLayout(header)
        layout.addStretch()
        layout.addWidget(bal_label)
        layout.addWidget(amount)
        layout.addStretch()
        layout.addLayout(footer)
