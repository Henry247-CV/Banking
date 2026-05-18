"""Admin User Detail Card — Displays selected user's full info with action buttons.

Shows: username, phone, account number, balance, tier, status, join date, last login.
Actions: Freeze, Unfreeze, Suspend, Upgrade Tier, Downgrade Tier.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QMessageBox, QComboBox,
    QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.core.utils import safe_currency, safe_text
from src.admin.services.admin_user_service import AdminUserService
from src.admin.dialogs.admin_security_dialog import AdminSecurityDialog
from src.services.auth_service import AuthService
from PyQt6.QtWidgets import QDialog


class StatusBadge(QLabel):
    """Colored status badge label."""

    STATUS_CONFIG = {
        "ACTIVE": {"color": "#22C55E", "bg": "#052E16", "light_bg": "#DCFCE7", "light_color": "#166534"},
        "FROZEN": {"color": "#F59E0B", "bg": "#422006", "light_bg": "#FEF3C7", "light_color": "#92400E"},
        "SUSPENDED": {"color": "#EF4444", "bg": "#450A0A", "light_bg": "#FEE2E2", "light_color": "#991B1B"},
    }

    def __init__(self, status="ACTIVE"):
        super().__init__(status)
        self.status = status.upper()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(28)
        self.setMinimumWidth(80)
        self.update_style()

    def set_status(self, status):
        self.status = status.upper()
        self.setText(self.status)
        self.update_style()

    def update_style(self):
        theme.update_globals()
        config = self.STATUS_CONFIG.get(self.status, self.STATUS_CONFIG["ACTIVE"])

        is_dark = ThemeManager().current_theme == "dark"
        bg = config["bg"] if is_dark else config["light_bg"]
        color = config["color"] if is_dark else config["light_color"]

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                border-radius: 4px;
                padding: 2px 10px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
                border: none;
            }}
        """)


