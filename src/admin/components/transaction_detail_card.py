"""Transaction Detail Card — Shows selected transaction info with admin action buttons.

Displays: ID, sender, receiver, amount, date, status, risk, flagged, note.
Actions: Mark Safe, Flag, Block, Set Reviewing.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QMessageBox, QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.core.utils import safe_currency, safe_text
from src.admin.services.admin_transaction_service import AdminTransactionService


class RiskBadge(QLabel):
    """Color-coded risk level badge."""

    RISK_CONFIG = {
        "LOW":      {"dark_bg": "#0C2E1A", "dark_fg": "#4ADE80", "light_bg": "#DCFCE7", "light_fg": "#166534"},
        "MEDIUM":   {"dark_bg": "#422006", "dark_fg": "#FBBF24", "light_bg": "#FEF3C7", "light_fg": "#92400E"},
        "HIGH":     {"dark_bg": "#431407", "dark_fg": "#FB923C", "light_bg": "#FFEDD5", "light_fg": "#9A3412"},
        "CRITICAL": {"dark_bg": "#450A0A", "dark_fg": "#F87171", "light_bg": "#FEE2E2", "light_fg": "#991B1B"},
    }

    def __init__(self, level="LOW"):
        super().__init__(level)
        self.level = level.upper()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(24)
        self.setMinimumWidth(70)
        self.update_style()

    def set_level(self, level):
        self.level = level.upper()
        self.setText(self.level)
        self.update_style()

    def update_style(self):
        config = self.RISK_CONFIG.get(self.level, self.RISK_CONFIG["LOW"])
        is_dark = ThemeManager().current_theme == "dark"
        bg = config["dark_bg"] if is_dark else config["light_bg"]
        fg = config["dark_fg"] if is_dark else config["light_fg"]
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg}; color: {fg};
                border-radius: 4px; padding: 2px 8px;
                font-size: 10px; font-weight: 700;
                letter-spacing: 0.5px; border: none;
            }}
        """)


class ReviewStatusBadge(QLabel):
    """Color-coded review status badge."""

    STATUS_CONFIG = {
        "COMPLETED": {"dark_fg": "#4ADE80", "light_fg": "#166534"},
        "PENDING":   {"dark_fg": "#FBBF24", "light_fg": "#92400E"},
        "BLOCKED":   {"dark_fg": "#F87171", "light_fg": "#991B1B"},
        "REVIEWING": {"dark_fg": "#A78BFA", "light_fg": "#6D28D9"},
    }

    def __init__(self, status="COMPLETED"):
        super().__init__(status)
        self.status = status.upper()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(24)
        self.setMinimumWidth(80)
        self.update_style()

    def set_status(self, status):
        self.status = status.upper()
        self.setText(self.status)
        self.update_style()

    def update_style(self):
        config = self.STATUS_CONFIG.get(self.status, self.STATUS_CONFIG["COMPLETED"])
        is_dark = ThemeManager().current_theme == "dark"
        fg = config["dark_fg"] if is_dark else config["light_fg"]
        self.setStyleSheet(f"""
            QLabel {{
                background-color: transparent; color: {fg};
                border: 1px solid {fg}; border-radius: 4px;
                padding: 2px 8px; font-size: 10px;
                font-weight: 700; letter-spacing: 0.5px;
            }}
        """)


