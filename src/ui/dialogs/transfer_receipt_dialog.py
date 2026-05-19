from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QApplication, QFrame
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.core.language_manager import LanguageManager
from src.ui.components.receipt_card import ReceiptCard
from src.services.receipt_service import ReceiptService


class TransferReceiptDialog(QDialog):
    """
    Premium modal dialog to display and manage transfer receipts.
    """

    def __init__(self, txn_data: dict, parent=None):
        super().__init__(parent)
        self.txn_data = txn_data
        self.lang_manager = LanguageManager()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()
        self.update_theme()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Background Container (for shadow/border)
        self.container = QFrame()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(20, 20, 20, 20)
        self.container_layout.setSpacing(20)

        # 1. Receipt Card
        self.receipt_card = ReceiptCard(self.txn_data)
        self.container_layout.addWidget(self.receipt_card)

        # 2. Action Buttons
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(10)

        self.copy_btn = QPushButton(self.lang_manager.get_text("copy_id") or "Copy ID")
        self.save_btn = QPushButton(self.lang_manager.get_text("save_receipt") or "Save Image")
        self.close_btn = QPushButton(self.lang_manager.get_text("close") or "Close")

        for btn in [self.copy_btn, self.save_btn, self.close_btn]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(40)

        self.copy_btn.clicked.connect(self.handle_copy_id)
        self.save_btn.clicked.connect(self.handle_save_image)
        self.close_btn.clicked.connect(self.accept)

        self.actions_layout.addWidget(self.copy_btn)
        self.actions_layout.addWidget(self.save_btn)
        self.actions_layout.addWidget(self.close_btn)
        
        self.container_layout.addLayout(self.actions_layout)
        self.main_layout.addWidget(self.container)

    def update_theme(self):
        styles = get_styles()
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {BACKGROUND};
                border: 1px solid {BORDER};
                border-radius: 30px;
            }}
        """)
        
        self.copy_btn.setStyleSheet(styles["SECONDARY_BUTTON"])
        self.save_btn.setStyleSheet(styles["PRIMARY_BUTTON"])
        self.close_btn.setStyleSheet(styles["SECONDARY_BUTTON"])

    def handle_copy_id(self):
        txn_id = self.txn_data.get('transaction_id', '')
        QApplication.clipboard().setText(txn_id)
        
        # Small temporary visual feedback on button
        old_text = self.copy_btn.text()
        self.copy_btn.setText("Copied!")
        self.copy_btn.setEnabled(False)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.reset_copy_btn(old_text))

    def reset_copy_btn(self, text):
        self.copy_btn.setText(text)
        self.copy_btn.setEnabled(True)

    def handle_save_image(self):
        success, result = ReceiptService.save_widget_as_image(
            self.receipt_card, 
            self.txn_data.get('transaction_id', 'TXN')
        )
        
        if success:
            self.save_btn.setText("Saved to Desktop!")
            self.save_btn.setEnabled(False)
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.save_btn.setText(self.lang_manager.get_text("save_receipt") or "Save Image"))
            QTimer.singleShot(2000, lambda: self.save_btn.setEnabled(True))
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Could not save receipt: {result}")
