"""Admin Transactions Tab — Full transaction monitoring with search, filters, table, and detail panel.

Layout:
┌──────────────────────────────────────────────────────────┐
│ Search │ Status Filter │ Risk Filter │ Date Filter │ 🔄 │
├──────────────────────────────────────────────────────────┤
│ 128 transactions  │  🚩 3 flagged  │  ⚠ 1 critical     │
├──────────────────────────────────────────────────────────┤
│ ID │ Sender │ Receiver │ Amount │ Date │ Status │ Risk  │
│ ───┼────────┼──────────┼────────┼──────┼────────┼────── │
├──────────────────────────────────────────────────────────┤
│ Transaction Detail Panel (auto-loads on row click)       │
└──────────────────────────────────────────────────────────┘
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QPushButton, QSplitter,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.core.utils import safe_currency
from src.admin.services.admin_transaction_service import AdminTransactionService
from src.admin.components.transaction_detail_card import TransactionDetailCard


class AdminTransactionsTab(QWidget):
    """Admin transaction monitoring tab with search, filters, table, and detail panel."""

    COL_ID = 0
    COL_SENDER = 1
    COL_RECEIVER = 2
    COL_AMOUNT = 3
    COL_DATE = 4
    COL_STATUS = 5
    COL_RISK = 6
    NUM_COLS = 7

    # Color maps
    STATUS_COLORS = {
        "COMPLETED": "#22C55E", "SUCCESS": "#22C55E",
        "PENDING": "#FBBF24", "BLOCKED": "#EF4444",
        "REVIEWING": "#A78BFA",
    }
    RISK_COLORS = {
        "LOW": "#4ADE80", "MEDIUM": "#FBBF24",
        "HIGH": "#FB923C", "CRITICAL": "#F87171",
    }

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self._all_transactions = []
        self._setup_ui()
        self.update_theme()
        self.load_transactions()

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(2)
        splitter.setChildrenCollapsible(False)

        # ── Top: filters + table ──
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(28, 20, 28, 8)
        top_layout.setSpacing(12)

        # Section title
        self.section_title = QLabel(
            self.lang_manager.get_text("admin_transactions_management")
        )
        top_layout.addWidget(self.section_title)

        # Filters row
        filters_row = QHBoxLayout()
        filters_row.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            f"🔍  {self.lang_manager.get_text('admin_search_transactions')}"
        )
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self._apply_filters)

        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All Status", "COMPLETED", "PENDING", "BLOCKED", "REVIEWING"
        ])
        self.status_filter.setFixedHeight(38)
        self.status_filter.setFixedWidth(130)
        self.status_filter.currentTextChanged.connect(self._apply_filters)

        self.risk_filter = QComboBox()
        self.risk_filter.addItems([
            "All Risk", "LOW", "MEDIUM", "HIGH", "CRITICAL"
        ])
        self.risk_filter.setFixedHeight(38)
        self.risk_filter.setFixedWidth(120)
        self.risk_filter.currentTextChanged.connect(self._apply_filters)

        self.date_filter = QComboBox()
        self.date_filter.addItems([
            "All Time", "Today", "Last 7 Days", "Last 30 Days"
        ])
        self.date_filter.setFixedHeight(38)
        self.date_filter.setFixedWidth(130)
        self.date_filter.currentTextChanged.connect(self._apply_filters)

        self.refresh_btn = QPushButton(
            f"🔄  {self.lang_manager.get_text('admin_refresh')}"
        )
        self.refresh_btn.setFixedHeight(38)
        self.refresh_btn.setFixedWidth(100)
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.load_transactions)

        filters_row.addWidget(self.search_input)
        filters_row.addWidget(self.status_filter)
        filters_row.addWidget(self.risk_filter)
        filters_row.addWidget(self.date_filter)
        filters_row.addWidget(self.refresh_btn)
        top_layout.addLayout(filters_row)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        self.count_label = QLabel("0 transactions")
        self.flagged_label = QLabel("🚩 0 flagged")
        self.critical_label = QLabel("⚠ 0 high risk")

        stats_row.addWidget(self.count_label)
        stats_row.addWidget(self.flagged_label)
        stats_row.addWidget(self.critical_label)
        stats_row.addStretch()
        top_layout.addLayout(stats_row)

        # Transactions table (7 columns)
        self.transactions_table = QTableWidget(0, self.NUM_COLS)
        self.transactions_table.setHorizontalHeaderLabels([
            "ID",
            self.lang_manager.get_text("admin_sender"),
            self.lang_manager.get_text("admin_receiver"),
            self.lang_manager.get_text("admin_amount"),
            self.lang_manager.get_text("admin_date"),
            "Status",
            "Risk",
        ])
        self.transactions_table.verticalHeader().setVisible(False)
        self.transactions_table.setShowGrid(False)
        self.transactions_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.transactions_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.transactions_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.transactions_table.setMouseTracking(True)
        self.transactions_table.setMinimumHeight(200)

        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COL_ID, QHeaderView.ResizeMode.Fixed)
        self.transactions_table.setColumnWidth(self.COL_ID, 60)
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.transactions_table.currentCellChanged.connect(self._on_row_selected)
        top_layout.addWidget(self.transactions_table)
        splitter.addWidget(top_widget)

        # ── Bottom: Detail panel ──
        detail_container = QWidget()
        detail_layout = QVBoxLayout(detail_container)
        detail_layout.setContentsMargins(28, 8, 28, 16)
        detail_layout.setSpacing(0)

        self.detail_card = TransactionDetailCard()
        self.detail_card.transaction_action_completed.connect(
            self._on_txn_action_completed
        )
        detail_layout.addWidget(self.detail_card)
        splitter.addWidget(detail_container)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        outer_layout.addWidget(splitter)
        self._splitter = splitter

    def load_transactions(self):
        """Load all transactions and update stats."""
        self._all_transactions = AdminTransactionService.get_all_transactions()
        self._display_transactions(self._all_transactions)
        self._update_stats()
        self.detail_card._show_empty_state()

    def _apply_filters(self, *_args):
        """Apply combined search + status + risk + date filters."""
        query = self.search_input.text().strip()

        status_raw = self.status_filter.currentText()
        status = "All" if "All" in status_raw else status_raw

        risk_raw = self.risk_filter.currentText()
        risk = "All" if "All" in risk_raw else risk_raw

        date_raw = self.date_filter.currentText()
        date = "All" if date_raw == "All Time" else date_raw

        results = AdminTransactionService.search_transactions(
            query, status, risk, date
        )
        self._display_transactions(results)

    def _display_transactions(self, transactions):
        """Populate the transactions table."""
        self.count_label.setText(f"{len(transactions)} transactions")

        if not transactions:
            self.transactions_table.setRowCount(1)
            empty_item = QTableWidgetItem(
                self.lang_manager.get_text("admin_no_txn_found")
            )
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_item.setForeground(QColor(theme.TEXT_SECONDARY))
            self.transactions_table.setItem(0, 0, empty_item)
            self.transactions_table.setSpan(0, 0, 1, self.NUM_COLS)
            return

        self.transactions_table.clearSpans()
        self.transactions_table.setRowCount(len(transactions))

        for row, txn in enumerate(transactions):
            txn_id = str(txn[0]) if txn[0] else "—"
            sender = str(txn[1]) if txn[1] else "N/A"
            receiver = str(txn[3]) if txn[3] else "N/A"  # receiver_account
            amount = float(txn[4]) if txn[4] else 0
            date = str(txn[7])[:16] if txn[7] else "N/A"  # created_at
            review_status = str(txn[10]) if txn[10] else "COMPLETED"  # review_status
            risk_level = str(txn[9]) if txn[9] else "LOW"  # risk_level
            flagged = txn[8]  # flagged

            formatted_amount = safe_currency(abs(amount))
            # Prefix flagged transactions
            display_sender = f"🚩 {sender}" if flagged else sender

            row_data = [
                (txn_id, None),
                (display_sender, theme.RED if flagged else None),
                (receiver, None),
                (formatted_amount, theme.CYAN),
                (date, None),
                (review_status, self.STATUS_COLORS.get(review_status, theme.TEXT_SECONDARY)),
                (risk_level, self.RISK_COLORS.get(risk_level, theme.TEXT_SECONDARY)),
            ]

            for col, (val, color) in enumerate(row_data):
                item = QTableWidgetItem(val)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                if color:
                    item.setForeground(QColor(color))
                self.transactions_table.setItem(row, col, item)

    def _on_row_selected(self, current_row, _col, _prev_row, _prev_col):
        """Load transaction details when a row is selected."""
        if current_row < 0:
            return
        id_item = self.transactions_table.item(current_row, self.COL_ID)
        if not id_item:
            return
        try:
            txn_id = int(id_item.text())
            self.detail_card.load_transaction(txn_id)
        except (ValueError, TypeError):
            pass

    def _on_txn_action_completed(self):
        """Refresh after admin modifies a transaction."""
        self._apply_filters()
        self._update_stats()

    def _update_stats(self):
        """Update the flagged and critical counters."""
        flagged = AdminTransactionService.get_flagged_count()
        critical = AdminTransactionService.get_critical_count()
        self.flagged_label.setText(f"🚩 {flagged} flagged")
        self.critical_label.setText(f"⚠ {critical} high risk")

    def update_theme(self):
        theme.update_globals()

        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")

        self.section_title.setStyleSheet(f"""
            color: {theme.TEXT_PRIMARY}; font-size: 16px; font-weight: 700;
            border: none; background: transparent;
        """)

        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.PANEL_BG}; color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER}; border-radius: 8px;
                padding: 0 14px; font-size: 13px;
            }}
            QLineEdit:focus {{ border: 1px solid {theme.CYAN}; }}
        """)

        combo_style = f"""
            QComboBox {{
                background-color: {theme.PANEL_BG}; color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER}; border-radius: 8px;
                padding: 0 10px; font-size: 12px;
            }}
            QComboBox:hover {{ border: 1px solid {theme.CYAN}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                background-color: {theme.CARD_BG}; color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                selection-background-color: {theme.PANEL_BG};
                selection-color: {theme.CYAN};
            }}
        """
        for combo in [self.status_filter, self.risk_filter, self.date_filter]:
            combo.setStyleSheet(combo_style)

        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.CYAN}; color: white;
                border: none; border-radius: 8px;
                font-size: 12px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {theme.CYAN_HOVER}; }}
        """)

        stats_style = f"""
            color: {theme.TEXT_SECONDARY}; font-size: 12px; font-weight: 500;
            border: none; background: transparent;
        """
        self.count_label.setStyleSheet(stats_style)
        self.flagged_label.setStyleSheet(f"""
            color: {theme.ORANGE}; font-size: 12px; font-weight: 600;
            border: none; background: transparent;
        """)
        self.critical_label.setStyleSheet(f"""
            color: {theme.RED}; font-size: 12px; font-weight: 600;
            border: none; background: transparent;
        """)

        table_style = f"""
            QTableWidget {{
                background-color: {theme.CARD_BG}; color: {theme.TEXT_PRIMARY};
                gridline-color: transparent; border: 1px solid {theme.BORDER};
                border-radius: 10px; font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 8px 12px; border-bottom: 1px solid {theme.BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {theme.PANEL_BG}; color: {theme.CYAN};
            }}
            QTableWidget::item:hover {{
                background-color: {theme.PANEL_BG};
            }}
            QHeaderView::section {{
                background-color: {theme.PANEL_BG}; color: {theme.TEXT_SECONDARY};
                padding: 8px 12px; border: none;
                border-bottom: 2px solid {theme.BORDER};
                font-weight: 700; font-size: 11px; letter-spacing: 0.5px;
            }}
        """
        self.transactions_table.setStyleSheet(table_style)

        self._splitter.setStyleSheet(f"""
            QSplitter::handle {{ background-color: {theme.BORDER}; }}
            QSplitter::handle:hover {{ background-color: {theme.CYAN}; }}
        """)

        self.detail_card.update_theme()

    def update_translations(self):
        self.section_title.setText(
            self.lang_manager.get_text("admin_transactions_management")
        )
        self.search_input.setPlaceholderText(
            f"🔍  {self.lang_manager.get_text('admin_search_transactions')}"
        )
        self.refresh_btn.setText(
            f"🔄  {self.lang_manager.get_text('admin_refresh')}"
        )
        self.detail_card.update_translations()

    def update_ui(self):
        self.load_transactions()
        self.update_theme()
