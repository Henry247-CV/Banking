from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import qrcode
from io import BytesIO
import os

from src.core.theme import *
from src.core.styles import *
from src.core.utils import safe_text, safe_currency
from src.ui.components.virtual_bank_card import VirtualBankCard
from src.ui.components.transaction_table import TransactionTable
from src.services.transfer_service import TransferService
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.services.qr_service import QRService

class WalletTab(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.transfer_service = TransferService()
        self.qr_service = QRService()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.current_qr_img = None
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

        # 1. Virtual Cards Section
        self.setup_cards_section()

        # 2. Balance + QR Section
        self.setup_balance_qr_section()

        # 3. Transaction History
        self.setup_history_section()

        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)
        
        self.refresh_transactions()

    def update_theme(self):
        styles = get_styles()
        self.scroll.verticalScrollBar().setStyleSheet(styles["GLOBAL_STYLE"])
        self.container.setStyleSheet(f"background-color: transparent;")
        
        self.cards_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 20px; font-weight: 800; border: none; background: transparent;")
        self.bal_card.setStyleSheet(styles["CARD_STYLE"])
        self.bal_title_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 14px; font-weight: 600; background: transparent; border: none;")
        self.bal_val.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 32px; font-weight: 800; background: transparent; border: none;")
        
        self.qr_card.setStyleSheet(styles["CARD_STYLE"])
        self.qr_desc.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 12px; font-weight: 700; margin-top: 10px; background: transparent; border: none;")
        self.qr_info_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        self.download_btn.setStyleSheet(styles["PRIMARY_BUTTON"] + "min-height: 34px; font-size: 12px; margin-top: 10px;")
        
        self.history_card.setStyleSheet(styles["CARD_STYLE"])
        self.history_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 20px; font-weight: 800; border: none; background: transparent;")
        self.trans_table.update_theme()
        
        self.refresh_cards()
        self.refresh_qr()

    def update_translations(self):
        self.cards_title.setText(self.lang_manager.get_text("virtual_cards"))
        self.bal_title_lbl.setText(self.lang_manager.get_text("available_balance"))
        self.qr_desc.setText(self.lang_manager.get_text("payment_qr"))
        self.history_title.setText(self.lang_manager.get_text("trans_history"))
        self.download_btn.setText(self.lang_manager.get_text("download_qr"))
        
        phone = self.user_data.get('phone', 'N/A')
        acc = self.user_data.get('account_number', 'N/A')
        self.qr_info_lbl.setText(f"{phone} | {acc}")

    def setup_cards_section(self):
        self.cards_panel = QFrame()
        layout = QVBoxLayout(self.cards_panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        self.cards_title = QLabel("Virtual Banking Cards")
        layout.addWidget(self.cards_title)

        # Horizontal Scroll for Cards
        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setFixedHeight(220)
        self.cards_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.cards_scroll.setStyleSheet("background: transparent;")
        
        self.cards_container = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.refresh_cards()

        self.cards_scroll.setWidget(self.cards_container)
        layout.addWidget(self.cards_scroll)
        self.container_layout.addWidget(self.cards_panel)

    def setup_balance_qr_section(self):
        row = QHBoxLayout()
        row.setSpacing(30)

        # Balance Card
        self.bal_card = QFrame()
        bal_layout = QVBoxLayout(self.bal_card)
        bal_layout.setContentsMargins(25, 25, 25, 25)
        bal_layout.setSpacing(10)

        self.bal_title_lbl = QLabel("Available Balance")
        self.bal_val = QLabel(safe_currency(self.user_data.get('balance')))
        
        bal_layout.addWidget(self.bal_title_lbl)
        bal_layout.addWidget(self.bal_val)
        bal_layout.addStretch()
        
        row.addWidget(self.bal_card, 2)

        # QR Card
        self.qr_card = QFrame()
        self.qr_card.setFixedSize(240, 320)
        qr_layout = QVBoxLayout(self.qr_card)
        qr_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.qr_box = QLabel()
        self.qr_box.setFixedSize(140, 140)
        self.qr_box.setStyleSheet(f"background-color: #FFFFFF; border-radius: 12px; border: 4px solid #FFFFFF;")
        self.qr_box.setScaledContents(True)
        
        qr_layout.addWidget(self.qr_box)
        
        self.qr_desc = QLabel("Personal Payment QR")
        self.qr_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_layout.addWidget(self.qr_desc)
        
        self.qr_info_lbl = QLabel("")
        self.qr_info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_layout.addWidget(self.qr_info_lbl)

        self.download_btn = QPushButton("Download QR")
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.clicked.connect(self.download_qr)
        qr_layout.addWidget(self.download_btn)
        
        row.addWidget(self.qr_card, 1)
        self.container_layout.addLayout(row)

    def setup_history_section(self):
        self.history_card = QFrame()
        trans_layout = QVBoxLayout(self.history_card)
        trans_layout.setContentsMargins(30, 30, 30, 30)

        self.history_title = QLabel("Wallet Transaction History")
        trans_layout.addWidget(self.history_title)
        trans_layout.addSpacing(20)

        self.trans_table = TransactionTable(rows=10, cols=5)
        trans_layout.addWidget(self.trans_table)
        self.container_layout.addWidget(self.history_card)

    def refresh_qr(self):
        # Format: BANK=...;ACCOUNT=...;PHONE=...;USER=...;
        qr_data = f"BANK=Đăng Khoa Bank;ACCOUNT={self.user_data.get('account_number')};PHONE={self.user_data.get('phone')};USER={self.user_data.get('full_name')};"
        
        self.current_qr_img = self.qr_service.generate_qr(qr_data)
        
        # Convert PIL image to QPixmap
        buffer = BytesIO()
        self.current_qr_img.save(buffer, format="PNG")
        qimage = QImage.fromData(buffer.getvalue())
        pixmap = QPixmap.fromImage(qimage)
        self.qr_box.setPixmap(pixmap)

    def download_qr(self):
        if not self.current_qr_img: return
        
        filename = f"DKB_QR_{self.user_data.get('account_number')}.png"
        success, path = self.qr_service.save_qr_to_desktop(self.current_qr_img, filename)
        
        if success:
            QMessageBox.information(self, "QR Downloaded", f"Your payment QR has been saved to:\n{path}")
            if os.name == 'nt':
                os.startfile(os.path.dirname(path))
        else:
            QMessageBox.critical(self, "Download Error", f"Failed to save QR: {path}")

    def refresh_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # 1. User's Real Card
        user_card = VirtualBankCard(
            self.user_data.get('full_name'),
            self.user_data.get('account_number'),
            self.user_data.get('customer_tier', 'STANDARD')
        )
        self.cards_layout.addWidget(user_card)

        # 2. Sample Cards for demo (Other tiers)
        tiers = ["STANDARD", "GOLD", "DIAMOND"]
        for t in tiers:
            if t != self.user_data.get('customer_tier'):
                sample = VirtualBankCard("SAMPLE USER", "DKB20260000", t)
                sample.setStyleSheet(sample.styleSheet() + "QFrame { opacity: 0.7; }")
                self.cards_layout.addWidget(sample)

    def refresh_transactions(self):
        transactions = self.transfer_service.get_user_transactions(self.user_data.get('username'))
        formatted_trans = []
        for t in transactions:
            formatted_trans.append((t[0], t[1], t[2], -t[3], t[4]))
        self.trans_table.load_data(formatted_trans)

    def update_ui(self):
        self.refresh_cards()
        self.bal_val.setText(safe_currency(self.user_data.get('balance')))
        self.refresh_transactions()
        self.refresh_qr()
