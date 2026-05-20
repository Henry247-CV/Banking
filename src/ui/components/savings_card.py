from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
import src.core.theme as theme
from src.core.utils import safe_currency

from PyQt6.QtCore import Qt, pyqtSignal

class SavingsCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, account):
        super().__init__()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.account = account
        self.setup_ui()
        self.update_theme()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header: Plan Name + Type
        header = QHBoxLayout()
        self.name_label = QLabel(self.account.plan_name)
        self.type_badge = QLabel(self.account.savings_type)
        header.addWidget(self.name_label)
        header.addStretch()
        header.addWidget(self.type_badge)
        layout.addLayout(header)

        # Amounts
        amount_layout = QHBoxLayout()
        self.current_label = QLabel(safe_currency(self.account.current_amount))
        self.target_label = QLabel(f"/ {safe_currency(self.account.target_amount)}")
        amount_layout.addWidget(self.current_label)
        amount_layout.addWidget(self.target_label)
        amount_layout.addStretch()
        layout.addLayout(amount_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(int(self.account.progress))
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)

        # Footer: Progress % + Interest
        footer = QHBoxLayout()
        self.perc_label = QLabel(f"{int(self.account.progress)}% Saved")
        self.interest_label = QLabel(f"{self.account.interest_rate*100}% p.a.")
        footer.addWidget(self.perc_label)
        footer.addStretch()
        footer.addWidget(self.interest_label)
        layout.addLayout(footer)

    def update_theme(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 16px;
            }}
        """)
        self.name_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 16px; font-weight: 800; border: none; background: transparent;")
        self.type_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {theme.CYAN if self.account.savings_type == 'FLEXIBLE' else theme.ORANGE};
                color: white;
                font-size: 10px;
                font-weight: bold;
                padding: 2px 8px;
                border-radius: 4px;
            }}
        """)
        self.current_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: bold; border: none; background: transparent;")
        self.target_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 14px; border: none; background: transparent;")
        self.perc_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 12px; border: none; background: transparent;")
        self.interest_label.setStyleSheet(f"color: {theme.GREEN}; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {theme.PANEL_BG};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {theme.GREEN};
                border-radius: 4px;
            }}
        """)

    def update_data(self, account):
        self.account = account
        self.current_label.setText(safe_currency(self.account.current_amount))
        self.progress_bar.setValue(int(self.account.progress))
        self.perc_label.setText(f"{int(self.account.progress)}% Saved")

