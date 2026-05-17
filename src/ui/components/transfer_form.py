from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QComboBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.theme import *
from src.core.styles import *
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager

class TransferForm(QFrame):
    transfer_success = pyqtSignal(float)

    def __init__(self, current_balance):
        super().__init__()
        self.current_balance = current_balance
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setup_ui()
        self.update_theme()
        self.update_translations()

    def update_theme(self):
        styles = get_styles()
        self.setStyleSheet(styles["CARD_STYLE"])
        self.title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: bold; border: none; background: transparent;")
        
        combo_style = f"""
            QComboBox {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                min-height: 44px;
            }}
            QComboBox:focus {{
                border: 1px solid {theme.CYAN};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                selection-background-color: {theme.CYAN};
            }}
        """
        self.bank_combo.setStyleSheet(combo_style)
        self.account_input.setStyleSheet(styles["LINE_EDIT_STYLE"])
        self.amount_input.setStyleSheet(styles["LINE_EDIT_STYLE"])
        self.note_input.setStyleSheet(styles["LINE_EDIT_STYLE"])
        self.clear_btn.setStyleSheet(styles["SECONDARY_BUTTON"])
        self.transfer_btn.setStyleSheet(styles["PRIMARY_BUTTON"])
        self.bank_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 12px; border: none; background: transparent;")

    def update_translations(self):
        self.title.setText(self.lang_manager.get_text("transfer_money"))
        self.bank_label.setText(self.lang_manager.get_text("bank_name")) 
        self.account_input.setPlaceholderText(f"{self.lang_manager.get_text('acc_number')} / {self.lang_manager.get_text('phone')}")
        self.amount_input.setPlaceholderText("VND")
        self.note_input.setPlaceholderText(self.lang_manager.get_text("notifications")) 
        self.transfer_btn.setText(self.lang_manager.get_text("transfer_money"))
        self.clear_btn.setText("Clear")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        self.title = QLabel("Money Transfer")
        
        # Receiver Info Panel (Hidden by default, shown after QR upload)
        self.receiver_panel = QFrame()
        self.receiver_panel.setStyleSheet(f"background-color: {PANEL_BG}; border-radius: 12px; border: 1px solid {CYAN};")
        self.receiver_panel.hide()
        rec_layout = QVBoxLayout(self.receiver_panel)
        rec_layout.setContentsMargins(15, 15, 15, 15)
        
        self.rec_name_lbl = QLabel("")
        self.rec_name_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: 800; border: none;")
        self.rec_phone_lbl = QLabel("")
        self.rec_phone_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; border: none;")
        
        rec_layout.addWidget(self.rec_name_lbl)
        rec_layout.addWidget(self.rec_phone_lbl)

        self.bank_combo = QComboBox()
        self.bank_combo.addItems([
            "Vietcombank", "Techcombank", "MB Bank", "ACB", "BIDV", "VPBank", "Đăng Khoa Bank"
        ])

        self.account_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.note_input = QLineEdit()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_form)

        self.transfer_btn = QPushButton("Transfer Money")
        self.transfer_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.transfer_btn)

        layout.addWidget(self.title)
        layout.addWidget(self.receiver_panel)
        layout.addSpacing(10)
        self.bank_label = QLabel("Select Bank")
        layout.addWidget(self.bank_label)
        layout.addWidget(self.bank_combo)
        layout.addWidget(self.account_input)
        layout.addWidget(self.amount_input)
        layout.addWidget(self.note_input)
        layout.addSpacing(10)
        layout.addLayout(btn_layout)

    def clear_form(self):
        self.account_input.clear()
        self.amount_input.clear()
        self.note_input.clear()
        self.bank_combo.setCurrentIndex(0)
        self.receiver_panel.hide()

    def fill_data(self, data):
        """Auto-fills the form from decoded QR data."""
        if 'ACCOUNT' in data:
            self.account_input.setText(data['ACCOUNT'])
        if 'BANK' in data:
            index = self.bank_combo.findText(data['BANK'])
            if index >= 0: self.bank_combo.setCurrentIndex(index)
        
        if 'USER' in data:
            self.rec_name_lbl.setText(f"Receiver: {data['USER']}")
            self.rec_phone_lbl.setText(f"Phone: {data.get('PHONE', 'N/A')}")
            self.receiver_panel.show()

    def get_data(self):
        return {
            "bank": self.bank_combo.currentText(),
            "account": self.account_input.text().strip(),
            "amount": self.amount_input.text().strip(),
            "note": self.note_input.text().strip()
        }
