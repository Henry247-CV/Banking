from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QDialog, 
    QPushButton, QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout,
    QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import src.core.theme as theme
from src.core.styles import *
from src.core.language_manager import LanguageManager
from src.core.utils import safe_currency
from src.services.savings_service import SavingsService
from src.core.app_stabilizer import AppStabilizer

class SavingsDetailDialog(QDialog):
    def __init__(self, account, parent=None):
        super().__init__(parent)
        self.account = account
        self.lang_manager = LanguageManager()
        self.setWindowTitle(account.plan_name)
        self.setFixedSize(600, 700)
        self.setup_ui()
        self.update_theme()
        self.load_history()
        
        # Connect Actions
        self.deposit_btn.clicked.connect(self.handle_deposit)
        self.withdraw_btn.clicked.connect(self.handle_withdraw)

        # Setup Auto-Refresh Timer (10 seconds)
        self.refresh_timer = AppStabilizer().create_safe_timer(
            parent=self, interval_ms=10000, callback=self.refresh_view
        )
        self.refresh_timer.start()

    def handle_deposit(self):
        amount, ok = QInputDialog.getDouble(
            self, self.lang_manager.get_text("deposit"), 
            self.lang_manager.get_text("enter_amount"), 
            0, 0, 1000000000, 2
        )
        if ok and amount > 0:
            success, msg = SavingsService.deposit(self.account.id, self.account.username, amount)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.refresh_view()
            else:
                QMessageBox.warning(self, "Error", msg)

    def handle_withdraw(self):
        amount, ok = QInputDialog.getDouble(
            self, self.lang_manager.get_text("withdraw"), 
            self.lang_manager.get_text("enter_amount"), 
            0, 0, self.account.current_amount, 2
        )
        if ok and amount > 0:
            success, msg = SavingsService.withdraw(self.account.id, self.account.username, amount)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.refresh_view()
            else:
                QMessageBox.warning(self, "Error", msg)

    def refresh_view(self):
        """Live update for the detail view."""
        # 1. Fetch latest plan data
        from src.services.savings_service import SavingsService
        plans = SavingsService.get_user_savings(self.account.username)
        for p in plans:
            if p.id == self.account.id:
                self.account = p
                break
        
        # 2. Update labels
        if hasattr(self, 'balance_val_lbl'):
            self.balance_val_lbl.setText(safe_currency(self.account.current_amount))
            
        # 3. Reload History
        self.load_history()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(24)

        # Header Section
        header = QHBoxLayout()
        self.title_lbl = QLabel(self.account.plan_name)
        header.addWidget(self.title_lbl)
        header.addStretch()
        self.status_badge = QLabel(self.account.status)
        header.addWidget(self.status_badge)
        self.layout.addLayout(header)

        # Stats Grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        # Store balance label for live updates
        self.balance_val_lbl = self.add_stat(stats_layout, "current_balance", safe_currency(self.account.current_amount), 0, 0)
        self.add_stat(stats_layout, "target_amount", safe_currency(self.account.target_amount), 0, 1)
        self.add_stat(stats_layout, "interest_rate", f"{self.account.interest_rate*100}%", 1, 0)
        self.add_stat(stats_layout, "maturity_date", str(self.account.end_date)[:10], 1, 1)
        
        self.layout.addLayout(stats_layout)

        # Actions
        actions = QHBoxLayout()
        self.deposit_btn = QPushButton(self.lang_manager.get_text("deposit"))
        self.withdraw_btn = QPushButton(self.lang_manager.get_text("withdraw"))
        actions.addWidget(self.deposit_btn)
        actions.addWidget(self.withdraw_btn)
        self.layout.addLayout(actions)

        # History Table
        self.history_title = QLabel(self.lang_manager.get_text("savings_history"))
        self.layout.addWidget(self.history_title)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Date", "Action", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

    def add_stat(self, layout, key, value, row, col):
        container = QFrame()
        l = QVBoxLayout(container)
        title = QLabel(self.lang_manager.get_text(key))
        val = QLabel(value)
        title.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
        val.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        l.addWidget(title)
        l.addWidget(val)
        container.setStyleSheet(f"background: {theme.PANEL_BG}; border-radius: 8px; border: 1px solid {theme.BORDER}; padding: 10px;")
        layout.addWidget(container, row, col)
        return val # Return label for updates

    def load_history(self):
        history = SavingsService.get_savings_history(self.account.username, self.account.id)
        self.table.setRowCount(len(history))
        for i, tx in enumerate(history):
            self.table.setItem(i, 0, QTableWidgetItem(str(tx.created_at)[:16]))
            self.table.setItem(i, 1, QTableWidgetItem(tx.type))
            item = QTableWidgetItem(safe_currency(tx.amount))
            item.setForeground(QColor(theme.GREEN if tx.type == 'DEPOSIT' else theme.RED))
            self.table.setItem(i, 2, item)

    def update_theme(self):
        styles = get_styles()
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        self.title_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 24px; font-weight: 800;")
        self.status_badge.setStyleSheet(f"background: {theme.GREEN}; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 10px;")
        self.history_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: 700;")
        
        self.deposit_btn.setStyleSheet(styles["PRIMARY_BUTTON"])
        self.withdraw_btn.setStyleSheet(styles["SECONDARY_BUTTON"])
        
        table_style = f"""
            QTableWidget {{
                background-color: {theme.CARD_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 10px;
                gridline-color: transparent;
            }}
            QHeaderView::section {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_SECONDARY};
                padding: 10px;
                border: none;
                font-weight: bold;
            }}
        """
        self.table.setStyleSheet(table_style)
