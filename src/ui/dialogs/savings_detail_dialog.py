from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QProgressBar, QMessageBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from datetime import datetime
from src.core import theme
from src.core.language_manager import LanguageManager
from src.models.savings_model import SavingsAccount, SavingsType
from src.services.savings_service import SavingsService

class SavingsDetailDialog(QDialog):
    def __init__(self, username: str, plan: SavingsAccount, parent=None):
        super().__init__(parent)
        self.username = username
        self.plan = plan
        self.lang_manager = LanguageManager()
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        self.setWindowTitle(self.plan.plan_name)
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background-color: {theme.PANEL_BG};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Header Info
        header_layout = QHBoxLayout()
        title_label = QLabel(self.plan.plan_name)
        title_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 24px; font-weight: 800;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        status_label = QLabel(self.plan.status)
        status_label.setStyleSheet(f"""
            background-color: {theme.GREEN}22;
            color: {theme.GREEN};
            border-radius: 8px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: bold;
        """)
        header_layout.addWidget(status_label)
        layout.addLayout(header_layout)

        # Progress Section
        progress_card = QFrame()
        progress_card.setStyleSheet(f"background-color: {theme.SIDEBAR_BG}; border-radius: 15px; border: 1px solid {theme.BORDER};")
        p_layout = QVBoxLayout(progress_card)
        p_layout.setContentsMargins(20, 20, 20, 20)

        # Percent & Progress Bar
        percentage = min(100, int((self.plan.current_amount / self.plan.target_amount) * 100)) if self.plan.target_amount > 0 else 0
        p_header = QHBoxLayout()
        p_header.addWidget(QLabel(f"{percentage}% Completed", styleSheet=f"color: {theme.TEXT_PRIMARY}; font-weight: bold; border:none;"))
        p_header.addStretch()
        p_header.addWidget(QLabel(f"{self.plan.current_amount:,.0f} / {self.plan.target_amount:,.0f} VND", styleSheet=f"color: {theme.TEXT_SECONDARY}; border:none;"))
        p_layout.addLayout(p_header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(percentage)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setStyleSheet(f"QProgressBar {{ background-color: {theme.BORDER}; border-radius: 6px; }} QProgressBar::chunk {{ background-color: {theme.CYAN}; border-radius: 6px; }}")
        p_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_card)

        # Action Buttons
        action_layout = QHBoxLayout()
        
        self.deposit_amount = QDoubleSpinBox()
        self.deposit_amount.setRange(10000, 100000000)
        self.deposit_amount.setSingleStep(100000)
        self.deposit_amount.setValue(500000)
        self.deposit_amount.setStyleSheet(self.get_input_style())
        action_layout.addWidget(self.deposit_amount)

        deposit_btn = QPushButton(self.lang_manager.get_text("deposit_savings"))
        deposit_btn.clicked.connect(self.handle_deposit)
        deposit_btn.setStyleSheet(self.get_btn_style(theme.CYAN))
        action_layout.addWidget(deposit_btn)

        withdraw_btn = QPushButton(self.lang_manager.get_text("withdraw_savings"))
        withdraw_btn.clicked.connect(self.handle_withdraw)
        withdraw_btn.setStyleSheet(self.get_btn_style(theme.RED))
        action_layout.addWidget(withdraw_btn)
        
        layout.addLayout(action_layout)

        # History Table
        layout.addWidget(QLabel(self.lang_manager.get_text("savings_history"), styleSheet=f"color: {theme.TEXT_PRIMARY}; font-weight: bold;"))
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels([
            self.lang_manager.get_text("admin_date"),
            self.lang_manager.get_text("action"),
            self.lang_manager.get_text("admin_amount")
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setStyleSheet(f"""
            QTableWidget {{ background-color: transparent; border: none; color: {theme.TEXT_PRIMARY}; }}
            QHeaderView::section {{ background-color: {theme.SIDEBAR_BG}; color: {theme.TEXT_SECONDARY}; border: none; padding: 10px; }}
        """)
        layout.addWidget(self.history_table)

    def get_input_style(self):
        return f"background-color: {theme.SIDEBAR_BG}; color: {theme.TEXT_PRIMARY}; border: 1px solid {theme.BORDER}; border-radius: 10px; padding: 8px;"

    def get_btn_style(self, color):
        return f"background-color: {color}; color: white; border-radius: 10px; padding: 10px 20px; font-weight: bold;"

    def load_history(self):
        history = SavingsService.get_savings_history(self.plan.savings_id)
        self.history_table.setRowCount(len(history))
        for i, entry in enumerate(history):
            self.history_table.setItem(i, 0, QTableWidgetItem(entry["created_at"]))
            self.history_table.setItem(i, 1, QTableWidgetItem(entry["transaction_type"]))
            self.history_table.setItem(i, 2, QTableWidgetItem(f"{entry['amount']:,.0f}"))

    def handle_deposit(self):
        amount = self.deposit_amount.value()
        success, msg = SavingsService.deposit(self.username, self.plan.savings_id, amount)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", msg)

    def handle_withdraw(self):
        # 1. Validation for fixed plans
        if self.plan.savings_type == SavingsType.FIXED:
            from datetime import datetime
            try:
                end_dt = datetime.strptime(self.plan.end_date, "%Y-%m-%d %H:%M:%S")
                if datetime.now() < end_dt:
                    msg = (
                        f"This fixed savings plan matures on {self.plan.end_date}.\n\n"
                        "Early withdrawal is NOT permitted for fixed plans in this version.\n"
                        "Please wait until the maturity date."
                    )
                    QMessageBox.warning(self, "Plan Not Matured", msg)
                    return
            except Exception as e:
                print(f"Date parsing error: {e}")

        # 2. Amount Validation
        amount = self.deposit_amount.value()
        if amount > self.plan.current_amount:
            QMessageBox.warning(self, "Insufficient Funds", 
                                f"You can only withdraw up to {self.plan.current_amount:,.0f} VND.")
            return

        # 3. Confirmation
        confirm_msg = f"Are you sure you want to withdraw {amount:,.0f} VND to your wallet?"
        reply = QMessageBox.question(self, "Confirm Withdrawal", confirm_msg,
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.No:
            return

        # 4. Execute
        success, msg = SavingsService.withdraw(self.username, self.plan.savings_id, amount)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "Withdrawal Failed", msg)