class TransactionDetailCard(QFrame):
    """Transaction detail panel with admin action buttons."""

    transaction_action_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self._current_txn = None
        self.setMinimumHeight(200)
        self.setMaximumHeight(300)
        self._setup_ui()
        self.update_theme()
        self._show_empty_state()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 14, 20, 14)
        self.main_layout.setSpacing(10)

        # Title row
        title_row = QHBoxLayout()
        self.detail_title = QLabel(self.lang_manager.get_text("admin_txn_details"))
        self.review_badge = ReviewStatusBadge("COMPLETED")
        self.risk_badge = RiskBadge("LOW")
        self.flag_label = QLabel("🚩 FLAGGED")
        self.flag_label.setVisible(False)

        title_row.addWidget(self.detail_title)
        title_row.addStretch()
        title_row.addWidget(self.flag_label)
        title_row.addWidget(self.risk_badge)
        title_row.addWidget(self.review_badge)
        self.main_layout.addLayout(title_row)

        # Info grid
        self.info_container = QWidget()
        grid = QGridLayout(self.info_container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(5, 1)

        # Row 0
        self.k_id = QLabel("ID")
        self.v_id = QLabel("—")
        self.k_sender = QLabel(self.lang_manager.get_text("admin_sender"))
        self.v_sender = QLabel("—")
        self.k_receiver = QLabel(self.lang_manager.get_text("admin_receiver"))
        self.v_receiver = QLabel("—")

        grid.addWidget(self.k_id, 0, 0)
        grid.addWidget(self.v_id, 0, 1)
        grid.addWidget(self.k_sender, 0, 2)
        grid.addWidget(self.v_sender, 0, 3)
        grid.addWidget(self.k_receiver, 0, 4)
        grid.addWidget(self.v_receiver, 0, 5)

        # Row 1
        self.k_amount = QLabel(self.lang_manager.get_text("admin_amount"))
        self.v_amount = QLabel("—")
        self.k_date = QLabel(self.lang_manager.get_text("admin_date"))
        self.v_date = QLabel("—")
        self.k_note = QLabel(self.lang_manager.get_text("admin_note"))
        self.v_note = QLabel("—")

        grid.addWidget(self.k_amount, 1, 0)
        grid.addWidget(self.v_amount, 1, 1)
        grid.addWidget(self.k_date, 1, 2)
        grid.addWidget(self.v_date, 1, 3)
        grid.addWidget(self.k_note, 1, 4)
        grid.addWidget(self.v_note, 1, 5)

        # Row 2
        self.k_bank = QLabel(self.lang_manager.get_text("bank_name"))
        self.v_bank = QLabel("—")
        self.k_orig_status = QLabel(self.lang_manager.get_text("admin_orig_status"))
        self.v_orig_status = QLabel("—")

        grid.addWidget(self.k_bank, 2, 0)
        grid.addWidget(self.v_bank, 2, 1)
        grid.addWidget(self.k_orig_status, 2, 2)
        grid.addWidget(self.v_orig_status, 2, 3)

        self.main_layout.addWidget(self.info_container)

        # Action buttons
        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)

        self.btn_safe = QPushButton(f"✅  {self.lang_manager.get_text('admin_mark_safe')}")
        self.btn_safe.setFixedHeight(34)
        self.btn_safe.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_safe.clicked.connect(self._on_mark_safe)

        self.btn_flag = QPushButton(f"🚩  {self.lang_manager.get_text('admin_flag_txn')}")
        self.btn_flag.setFixedHeight(34)
        self.btn_flag.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_flag.clicked.connect(self._on_flag)

        self.btn_block = QPushButton(f"⛔  {self.lang_manager.get_text('admin_block_txn')}")
        self.btn_block.setFixedHeight(34)
        self.btn_block.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_block.clicked.connect(self._on_block)

        self.btn_review = QPushButton(f"🔍  {self.lang_manager.get_text('admin_set_reviewing')}")
        self.btn_review.setFixedHeight(34)
        self.btn_review.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_review.clicked.connect(self._on_review)

        actions_row.addWidget(self.btn_safe)
        actions_row.addWidget(self.btn_flag)
        actions_row.addWidget(self.btn_block)
        actions_row.addWidget(self.btn_review)
        actions_row.addStretch()
        self.main_layout.addLayout(actions_row)

        # Empty state
        self.empty_label = QLabel(self.lang_manager.get_text("admin_select_txn"))
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.empty_label)

    def _show_empty_state(self):
        self.info_container.setVisible(False)
        for btn in [self.btn_safe, self.btn_flag, self.btn_block, self.btn_review]:
            btn.setVisible(False)
        self.review_badge.setVisible(False)
        self.risk_badge.setVisible(False)
        self.flag_label.setVisible(False)
        self.empty_label.setVisible(True)
        self.detail_title.setText(self.lang_manager.get_text("admin_txn_details"))

    def load_transaction(self, txn_id):
        """Load a transaction by ID and display details."""
        txn = AdminTransactionService.get_transaction_by_id(txn_id)
        if not txn:
            self._show_empty_state()
            return

        self._current_txn = txn
        self.empty_label.setVisible(False)
        self.info_container.setVisible(True)
        self.review_badge.setVisible(True)
        self.risk_badge.setVisible(True)

        self.v_id.setText(f"#{txn.get('id', 'N/A')}")
        self.v_sender.setText(safe_text(txn.get("sender_username")))
        self.v_receiver.setText(safe_text(txn.get("receiver_account")))
        self.v_amount.setText(safe_currency(abs(float(txn.get("amount", 0)))))
        self.v_date.setText(str(txn.get("created_at", ""))[:16])
        self.v_note.setText(safe_text(txn.get("note"), "—"))
        self.v_bank.setText(safe_text(txn.get("receiver_bank"), "N/A"))
        self.v_orig_status.setText(safe_text(txn.get("status"), "N/A"))

        review_status = safe_text(txn.get("review_status"), "COMPLETED")
        self.review_badge.set_status(review_status)

        risk = safe_text(txn.get("risk_level"), "LOW")
        self.risk_badge.set_level(risk)

        flagged = txn.get("flagged", 0)
        self.flag_label.setVisible(bool(flagged))

        self.detail_title.setText(
            f"{self.lang_manager.get_text('admin_txn_details')} — #{txn.get('id')}"
        )

        # Show/hide buttons contextually
        for btn in [self.btn_safe, self.btn_flag, self.btn_block, self.btn_review]:
            btn.setVisible(True)
        self.btn_safe.setVisible(review_status != "COMPLETED" or bool(flagged))
        self.btn_block.setVisible(review_status != "BLOCKED")
        self.btn_review.setVisible(review_status != "REVIEWING")

        self.update_theme()

    def _confirm(self, title, msg):
        return QMessageBox.question(
            self, title, msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes

    def _on_mark_safe(self):
        if not self._current_txn:
            return
        tid = self._current_txn["id"]
        AdminTransactionService.flag_transaction(tid, flagged=False)
        AdminTransactionService.update_review_status(tid, "COMPLETED")
        AdminTransactionService.update_risk_level(tid, "LOW")
        self.load_transaction(tid)
        self.transaction_action_completed.emit()

    def _on_flag(self):
        if not self._current_txn:
            return
        tid = self._current_txn["id"]
        if not self._confirm(
            self.lang_manager.get_text("admin_flag_txn"),
            f"Flag transaction #{tid} as suspicious?"
        ):
            return
        AdminTransactionService.flag_transaction(tid, flagged=True)
        AdminTransactionService.update_review_status(tid, "REVIEWING")
        self.load_transaction(tid)
        self.transaction_action_completed.emit()

    def _on_block(self):
        if not self._current_txn:
            return
        tid = self._current_txn["id"]
        if not self._confirm(
            self.lang_manager.get_text("admin_block_txn"),
            f"Block transaction #{tid}? The sender will be notified."
        ):
            return
        AdminTransactionService.update_review_status(tid, "BLOCKED")
        AdminTransactionService.flag_transaction(tid, flagged=True)
        self.load_transaction(tid)
        self.transaction_action_completed.emit()

    def _on_review(self):
        if not self._current_txn:
            return
        tid = self._current_txn["id"]
        AdminTransactionService.update_review_status(tid, "REVIEWING")
        self.load_transaction(tid)
        self.transaction_action_completed.emit()

    def update_theme(self):
        theme.update_globals()

        self.setStyleSheet(f"""
            TransactionDetailCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 10px;
            }}
        """)

        self.detail_title.setStyleSheet(f"""
            color: {theme.TEXT_PRIMARY}; font-size: 14px; font-weight: 700;
            border: none; background: transparent;
        """)
        self.empty_label.setStyleSheet(f"""
            color: {theme.TEXT_SECONDARY}; font-size: 13px; font-weight: 500;
            border: none; background: transparent;
        """)
        self.flag_label.setStyleSheet(f"""
            color: {theme.RED}; font-size: 11px; font-weight: 700;
            border: none; background: transparent;
        """)

        key_style = f"""
            color: {theme.TEXT_SECONDARY}; font-size: 11px; font-weight: 600;
            letter-spacing: 0.3px; border: none; background: transparent;
        """
        for k in [self.k_id, self.k_sender, self.k_receiver, self.k_amount,
                   self.k_date, self.k_note, self.k_bank, self.k_orig_status]:
            k.setStyleSheet(key_style)

        val_style = f"""
            color: {theme.TEXT_PRIMARY}; font-size: 12px; font-weight: 600;
            border: none; background: transparent;
        """
        for v in [self.v_id, self.v_sender, self.v_receiver, self.v_date,
                   self.v_note, self.v_bank, self.v_orig_status]:
            v.setStyleSheet(val_style)

        # Amount gets accent color
        self.v_amount.setStyleSheet(f"""
            color: {theme.CYAN}; font-size: 13px; font-weight: 700;
            border: none; background: transparent;
        """)

        self.risk_badge.update_style()
        self.review_badge.update_style()

        # Button styles
        safe_btn = f"""
            QPushButton {{ background-color: {theme.PANEL_BG}; color: {theme.GREEN};
                border: 1px solid {theme.BORDER}; border-radius: 6px;
                padding: 0 10px; font-size: 11px; font-weight: 600; }}
            QPushButton:hover {{ background-color: {theme.GREEN}; color: white;
                border: 1px solid {theme.GREEN}; }}
        """
        self.btn_safe.setStyleSheet(safe_btn)

        flag_btn = f"""
            QPushButton {{ background-color: {theme.PANEL_BG}; color: {theme.ORANGE};
                border: 1px solid {theme.BORDER}; border-radius: 6px;
                padding: 0 10px; font-size: 11px; font-weight: 600; }}
            QPushButton:hover {{ background-color: {theme.ORANGE}; color: white;
                border: 1px solid {theme.ORANGE}; }}
        """
        self.btn_flag.setStyleSheet(flag_btn)

        block_btn = f"""
            QPushButton {{ background-color: {theme.PANEL_BG}; color: {theme.RED};
                border: 1px solid {theme.BORDER}; border-radius: 6px;
                padding: 0 10px; font-size: 11px; font-weight: 600; }}
            QPushButton:hover {{ background-color: {theme.RED}; color: white;
                border: 1px solid {theme.RED}; }}
        """
        self.btn_block.setStyleSheet(block_btn)

        review_btn = f"""
            QPushButton {{ background-color: {theme.PANEL_BG}; color: #A78BFA;
                border: 1px solid {theme.BORDER}; border-radius: 6px;
                padding: 0 10px; font-size: 11px; font-weight: 600; }}
            QPushButton:hover {{ background-color: #7C3AED; color: white;
                border: 1px solid #7C3AED; }}
        """
        self.btn_review.setStyleSheet(review_btn)

    def update_translations(self):
        self.k_sender.setText(self.lang_manager.get_text("admin_sender"))
        self.k_receiver.setText(self.lang_manager.get_text("admin_receiver"))
        self.k_amount.setText(self.lang_manager.get_text("admin_amount"))
        self.k_date.setText(self.lang_manager.get_text("admin_date"))
        self.k_note.setText(self.lang_manager.get_text("admin_note"))
        self.k_bank.setText(self.lang_manager.get_text("bank_name"))
        self.k_orig_status.setText(self.lang_manager.get_text("admin_orig_status"))
        self.btn_safe.setText(f"✅  {self.lang_manager.get_text('admin_mark_safe')}")
        self.btn_flag.setText(f"🚩  {self.lang_manager.get_text('admin_flag_txn')}")
        self.btn_block.setText(f"⛔  {self.lang_manager.get_text('admin_block_txn')}")
        self.btn_review.setText(f"🔍  {self.lang_manager.get_text('admin_set_reviewing')}")
        self.empty_label.setText(self.lang_manager.get_text("admin_select_txn"))
        if not self._current_txn:
            self.detail_title.setText(self.lang_manager.get_text("admin_txn_details"))
