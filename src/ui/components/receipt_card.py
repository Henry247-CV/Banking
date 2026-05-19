from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.core.theme import *
from src.core.styles import *
from src.core.language_manager import LanguageManager
from src.services.receipt_service import ReceiptService


class ReceiptCard(QFrame):
    """
    A modern fintech-style receipt card.
    Displays transaction success, amount, and details.
    """

    def __init__(self, txn_data: dict, parent=None):
        super().__init__(parent)
        self.txn_data = txn_data
        self.lang_manager = LanguageManager()
        self.setup_ui()
        self.update_theme()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 40, 30, 40)
        self.layout.setSpacing(15)
        self.setFixedWidth(380)

        # 1. Success Header
        self.header_layout = QVBoxLayout()
        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_lbl = QLabel("✓")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setFixedSize(60, 60)
        
        self.status_lbl = QLabel(self.lang_manager.get_text("transfer_success") or "Transfer Successful")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.header_layout.addWidget(self.icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        self.header_layout.addWidget(self.status_lbl)
        self.layout.addLayout(self.header_layout)
        self.layout.addSpacing(10)

        # 2. Amount Section
        self.amount_lbl = QLabel(ReceiptService.format_amount(self.txn_data.get('amount', 0)))
        self.amount_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.amount_lbl)
        
        # Divider
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.Shape.HLine)
        self.divider.setFixedHeight(1)
        self.layout.addWidget(self.divider)
        self.layout.addSpacing(10)

        # 3. Details Section
        self.details_layout = QVBoxLayout()
        self.details_layout.setSpacing(12)

        self.add_detail_row("receiver_name", self.txn_data.get('receiver_bank', 'DKB'))
        self.add_detail_row("receiver_account", self.txn_data.get('receiver_account', 'N/A'))
        self.add_detail_row("transaction_type", self.txn_data.get('transaction_type', 'TRANSFER'))
        self.add_detail_row("transaction_id", self.txn_data.get('transaction_id', 'N/A'))
        self.add_detail_row("date_time", ReceiptService.format_date(self.txn_data.get('created_at', '')))
        
        if self.txn_data.get('note'):
            self.add_detail_row("note", self.txn_data.get('note'))

        self.layout.addLayout(self.details_layout)
        self.layout.addSpacing(20)

        # 4. Footer Badge
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.badge = QLabel("SUCCESS")
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge.setFixedSize(100, 30)
        
        self.footer_layout.addWidget(self.badge)
        self.layout.addLayout(self.footer_layout)

    def add_detail_row(self, label_key, value):
        row = QHBoxLayout()
        label = QLabel(self.lang_manager.get_text(label_key) or label_key.replace("_", " ").title())
        val = QLabel(str(value))
        val.setWordWrap(True)
        val.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: 500;")
        val.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 700;")
        
        row.addWidget(label)
        row.addWidget(val)
        self.details_layout.addLayout(row)

    def update_theme(self):
        """Update colors based on theme."""
        import src.core.theme as theme
        theme.update_globals()
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.CARD_BG};
                border-radius: 20px;
                border: 1px solid {theme.BORDER};
            }}
        """)
        
        self.icon_lbl.setStyleSheet(f"""
            background-color: {theme.GREEN}22;
            color: {theme.GREEN};
            border-radius: 30px;
            font-size: 28px;
            font-weight: 900;
        """)
        
        self.status_lbl.setStyleSheet(f"color: {theme.GREEN}; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        self.amount_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 32px; font-weight: 900; border: none; background: transparent;")
        self.divider.setStyleSheet(f"background-color: {theme.BORDER}; border: none;")
        
        self.badge.setStyleSheet(f"""
            background-color: {theme.CYAN}22;
            color: {theme.CYAN};
            border: 1px solid {theme.CYAN};
            border-radius: 15px;
            font-size: 11px;
            font-weight: 800;
        """)
