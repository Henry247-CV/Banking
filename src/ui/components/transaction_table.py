from PyQt6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.core.theme import *
from src.core.styles import *

class TransactionTable(QTableWidget):
    def __init__(self, rows=5, cols=5):
        super().__init__(rows, cols)
        self.setHorizontalHeaderLabels(["Date", "Bank", "Account", "Amount", "Status"])
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(False)
        self.setMouseTracking(True)
        self.update_theme()

    def update_theme(self):
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                color: {theme.TEXT_PRIMARY};
                gridline-color: transparent;
                border: none;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 15px;
                border-bottom: 1px solid {theme.BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {theme.TEXT_SECONDARY};
                padding: 10px 15px;
                border: none;
                border-bottom: 2px solid {theme.BORDER};
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }}
        """)
        
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