class AdminUserDetailCard(QFrame):
    """Enterprise user detail panel shown when a user row is selected.
    
    Emits user_action_completed when an admin action modifies user data,
    so parent can refresh the users table.
    """
    user_action_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setObjectName("AdminUserDetailCard")
        self._current_user = None
        self.setMinimumHeight(220)
        self.setMaximumHeight(320)
        self._setup_ui()
        self.update_theme()
        self._show_empty_state()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 16, 20, 16)
        self.main_layout.setSpacing(12)

        # Title row
        title_row = QHBoxLayout()
        self.detail_title = QLabel(self.lang_manager.get_text("admin_user_details"))
        self.detail_title.setObjectName("UserDetailTitle")
        self.status_badge = StatusBadge("ACTIVE")
        self.status_badge.setObjectName("UserStatusBadge")
        title_row.addWidget(self.detail_title)
        title_row.addStretch()
        title_row.addWidget(self.status_badge)
        self.main_layout.addLayout(title_row)

        # Info grid
        self.info_container = QWidget()
        self.info_container.setObjectName("UserInfoContainer")
        info_grid = QGridLayout(self.info_container)
        info_grid.setContentsMargins(0, 0, 0, 0)
        info_grid.setSpacing(8)
        info_grid.setColumnStretch(1, 1)
        info_grid.setColumnStretch(3, 1)

        # Row 0
        self.lbl_username_key = QLabel(self.lang_manager.get_text("username"))
        self.lbl_username_val = QLabel("—")
        self.lbl_phone_key = QLabel(self.lang_manager.get_text("phone"))
        self.lbl_phone_val = QLabel("—")

        info_grid.addWidget(self.lbl_username_key, 0, 0)
        info_grid.addWidget(self.lbl_username_val, 0, 1)
        info_grid.addWidget(self.lbl_phone_key, 0, 2)
        info_grid.addWidget(self.lbl_phone_val, 0, 3)

        # Row 1
        self.lbl_accnum_key = QLabel(self.lang_manager.get_text("acc_number"))
        self.lbl_accnum_val = QLabel("—")
        self.lbl_balance_key = QLabel(self.lang_manager.get_text("total_balance"))
        self.lbl_balance_val = QLabel("—")

        info_grid.addWidget(self.lbl_accnum_key, 1, 0)
        info_grid.addWidget(self.lbl_accnum_val, 1, 1)
        info_grid.addWidget(self.lbl_balance_key, 1, 2)
        info_grid.addWidget(self.lbl_balance_val, 1, 3)

        # Row 2
        self.lbl_tier_key = QLabel("Tier")
        self.lbl_tier_val = QLabel("—")
        self.lbl_joined_key = QLabel(self.lang_manager.get_text("member_since"))
        self.lbl_joined_val = QLabel("—")

        info_grid.addWidget(self.lbl_tier_key, 2, 0)
        info_grid.addWidget(self.lbl_tier_val, 2, 1)
        info_grid.addWidget(self.lbl_joined_key, 2, 2)
        info_grid.addWidget(self.lbl_joined_val, 2, 3)

        # Row 3
        self.lbl_lastlogin_key = QLabel(self.lang_manager.get_text("admin_last_login"))
        self.lbl_lastlogin_val = QLabel("—")
        self.lbl_email_key = QLabel(self.lang_manager.get_text("email"))
        self.lbl_email_val = QLabel("—")

        info_grid.addWidget(self.lbl_lastlogin_key, 3, 0)
        info_grid.addWidget(self.lbl_lastlogin_val, 3, 1)
        info_grid.addWidget(self.lbl_email_key, 3, 2)
        info_grid.addWidget(self.lbl_email_val, 3, 3)

        self.main_layout.addWidget(self.info_container)

        # Action buttons row
        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)

        self.btn_freeze = QPushButton(f"🧊  {self.lang_manager.get_text('admin_freeze')}")
        self.btn_freeze.setObjectName("BtnFreeze")
        self.btn_freeze.setFixedHeight(36)
        self.btn_freeze.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_freeze.clicked.connect(self._on_freeze)

        self.btn_unfreeze = QPushButton(f"🔓  {self.lang_manager.get_text('admin_unfreeze')}")
        self.btn_unfreeze.setObjectName("BtnUnfreeze")
        self.btn_unfreeze.setFixedHeight(36)
        self.btn_unfreeze.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_unfreeze.clicked.connect(self._on_unfreeze)

        self.btn_suspend = QPushButton(f"⛔  {self.lang_manager.get_text('admin_suspend')}")
        self.btn_suspend.setObjectName("BtnSuspend")
        self.btn_suspend.setFixedHeight(36)
        self.btn_suspend.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suspend.clicked.connect(self._on_suspend)

        # Tier controls
        self.tier_combo = QComboBox()
        self.tier_combo.setObjectName("TierCombo")
        self.tier_combo.addItems(["STANDARD", "GOLD", "DIAMOND"])
        self.tier_combo.setFixedHeight(36)
        self.tier_combo.setFixedWidth(130)

        self.btn_set_tier = QPushButton(f"🏆  {self.lang_manager.get_text('admin_set_tier')}")
        self.btn_set_tier.setObjectName("BtnSetTier")
        self.btn_set_tier.setFixedHeight(36)
        self.btn_set_tier.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_set_tier.clicked.connect(self._on_set_tier)

        actions_row.addWidget(self.btn_freeze)
        actions_row.addWidget(self.btn_unfreeze)
        actions_row.addWidget(self.btn_suspend)
        actions_row.addStretch()
        actions_row.addWidget(self.tier_combo)
        actions_row.addWidget(self.btn_set_tier)

        self.main_layout.addLayout(actions_row)

        # Empty state label
        self.empty_label = QLabel(self.lang_manager.get_text("admin_select_user"))
        self.empty_label.setObjectName("UserDetailEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.empty_label)

    def _show_empty_state(self):
        """Show the 'select a user' placeholder."""
        self.info_container.setVisible(False)
        self.btn_freeze.setVisible(False)
        self.btn_unfreeze.setVisible(False)
        self.btn_suspend.setVisible(False)
        self.tier_combo.setVisible(False)
        self.btn_set_tier.setVisible(False)
        self.status_badge.setVisible(False)
        self.empty_label.setVisible(True)
        self.detail_title.setText(self.lang_manager.get_text("admin_user_details"))

    def load_user(self, username):
        """Load and display a user's details by username."""
        user = AdminUserService.get_user_by_username(username)
        if not user:
            self._show_empty_state()
            return

        self._current_user = user
        self.empty_label.setVisible(False)
        self.info_container.setVisible(True)
        self.status_badge.setVisible(True)

        # Populate fields
        self.lbl_username_val.setText(safe_text(user.get("username")))
        self.lbl_phone_val.setText(safe_text(user.get("phone")))
        self.lbl_accnum_val.setText(safe_text(user.get("account_number")))
        self.lbl_balance_val.setText(safe_currency(user.get("balance")))
        
        tier = safe_text(user.get("customer_tier"), "STANDARD")
        self.lbl_tier_val.setText(tier)

        status = safe_text(user.get("account_status"), "ACTIVE")
        self.status_badge.set_status(status)

        joined = safe_text(user.get("created_at"), "Unknown")
        self.lbl_joined_val.setText(str(joined)[:16])

        last_login = user.get("last_login")
        self.lbl_lastlogin_val.setText(str(last_login)[:16] if last_login else "Never")

        self.lbl_email_val.setText(safe_text(user.get("email"), "N/A"))

        self.detail_title.setText(f"{self.lang_manager.get_text('admin_user_details')} — {user.get('username')}")

        # Update tier combo to current tier
        tier_index = self.tier_combo.findText(tier)
        if tier_index >= 0:
            self.tier_combo.setCurrentIndex(tier_index)

        # Show/hide action buttons based on status and username
        is_admin = user.get("username", "").lower() == "admin"
        self.btn_freeze.setVisible(not is_admin and status == "ACTIVE")
        self.btn_unfreeze.setVisible(not is_admin and status in ("FROZEN", "SUSPENDED"))
        self.btn_suspend.setVisible(not is_admin and status != "SUSPENDED")
        self.tier_combo.setVisible(not is_admin)
        self.btn_set_tier.setVisible(not is_admin)

        self.update_theme()

    def _confirm_action(self, title, message):
        """Show confirmation dialog. Returns True if user confirms."""
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def _show_result(self, success, message):
        """Show result message box."""
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)

    def _on_freeze(self):
        if not self._current_user:
            return
        username = self._current_user["username"]
        if not self._confirm_action(
            self.lang_manager.get_text("admin_confirm_freeze_title"),
            self.lang_manager.get_text("admin_confirm_freeze").replace("{user}", username)
        ):
            return
        success, msg = AdminUserService.update_account_status(username, "FROZEN")
        self._show_result(success, msg)
        if success:
            self.load_user(username)
            self.user_action_completed.emit()

    def _on_unfreeze(self):
        if not self._current_user:
            return
        username = self._current_user["username"]
        if not self._confirm_action(
            self.lang_manager.get_text("admin_confirm_unfreeze_title"),
            self.lang_manager.get_text("admin_confirm_unfreeze").replace("{user}", username)
        ):
            return
        success, msg = AdminUserService.update_account_status(username, "ACTIVE")
        self._show_result(success, msg)
        if success:
            self.load_user(username)
            self.user_action_completed.emit()

    def _on_suspend(self):
        if not self._current_user:
            return
        username = self._current_user["username"]
        if not self._confirm_action(
            self.lang_manager.get_text("admin_confirm_suspend_title"),
            self.lang_manager.get_text("admin_confirm_suspend").replace("{user}", username)
        ):
            return

        sec_dialog = AdminSecurityDialog(self, f"suspend user {username}")
        if sec_dialog.exec() == QDialog.DialogCode.Accepted:
            if not AuthService.login_user("admin", sec_dialog.get_password()):
                QMessageBox.critical(self, "Security Error", "Invalid admin password.")
                return
        else:
            return

        success, msg = AdminUserService.update_account_status(username, "SUSPENDED")
        self._show_result(success, msg)
        if success:
            self.load_user(username)
            self.user_action_completed.emit()

    def _on_set_tier(self):
        if not self._current_user:
            return
        username = self._current_user["username"]
        new_tier = self.tier_combo.currentText()
        current_tier = self._current_user.get("customer_tier", "STANDARD")

        if new_tier == current_tier:
            QMessageBox.information(self, "Info", f"User is already {current_tier}.")
            return

        if not self._confirm_action(
            self.lang_manager.get_text("admin_confirm_tier_title"),
            self.lang_manager.get_text("admin_confirm_tier").replace("{user}", username).replace("{tier}", new_tier)
        ):
            return
        success, msg = AdminUserService.update_user_tier(username, new_tier)
        self._show_result(success, msg)
        if success:
            self.load_user(username)
            self.user_action_completed.emit()

    def update_theme(self):
        theme.update_globals()

        self.setStyleSheet(f"""
            AdminUserDetailCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 10px;
            }}
        """)

        self.detail_title.setStyleSheet(f"""
            color: {theme.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: 700;
            border: none;
            background: transparent;
        """)

        self.empty_label.setStyleSheet(f"""
            color: {theme.TEXT_SECONDARY};
            font-size: 13px;
            font-weight: 500;
            border: none;
            background: transparent;
        """)

        # Info keys style
        key_style = f"""
            color: {theme.TEXT_SECONDARY};
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.3px;
            border: none;
            background: transparent;
        """
        for lbl in [self.lbl_username_key, self.lbl_phone_key, self.lbl_accnum_key,
                     self.lbl_balance_key, self.lbl_tier_key, self.lbl_joined_key,
                     self.lbl_lastlogin_key, self.lbl_email_key]:
            lbl.setStyleSheet(key_style)

        # Info values style
        val_style = f"""
            color: {theme.TEXT_PRIMARY};
            font-size: 13px;
            font-weight: 600;
            border: none;
            background: transparent;
        """
        for lbl in [self.lbl_username_val, self.lbl_phone_val, self.lbl_accnum_val,
                     self.lbl_balance_val, self.lbl_joined_val, self.lbl_lastlogin_val,
                     self.lbl_email_val]:
            lbl.setStyleSheet(val_style)

        # Tier value gets special color
        if self._current_user:
            tier = self._current_user.get("customer_tier", "STANDARD")
            tier_colors = {"DIAMOND": theme.CYAN, "GOLD": "#D4AF37", "STANDARD": theme.TEXT_SECONDARY}
            self.lbl_tier_val.setStyleSheet(f"""
                color: {tier_colors.get(tier, theme.TEXT_SECONDARY)};
                font-size: 13px;
                font-weight: 700;
                border: none;
                background: transparent;
            """)

        # Status badge
        self.status_badge.update_style()

        # Action button styles
        action_btn = f"""
            QPushButton {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border: 1px solid {theme.CYAN};
                color: {theme.CYAN};
            }}
        """
        self.btn_freeze.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.PANEL_BG};
                color: {theme.ORANGE};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.ORANGE};
                color: white;
                border: 1px solid {theme.ORANGE};
            }}
        """)

        self.btn_unfreeze.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.PANEL_BG};
                color: {theme.GREEN};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.GREEN};
                color: white;
                border: 1px solid {theme.GREEN};
            }}
        """)

        self.btn_suspend.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.PANEL_BG};
                color: {theme.RED};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.RED};
                color: white;
                border: 1px solid {theme.RED};
            }}
        """)

        self.btn_set_tier.setStyleSheet(action_btn)

        self.tier_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                padding: 0 10px;
                font-size: 12px;
            }}
            QComboBox:hover {{
                border: 1px solid {theme.CYAN};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme.CARD_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                selection-background-color: {theme.PANEL_BG};
                selection-color: {theme.CYAN};
            }}
        """)

    def update_translations(self):
        self.lbl_username_key.setText(self.lang_manager.get_text("username"))
        self.lbl_phone_key.setText(self.lang_manager.get_text("phone"))
        self.lbl_accnum_key.setText(self.lang_manager.get_text("acc_number"))
        self.lbl_balance_key.setText(self.lang_manager.get_text("total_balance"))
        self.lbl_tier_key.setText("Tier")
        self.lbl_joined_key.setText(self.lang_manager.get_text("member_since"))
        self.lbl_lastlogin_key.setText(self.lang_manager.get_text("admin_last_login"))
        self.lbl_email_key.setText(self.lang_manager.get_text("email"))
        self.btn_freeze.setText(f"🧊  {self.lang_manager.get_text('admin_freeze')}")
        self.btn_unfreeze.setText(f"🔓  {self.lang_manager.get_text('admin_unfreeze')}")
        self.btn_suspend.setText(f"⛔  {self.lang_manager.get_text('admin_suspend')}")
        self.btn_set_tier.setText(f"🏆  {self.lang_manager.get_text('admin_set_tier')}")
        self.empty_label.setText(self.lang_manager.get_text("admin_select_user"))
        if not self._current_user:
            self.detail_title.setText(self.lang_manager.get_text("admin_user_details"))
