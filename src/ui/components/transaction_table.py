from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.core.theme import *
from src.core.styles import *
from src.design.component_factory import BaseTable

class TransactionTable(BaseTable):
    def __init__(self, rows=5, cols=5):
        super().__init__(rows, cols)
        self.setHorizontalHeaderLabels(["Date", "Bank", "Account", "Amount", "Status"])
        self.update_theme()

    def update_theme(self):
        super().update_theme()
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)


    def load_data(self, transactions):
        """Loads real transaction data into the table."""
        if not transactions:
            self.setRowCount(1)
            item = QTableWidgetItem("No recent transactions.")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(theme.TEXT_SECONDARY))
            self.setItem(0, 0, item)
            self.setSpan(0, 0, 1, 5)
            return

        self.setRowCount(len(transactions))
        self.clearSpans()
        
        for row, data in enumerate(transactions):
            # Date
            date_str = str(data[0])[:16]
            date_item = QTableWidgetItem(date_str)
            self.setItem(row, 0, date_item)

            # Bank
            bank_item = QTableWidgetItem(str(data[1]))
            self.setItem(row, 1, bank_item)

            # Account
            acc_item = QTableWidgetItem(str(data[2]))
            self.setItem(row, 2, acc_item)

            # Amount
            amount = float(data[3])
            formatted_amount = "{:,.0f} VND".format(amount)
            if amount > 0:
                formatted_amount = "+" + formatted_amount
                color = theme.GREEN
            else:
                color = theme.RED
            
            amount_item = QTableWidgetItem(formatted_amount)
            amount_item.setForeground(QColor(color))
            amount_item.setFont(Qt.FontWeight.Bold)
            self.setItem(row, 3, amount_item)

            # Status
            status_item = QTableWidgetItem(str(data[4]))
            status_item.setForeground(QColor(theme.GREEN if str(data[4]) == "SUCCESS" else theme.ORANGE))
            self.setItem(row, 4, status_item)
            
            # Apply common style
            for col in range(5):
                item = self.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
