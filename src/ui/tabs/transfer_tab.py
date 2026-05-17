from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QMessageBox,
    QScrollArea,
    QPushButton,
    QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.theme import *
from src.core.styles import *
from src.ui.components.transfer_form import TransferForm
from src.ui.components.transaction_table import TransactionTable
from src.services.transfer_service import TransferService
from src.services.qr_service import QRService
from PyQt6.QtWidgets import QFileDialog

from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager

class TransferTab(QWidget):
    balance_updated = pyqtSignal()

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.transfer_service = TransferService()
        self.qr_service = QRService()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setup_ui()
        self.update_theme()
        self.update_translations()

    def update_theme(self):
        styles = get_styles()
        self.scroll.verticalScrollBar().setStyleSheet(styles["GLOBAL_STYLE"])
        
        self.upload_container.setStyleSheet(styles["CARD_STYLE"])
        self.upload_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        self.upload_btn.setStyleSheet(styles["SECONDARY_BUTTON"] + "min-height: 40px; font-weight: bold;")
        
        self.history_container.setStyleSheet(styles["CARD_STYLE"])
        self.history_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 20px; font-weight: 800; border: none; background: transparent;")
        self.trans_table.update_theme()
        self.transfer_form.update_theme()

    def update_translations(self):
        self.upload_title.setText(self.lang_manager.get_text("upload_qr"))
        self.upload_btn.setText(self.lang_manager.get_text("select_qr"))
        self.history_title.setText(self.lang_manager.get_text("outgoing_trans"))
        self.transfer_form.update_translations()

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

        # 1. Upload QR Section
        self.upload_container = QFrame()
        up_layout = QVBoxLayout(self.upload_container)
        up_layout.setContentsMargins(25, 25, 25, 25)
        up_layout.setSpacing(15)

        self.upload_title = QLabel("Upload Payment QR")
        self.upload_btn = QPushButton("Select QR Image")
        self.upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.upload_btn.clicked.connect(self.handle_qr_upload)
        
        up_layout.addWidget(self.upload_title)
        up_layout.addWidget(self.upload_btn)
        self.container_layout.addWidget(self.upload_container)

        # 2. Top Section (Form)
        self.transfer_form = TransferForm(self.user_data['balance'])
        self.transfer_form.transfer_btn.clicked.connect(self.handle_transfer)
        self.container_layout.addWidget(self.transfer_form)

        # 3. History Section
        self.history_container = QFrame()
        history_layout = QVBoxLayout(self.history_container)
        history_layout.setContentsMargins(30, 30, 30, 30)

        self.history_title = QLabel("Recent Outgoing Transfers")
        history_layout.addWidget(self.history_title)
        history_layout.addSpacing(20)

        self.trans_table = TransactionTable(rows=5, cols=5)
        history_layout.addWidget(self.trans_table)

        self.container_layout.addWidget(self.history_container)
        self.container_layout.addStretch()

        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        # Initial data load
        self.refresh_history()

    def handle_qr_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Payment QR",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            success, decoded_text = self.qr_service.decode_qr_image(file_path)
            if success:
                qr_data = self.qr_service.parse_qr_data(decoded_text)
                if 'ACCOUNT' in qr_data:
                    self.transfer_form.fill_data(qr_data)
                    QMessageBox.information(self, "QR Decoded", "Transfer information has been auto-filled.")
                else:
                    QMessageBox.warning(self, "Invalid QR", "This QR code does not contain valid payment information.")
            else:
                QMessageBox.critical(self, "Error", f"Unable to read payment QR: {decoded_text}")

    def handle_transfer(self):
        data = self.transfer_form.get_data()
        
        # Validation
        if not data['account'] or not data['amount']:
            QMessageBox.warning(self, "Required Fields", "Please provide a valid account number and transfer amount.")
            return

        try:
            amount = float(data['amount'])
            if amount <= 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid numeric positive amount.")
            return

        if amount > self.user_data['balance']:
            QMessageBox.warning(self, "Insufficient Funds", f"Your current balance is only {"{:,.0f}".format(self.user_data['balance'])} VND.")
            return

        # Process Transfer
        receiver_id = data['account']
        
        # Check if it's a phone number (simple check: starts with 0 and 10 digits)
        from src.services.user_service import UserService
        if receiver_id.startswith('0') and len(receiver_id) >= 10:
            user = UserService.get_user_by_phone(receiver_id)
            if user:
                receiver_id = user['account_number']
                # Show confirmation
                reply = QMessageBox.question(self, "Resolve Phone", f"Found user: {user['full_name']}\nAccount: {user['account_number']}\n\nDo you want to proceed?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return

        success, message = self.transfer_service.create_transfer(
            self.user_data['username'],
            data['bank'],
            receiver_id,
            amount,
            data['note']
        )

        if success:
            self.user_data['balance'] -= amount
            
            # Generate and open bill
            self.transfer_service.generate_transfer_bill(
                self.user_data['username'],
                data['bank'],
                data['account'],
                amount,
                data['note']
            )

            QMessageBox.information(self, "Transfer Success", "The transaction has been processed. A bill has been generated on your Desktop.")
            self.transfer_form.clear_form()
            self.refresh_history()
            self.balance_updated.emit()
        else:
            QMessageBox.critical(self, "Error", message)

    def refresh_history(self):
        transactions = self.transfer_service.get_user_transactions(self.user_data['username'])
        formatted_trans = []
        for t in transactions:
            formatted_trans.append((t[0], t[1], t[2], -t[3], t[4]))
        self.trans_table.load_data(formatted_trans)

    def update_ui(self):
        self.refresh_history()
