"""Admin Users Tab — Full user management with search, filters, table, and detail panel.

Layout:
┌──────────────────────────────────────────────┐
│ Search Input  │ Status Filter │ Tier Filter │ Refresh │
├──────────────────────────────────────────────┤
│ 24 users                                     │
├──────────────────────────────────────────────┤
│                                              │
│ Users Table (7 columns)                      │
│                                              │
├──────────────────────────────────────────────┤
│                                              │
│ User Detail Panel (with action buttons)      │
│                                              │
└──────────────────────────────────────────────┘
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QPushButton, QSplitter,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.core.utils import safe_currency
from src.admin.services.admin_user_service import AdminUserService
from src.admin.components.admin_user_detail_card import AdminUserDetailCard


class AdminUsersTab(QWidget):
    """Admin users management tab with search, filters, table, and detail panel."""

    # Table column indices
    COL_USERNAME = 0
    COL_PHONE = 1
    COL_ACCNUM = 2
    COL_TIER = 3
    COL_BALANCE = 4
    COL_STATUS = 5
    COL_CREATED = 6
    NUM_COLS = 7

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self._all_users = []
        self._setup_ui()
        self.update_theme()
        self.load_users()

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Use a splitter for table + detail panel
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(2)
        splitter.setChildrenCollapsible(False)

        # ── Top section: search + filters + table ──
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(28, 20, 28, 8)
        top_layout.setSpacing(12)

        # Section title
        self.section_title = QLabel(self.lang_manager.get_text("admin_users_management"))
        top_layout.addWidget(self.section_title)

        # Search + Filters row
        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            f"🔍  {self.lang_manager.get_text('admin_search_users')}"
        )
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self._apply_filters)

        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All Status", "ACTIVE", "FROZEN", "SUSPENDED"
        ])
        self.status_filter.setFixedHeight(38)
        self.status_filter.setFixedWidth(140)
        self.status_filter.currentTextChanged.connect(self._apply_filters)

        self.tier_filter = QComboBox()
        self.tier_filter.addItems([
            "All Tiers", "STANDARD", "GOLD", "DIAMOND"
        ])
        self.tier_filter.setFixedHeight(38)
        self.tier_filter.setFixedWidth(130)
        self.tier_filter.currentTextChanged.connect(self._apply_filters)

        self.refresh_btn = QPushButton(f"🔄  {self.lang_manager.get_text('admin_refresh')}")
        self.refresh_btn.setFixedHeight(38)
        self.refresh_btn.setFixedWidth(110)
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.load_users)

        filters_row.addWidget(self.search_input)
        filters_row.addWidget(self.status_filter)
        filters_row.addWidget(self.tier_filter)
        filters_row.addWidget(self.refresh_btn)
        top_layout.addLayout(filters_row)

        # Count label
        self.count_label = QLabel("0 users")
        top_layout.addWidget(self.count_label)

        # Users table (7 columns now)
        self.users_table = QTableWidget(0, self.NUM_COLS)
        self.users_table.setHorizontalHeaderLabels([
            self.lang_manager.get_text("username"),
            self.lang_manager.get_text("phone"),
            self.lang_manager.get_text("acc_number"),
            "Tier",
            self.lang_manager.get_text("total_balance"),
            "Status",
            self.lang_manager.get_text("admin_created_at"),
        ])
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setShowGrid(False)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.users_table.setMouseTracking(True)
        self.users_table.setMinimumHeight(200)

        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Connect row selection to detail panel
        self.users_table.currentCellChanged.connect(self._on_row_selected)

        top_layout.addWidget(self.users_table)

        splitter.addWidget(top_widget)

        # ── Bottom section: User detail panel ──
        detail_container = QWidget()
        detail_layout = QVBoxLayout(detail_container)
        detail_layout.setContentsMargins(28, 8, 28, 16)
        detail_layout.setSpacing(0)

        self.detail_card = AdminUserDetailCard()
        self.detail_card.user_action_completed.connect(self._on_user_action_completed)
        detail_layout.addWidget(self.detail_card)

        splitter.addWidget(detail_container)

        # Set stretch factors: table gets more space
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        outer_layout.addWidget(splitter)
        self._splitter = splitter

    def load_users(self):
        """Load all users from database via admin service."""
        self._all_users = AdminUserService.get_all_users()
        self._display_users(self._all_users)
        # Clear detail panel on refresh
        self.detail_card._show_empty_state()

    def _apply_filters(self, *_args):
        """Apply combined search + status + tier filters."""
        search_text = self.search_input.text().strip()

        status_raw = self.status_filter.currentText()
        status = "All" if "All" in status_raw else status_raw

        tier_raw = self.tier_filter.currentText()
        tier = "All" if "All" in tier_raw else tier_raw

        results = AdminUserService.search_users(search_text, status, tier)
        self._display_users(results)

    def _display_users(self, users):
        """Populate the users table with data."""
        self.count_label.setText(f"{len(users)} users")

        if not users:
            self.users_table.setRowCount(1)
            empty_item = QTableWidgetItem(
                self.lang_manager.get_text("admin_no_users_found")
            )
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_item.setForeground(QColor(theme.TEXT_SECONDARY))
            self.users_table.setItem(0, 0, empty_item)
            self.users_table.setSpan(0, 0, 1, self.NUM_COLS)
            return

        self.users_table.clearSpans()
        self.users_table.setRowCount(len(users))

        for row, user in enumerate(users):
            username = str(user[1]) if user[1] else "N/A"       # username
            phone = str(user[3]) if user[3] else "N/A"          # phone
            acc_num = str(user[4]) if user[4] else "N/A"        # account_number
            tier = str(user[5]) if user[5] else "STANDARD"      # customer_tier
            balance = safe_currency(user[6])                     # balance
            status = str(user[7]) if user[7] else "ACTIVE"      # account_status
            created = str(user[9])[:16] if user[9] else "N/A"   # created_at

            row_data = [username, phone, acc_num, tier, balance, status, created]

            for col, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )

                # Color coding
                if col == self.COL_TIER:
                    tier_colors = {
                        "DIAMOND": theme.CYAN,
                        "GOLD": "#D4AF37",
                        "STANDARD": theme.TEXT_SECONDARY,
                    }
                    item.setForeground(QColor(tier_colors.get(tier, theme.TEXT_SECONDARY)))
                elif col == self.COL_STATUS:
                    status_colors = {
                        "ACTIVE": theme.GREEN,
                        "FROZEN": theme.ORANGE,
                        "SUSPENDED": theme.RED,
                    }
                    item.setForeground(QColor(status_colors.get(status, theme.TEXT_SECONDARY)))

                self.users_table.setItem(row, col, item)

    def _on_row_selected(self, current_row, _current_col, _prev_row, _prev_col):
        """When a row is selected, load user details."""
        if current_row < 0:
            return
        username_item = self.users_table.item(current_row, self.COL_USERNAME)
        if not username_item:
            return
        username = username_item.text()
        if username and username != "N/A":
            self.detail_card.load_user(username)

    def _on_user_action_completed(self):
        """Called when detail panel modifies a user — refresh table."""
        self._apply_filters()

    def update_theme(self):
        theme.update_globals()

        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")

        self.section_title.setStyleSheet(f"""
            color: {theme.TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 700;
            border: none;
            background: transparent;
        """)

        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {theme.CYAN};
            }}
        """)

        combo_style = f"""
            QComboBox {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 8px;
                padding: 0 10px;
                font-size: 12px;
            }}
            QComboBox:hover {{
                border: 1px solid {theme.CYAN};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 22px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme.CARD_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                selection-background-color: {theme.PANEL_BG};
                selection-color: {theme.CYAN};
            }}
        """
        self.status_filter.setStyleSheet(combo_style)
        self.tier_filter.setStyleSheet(combo_style)

        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.CYAN};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.CYAN_HOVER};
            }}
        """)

        self.count_label.setStyleSheet(f"""
            color: {theme.TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 500;
            border: none;
            background: transparent;
        """)

        table_style = f"""
            QTableWidget {{
                background-color: {theme.CARD_BG};
                color: {theme.TEXT_PRIMARY};
                gridline-color: transparent;
                border: 1px solid {theme.BORDER};
                border-radius: 10px;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {theme.BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {theme.PANEL_BG};
                color: {theme.CYAN};
            }}
            QTableWidget::item:hover {{
                background-color: {theme.PANEL_BG};
            }}
            QHeaderView::section {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_SECONDARY};
                padding: 8px 12px;
                border: none;
                border-bottom: 2px solid {theme.BORDER};
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            }}
        """
        self.users_table.setStyleSheet(table_style)

        # Splitter handle style
        self._splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {theme.BORDER};
            }}
            QSplitter::handle:hover {{
                background-color: {theme.CYAN};
            }}
        """)

        # Update detail card
        self.detail_card.update_theme()

    def update_translations(self):
        self.section_title.setText(self.lang_manager.get_text("admin_users_management"))
        self.search_input.setPlaceholderText(
            f"🔍  {self.lang_manager.get_text('admin_search_users')}"
        )
        self.refresh_btn.setText(f"🔄  {self.lang_manager.get_text('admin_refresh')}")
        self.detail_card.update_translations()

    def update_ui(self):
        self.load_users()
        self.update_theme()
