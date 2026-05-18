"""Admin Security Center Tab — Full Security Operations Center dashboard.

Layout:
┌──────────────────────────────────────────────────────────┐
│ Security Overview Cards (4)                              │
├──────────────────────────────────────────────────────────┤
│ Suspicious Activity Alerts                               │
├──────────────────────────────────────────────────────────┤
│ Active Sessions Panel                                    │
├──────────────────────────────────────────────────────────┤
│ Login History Table                                      │
├──────────────────────────────────────────────────────────┤
│ Admin Activity Logs Table                                │
└──────────────────────────────────────────────────────────┘
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QPushButton, QSizePolicy, QComboBox,
    QLineEdit, QTextEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QColor, QFont, QDesktopServices
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.admin.components.admin_stat_card import AdminStatCard
from src.admin.components.security_alert_card import SecurityAlertCard
from src.admin.components.session_card import SessionCard
from src.admin.services.security_service import SecurityService
from src.admin.services.notification_service import AdminNotificationService
from src.admin.components.notification_history_card import NotificationHistoryCard
from src.admin.services.backup_service import BackupService
from src.admin.components.backup_card import BackupCard
from src.admin.components.system_tool_card import SystemToolCard
from src.admin.dialogs.admin_security_dialog import AdminSecurityDialog
from src.services.auth_service import AuthService

class AdminSettingsTab(QWidget):
    """Admin Security Center (formerly Settings tab) — SOC-style dashboard."""

    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setObjectName("AdminSettingsTab")
        self._setup_ui()
        self.update_theme()

    # ─── UI Setup ─────────────────────────────────────────────────────

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setObjectName("AdminSettingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("AdminSettingsContent")
        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(28, 24, 28, 24)
        self.main_layout.setSpacing(20)

        # ── Top Bar: Title + Logout ──
        top_bar = QHBoxLayout()

        self.page_icon = QLabel("🛡️")
        self.page_icon.setObjectName("AdminSettingsPageIcon")
        self.page_icon.setFixedSize(28, 28)
        top_bar.addWidget(self.page_icon)

        self.page_title = QLabel(self.lang_manager.get_text("admin_security_center_title"))
        self.page_title.setObjectName("AdminSettingsPageTitle")
        title_font = QFont("Segoe UI", 16)
        title_font.setBold(True)
        self.page_title.setFont(title_font)
        top_bar.addWidget(self.page_title)

        top_bar.addStretch()

        self.refresh_btn = QPushButton("🔄 " + self.lang_manager.get_text("admin_refresh"))
        self.refresh_btn.setObjectName("AdminSettingsRefreshBtn")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setFixedHeight(32)
        self.refresh_btn.clicked.connect(self.load_data)
        top_bar.addWidget(self.refresh_btn)

        self.logout_btn = QPushButton("🚪 " + self.lang_manager.get_text("logout"))
        self.logout_btn.setObjectName("AdminSettingsLogoutBtn")
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setFixedHeight(32)
        top_bar.addWidget(self.logout_btn)

        self.main_layout.addLayout(top_bar)

        # ── Section 0: System Settings ──
        self._build_system_settings_section()

        # ── Section 0.1: Create Announcement ──
        self._build_announcement_section()

        # ── Section 0.2: Announcement History ──
        self._build_announcement_history_section()

        # ── Section 0.3: System Tools & Database Management ──
        self._build_system_tools_section()

        # ── Section 1: Security Overview Cards ──
        self._build_overview_section()

        # ── Section 2: Security Alerts ──
        self._build_alerts_section()

        # ── Section 3: Active Sessions Panel ──
        self._build_sessions_section()

        # ── Section 4: Login History Table ──
        self._build_history_section()

        # ── Section 5: Admin Activity Logs ──
        self._build_logs_section()

        self.main_layout.addStretch()

        scroll.setWidget(content)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def _build_section_header(self, icon, text_key, extra_widgets=None):
        """Create a consistent section header with icon + title + optional buttons."""
        header = QHBoxLayout()
        header.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedWidth(20)
        header.addWidget(icon_lbl)

        title_lbl = QLabel(self.lang_manager.get_text(text_key))
        font = QFont("Segoe UI", 14)
        font.setBold(True)
        title_lbl.setFont(font)
        header.addWidget(title_lbl)
        header.addStretch()

        if extra_widgets:
            for w in extra_widgets:
                header.addWidget(w)

        self.main_layout.addLayout(header)
        return icon_lbl, title_lbl

    # ── Section Builders ──────────────────────────────────────────────

    def _build_system_settings_section(self):
        self.sys_icon, self.sys_title = self._build_section_header(
            "⚙️", "admin_system_settings"
        )

        self.sys_frame = QFrame()
        self.sys_frame.setObjectName("AdminSystemSettingsFrame")
        self.sys_frame.setMinimumHeight(80)
        sys_layout = QHBoxLayout(self.sys_frame)
        sys_layout.setContentsMargins(20, 16, 20, 16)
        sys_layout.setSpacing(24)

        # Theme Selector
        theme_layout = QVBoxLayout()
        theme_layout.setSpacing(8)
        self.theme_label = QLabel(self.lang_manager.get_text("theme_mode"))
        self.theme_label.setObjectName("AdminThemeLabel")
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("AdminThemeCombo")
        self.theme_combo.addItems([
            self.lang_manager.get_text("dark_mode"),
            self.lang_manager.get_text("light_mode")
        ])
        if self.theme_manager.current_theme == "light":
            self.theme_combo.setCurrentIndex(1)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        
        theme_layout.addWidget(self.theme_label)
        theme_layout.addWidget(self.theme_combo)

        # Language Selector
        lang_layout = QVBoxLayout()
        lang_layout.setSpacing(8)
        self.lang_label = QLabel(self.lang_manager.get_text("language"))
        self.lang_label.setObjectName("AdminLangLabel")
        self.lang_combo = QComboBox()
        self.lang_combo.setObjectName("AdminLangCombo")
        self.lang_combo.addItems(["English", "Tiếng Việt"])
        if self.lang_manager.current_language == "vi":
            self.lang_combo.setCurrentIndex(1)
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)

        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_combo)

        sys_layout.addLayout(theme_layout)
        sys_layout.addLayout(lang_layout)
        sys_layout.addStretch()

        self.main_layout.addWidget(self.sys_frame)

    def _on_theme_changed(self, index):
        theme_name = "light" if index == 1 else "dark"
        self.theme_manager.set_theme(theme_name)

    def _on_language_changed(self, index):
        lang_code = "vi" if index == 1 else "en"
        self.lang_manager.set_language(lang_code)

    def _build_announcement_section(self):
        self.ann_icon, self.ann_title = self._build_section_header(
            "📢", "admin_create_announcement"
        )

        self.ann_frame = QFrame()
        self.ann_frame.setObjectName("AdminAnnouncementFrame")
        ann_layout = QVBoxLayout(self.ann_frame)
        ann_layout.setContentsMargins(20, 16, 20, 16)
        ann_layout.setSpacing(12)

        # Title input
        self.ann_title_input = QLineEdit()
        self.ann_title_input.setObjectName("AnnTitleInput")
        self.ann_title_input.setPlaceholderText(self.lang_manager.get_text("admin_ann_title_placeholder"))
        self.ann_title_input.setFixedHeight(36)
        ann_layout.addWidget(self.ann_title_input)

        # Message input
        self.ann_msg_input = QTextEdit()
        self.ann_msg_input.setObjectName("AnnMsgInput")
        self.ann_msg_input.setPlaceholderText(self.lang_manager.get_text("admin_ann_msg_placeholder"))
        self.ann_msg_input.setFixedHeight(80)
        ann_layout.addWidget(self.ann_msg_input)

        # Controls row
        controls_row = QHBoxLayout()
        controls_row.setSpacing(12)

        # Type Combo
        self.ann_type_combo = QComboBox()
        self.ann_type_combo.setObjectName("AnnTypeCombo")
        self.ann_type_combo.addItems(["INFO", "WARNING", "SECURITY", "MAINTENANCE", "PROMOTION"])
        self.ann_type_combo.setFixedHeight(36)

        # Priority Combo
        self.ann_priority_combo = QComboBox()
        self.ann_priority_combo.setObjectName("AnnPriorityCombo")
        self.ann_priority_combo.addItems(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        self.ann_priority_combo.setFixedHeight(36)

        # Target Combo
        self.ann_target_combo = QComboBox()
        self.ann_target_combo.setObjectName("AnnTargetCombo")
        self.ann_target_combo.addItems(["ALL_USERS", "STANDARD_USERS", "GOLD_USERS", "DIAMOND_USERS", "ADMIN_ONLY"])
        self.ann_target_combo.setFixedHeight(36)

        controls_row.addWidget(self.ann_type_combo)
        controls_row.addWidget(self.ann_priority_combo)
        controls_row.addWidget(self.ann_target_combo)
        controls_row.addStretch()

        # Action Buttons
        self.ann_clear_btn = QPushButton(self.lang_manager.get_text("admin_ann_clear"))
        self.ann_clear_btn.setObjectName("AnnClearBtn")
        self.ann_clear_btn.setFixedHeight(36)
        self.ann_clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ann_clear_btn.clicked.connect(self._clear_announcement_form)
        controls_row.addWidget(self.ann_clear_btn)

        self.ann_send_btn = QPushButton("🚀 " + self.lang_manager.get_text("admin_ann_send"))
        self.ann_send_btn.setObjectName("AnnSendBtn")
        self.ann_send_btn.setFixedHeight(36)
        self.ann_send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ann_send_btn.clicked.connect(self._handle_send_announcement)
        controls_row.addWidget(self.ann_send_btn)

        ann_layout.addLayout(controls_row)
        self.main_layout.addWidget(self.ann_frame)

    def _build_announcement_history_section(self):
        self.ann_hist_icon, self.ann_hist_title = self._build_section_header(
            "📜", "admin_notification_history"
        )

        self.ann_hist_frame = QFrame()
        self.ann_hist_frame.setObjectName("AdminAnnHistFrame")
        self.ann_hist_frame.setMinimumHeight(60)
        ann_hist_layout = QVBoxLayout(self.ann_hist_frame)
        ann_hist_layout.setContentsMargins(8, 8, 8, 8)
        ann_hist_layout.setSpacing(8)

        self.ann_hist_container = QVBoxLayout()
        self.ann_hist_container.setSpacing(8)
        ann_hist_layout.addLayout(self.ann_hist_container)

        self.main_layout.addWidget(self.ann_hist_frame)

    def _clear_announcement_form(self):
        self.ann_title_input.clear()
        self.ann_msg_input.clear()
        self.ann_type_combo.setCurrentIndex(0)
        self.ann_priority_combo.setCurrentIndex(0)
        self.ann_target_combo.setCurrentIndex(0)

    def _handle_send_announcement(self):
        title = self.ann_title_input.text().strip()
        message = self.ann_msg_input.toPlainText().strip()
        n_type = self.ann_type_combo.currentText()
        priority = self.ann_priority_combo.currentText()
        target = self.ann_target_combo.currentText()

        if not title or not message:
            QMessageBox.warning(self, "Validation Error", "Title and Message are required.")
            return

        success = AdminNotificationService.create_notification(
            title=title, message=message, n_type=n_type, priority=priority, target=target
        )

        if success:
            QMessageBox.information(self, "Success", "Announcement broadcasted successfully.")
            self._clear_announcement_form()
            self.load_data()  # Refresh history
        else:
            QMessageBox.critical(self, "Error", "Failed to send announcement.")

    def _build_system_tools_section(self):
        self.tools_icon, self.tools_title = self._build_section_header(
            "🧰", "admin_system_tools_title"
        )

        # 1. Backup Card
        self.backup_card = BackupCard()
        self.backup_card.create_requested.connect(self._handle_create_backup)
        self.backup_card.restore_requested.connect(self._handle_restore_backup)
        self.backup_card.open_folder_requested.connect(self._handle_open_backup_folder)
        self.main_layout.addWidget(self.backup_card)

        # 2. Tools Grid
        tools_grid = QGridLayout()
        tools_grid.setSpacing(12)

        self.cleanup_card = SystemToolCard(
            title=self.lang_manager.get_text("admin_tool_cleanup_title"),
            description=self.lang_manager.get_text("admin_tool_cleanup_desc"),
            icon_str="🧹",
            btn_text=self.lang_manager.get_text("admin_btn_cleanup")
        )
        self.cleanup_card.action_requested.connect(self._handle_cleanup)

        self.export_card = SystemToolCard(
            title=self.lang_manager.get_text("admin_tool_export_title"),
            description=self.lang_manager.get_text("admin_tool_export_desc"),
            icon_str="📥",
            btn_text=self.lang_manager.get_text("admin_btn_export")
        )
        self.export_card.action_requested.connect(self._handle_export_logs)

        self.maintenance_card = SystemToolCard(
            title=self.lang_manager.get_text("admin_tool_maintenance_title"),
            description=self.lang_manager.get_text("admin_tool_maintenance_desc"),
            icon_str="🚧",
            btn_text=self.lang_manager.get_text("admin_btn_toggle_maintenance"),
            is_danger=True
        )
        self.maintenance_card.action_requested.connect(self._handle_toggle_maintenance)

        tools_grid.addWidget(self.cleanup_card, 0, 0)
        tools_grid.addWidget(self.export_card, 0, 1)
        tools_grid.addWidget(self.maintenance_card, 1, 0, 1, 2) # spans 2 cols

        self.main_layout.addLayout(tools_grid)

    def _handle_create_backup(self):
        success, msg = BackupService.create_backup("admin")
        if success:
            QMessageBox.information(self, "Success", msg)
            self._load_backup_data()
        else:
            QMessageBox.critical(self, "Error", msg)

    def _handle_restore_backup(self):
        # Open file dialog to select backup
        backup_dir = os.path.abspath(BackupService.BACKUP_DIR)
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup File",
            backup_dir,
            "SQLite Database (*.db);;All Files (*)"
        )
        if not file_path:
            return

        filename = os.path.basename(file_path)
        
        reply = QMessageBox.warning(
            self, "Restore Database",
            f"Restoring '{filename}' will overwrite the current database data.\n\nA safety backup will be created first.\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            sec_dialog = AdminSecurityDialog(self, "restore the database")
            if sec_dialog.exec() == QDialog.DialogCode.Accepted:
                if not AuthService.login_user("admin", sec_dialog.get_password()):
                    QMessageBox.critical(self, "Security Error", "Invalid admin password.")
                    return
            else:
                return

            success, msg = BackupService.restore_backup(filename, "admin")
            if success:
                QMessageBox.information(self, "Restore Successful", msg)
                self.load_data()
            else:
                QMessageBox.critical(self, "Restore Failed", msg)

    def _handle_open_backup_folder(self):
        BackupService._ensure_dirs()
        backup_dir = os.path.abspath(BackupService.BACKUP_DIR)
        QDesktopServices.openUrl(QUrl.fromLocalFile(backup_dir))

    def _handle_cleanup(self):
        reply = QMessageBox.question(
            self, "System Cleanup",
            "This will delete expired temporary files (like verification TXTs) and clean up old database records. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            sec_dialog = AdminSecurityDialog(self, "run system cleanup")
            if sec_dialog.exec() == QDialog.DialogCode.Accepted:
                if not AuthService.login_user("admin", sec_dialog.get_password()):
                    QMessageBox.critical(self, "Security Error", "Invalid admin password.")
                    return
            else:
                return

            success, msg = BackupService.cleanup_temp_files("admin")
            if success:
                QMessageBox.information(self, "Cleanup Complete", msg)
            else:
                QMessageBox.warning(self, "Cleanup Failed", msg)

    def _handle_export_logs(self):
        success, msg = BackupService.export_logs(log_type="security", format="csv", admin_username="admin")
        if success:
            QMessageBox.information(self, "Export Complete", msg)
        else:
            QMessageBox.warning(self, "Export Failed", msg)

    def _handle_toggle_maintenance(self):
        reply = QMessageBox.warning(
            self, "Toggle Maintenance Mode",
            "This will toggle emergency maintenance mode. When active, users cannot log in or transfer money. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            sec_dialog = AdminSecurityDialog(self, "toggle maintenance mode")
            if sec_dialog.exec() == QDialog.DialogCode.Accepted:
                if not AuthService.login_user("admin", sec_dialog.get_password()):
                    QMessageBox.critical(self, "Security Error", "Invalid admin password.")
                    return
            else:
                return

            success, msg = BackupService.toggle_maintenance_mode("admin")
            if success:
                QMessageBox.information(self, "Maintenance Mode", msg)
                self._load_maintenance_state()
            else:
                QMessageBox.critical(self, "Error", msg)

    def _load_maintenance_state(self):
        is_active = BackupService.get_maintenance_mode()
        if is_active:
            self.maintenance_card.desc_lbl.setText(self.lang_manager.get_text("admin_maintenance_active"))
        else:
            self.maintenance_card.desc_lbl.setText(self.lang_manager.get_text("admin_tool_maintenance_desc"))

    def _load_backup_data(self):
        backups = BackupService.get_backup_history()
        count = len(backups)
        if count > 0:
            last = backups[0]
            self.backup_card.update_data(last["created_at"], f"{last['size_mb']} MB", count)
        else:
            self.backup_card.update_data("Never", "0 MB", 0)

    def _build_overview_section(self):
        self.overview_icon, self.overview_title = self._build_section_header(
            "📊", "admin_security_overview"
        )

        cards_grid = QGridLayout()
        cards_grid.setSpacing(12)

        self.card_active = AdminStatCard(
            title="Active Sessions", value="0",
            trend_text="Current online", icon="🔒",
            accent_color=theme.CYAN
        )
        self.card_failed = AdminStatCard(
            title="Failed Logins", value="0",
            trend_text="Today: 0", icon="❌",
            accent_color=theme.ORANGE
        )
        self.card_suspicious = AdminStatCard(
            title="Suspicious", value="0",
            trend_text="Detected alerts", icon="⚠️",
            accent_color=theme.RED
        )
        self.card_frozen = AdminStatCard(
            title="Restricted Accounts", value="0",
            trend_text="Frozen / Suspended", icon="❄️",
            accent_color=theme.TEXT_SECONDARY
        )

        cards_grid.addWidget(self.card_active, 0, 0)
        cards_grid.addWidget(self.card_failed, 0, 1)
        cards_grid.addWidget(self.card_suspicious, 0, 2)
        cards_grid.addWidget(self.card_frozen, 0, 3)
        self.main_layout.addLayout(cards_grid)

    def _build_alerts_section(self):
        self.alerts_icon, self.alerts_title = self._build_section_header(
            "🚨", "admin_security_alerts"
        )

        # Container frame for alerts
        self.alerts_frame = QFrame()
        self.alerts_frame.setMinimumHeight(40)
        alerts_frame_layout = QVBoxLayout(self.alerts_frame)
        alerts_frame_layout.setContentsMargins(0, 0, 0, 0)
        alerts_frame_layout.setSpacing(8)

        self.alerts_container = QVBoxLayout()
        self.alerts_container.setSpacing(8)
        alerts_frame_layout.addLayout(self.alerts_container)

        self.main_layout.addWidget(self.alerts_frame)

    def _build_sessions_section(self):
        # "End All Sessions" button in header
        self.end_all_btn = QPushButton("⏹ End All")
        self.end_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.end_all_btn.setFixedHeight(28)
        self.end_all_btn.setFixedWidth(100)
        self.end_all_btn.clicked.connect(self._handle_terminate_all)

        self.sessions_icon, self.sessions_title = self._build_section_header(
            "🖥️", "admin_active_sessions", extra_widgets=[self.end_all_btn]
        )

        # Container for session cards
        self.sessions_frame = QFrame()
        self.sessions_frame.setMinimumHeight(40)
        sessions_frame_layout = QVBoxLayout(self.sessions_frame)
        sessions_frame_layout.setContentsMargins(0, 0, 0, 0)
        sessions_frame_layout.setSpacing(8)

        self.sessions_container = QVBoxLayout()
        self.sessions_container.setSpacing(8)
        sessions_frame_layout.addLayout(self.sessions_container)

        self.main_layout.addWidget(self.sessions_frame)

    def _build_history_section(self):
        self.history_icon, self.history_title = self._build_section_header(
            "📋", "admin_login_history"
        )

        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels([
            "Username", "Time", "Status", "Device", "Location"
        ])
        self._setup_table(self.history_table)
        self.main_layout.addWidget(self.history_table)

    def _build_logs_section(self):
        self.logs_icon, self.logs_title = self._build_section_header(
            "📝", "admin_activity_logs"
        )

        self.logs_table = QTableWidget(0, 4)
        self.logs_table.setHorizontalHeaderLabels([
            "Admin", "Action", "Target", "Time"
        ])
        self._setup_table(self.logs_table)
        self.main_layout.addWidget(self.logs_table)

    # ─── Table Setup ──────────────────────────────────────────────────

    def _setup_table(self, table):
        """Common enterprise styling for security tables."""
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setMinimumHeight(180)
        table.setMaximumHeight(320)
        table.setAlternatingRowColors(True)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        header.setMinimumSectionSize(80)

        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    # ─── Data Loading ─────────────────────────────────────────────────

    def load_data(self):
        """Fetch all security data and populate UI. Safe with try/except."""
        try:
            self._load_backup_data()
            self._load_maintenance_state()
            self._load_announcement_history()
            self._load_overview_stats()
            self._load_alerts()
            self._load_sessions()
            self._load_history()
            self._load_logs()
        except Exception as e:
            print(f"Security Center load_data error: {e}")

    def _load_announcement_history(self):
        self._clear_layout(self.ann_hist_container)
        history = AdminNotificationService.get_notification_history(10)

        if not history:
            lbl = QLabel(self.lang_manager.get_text("admin_no_ann_history"))
            lbl.setStyleSheet(
                f"color: {theme.TEXT_SECONDARY}; font-size: 13px; "
                f"padding: 16px; background: transparent;"
            )
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ann_hist_container.addWidget(lbl)
        else:
            for item in history:
                try:
                    notif_id = item[0]
                    title = item[1]
                    n_type = item[2]
                    priority = item[3]
                    target = item[4]
                    time_str = str(item[5])[:16]
                    card = NotificationHistoryCard(
                        notif_id, title, n_type, priority, target, time_str
                    )
                    card.delete_requested.connect(self._handle_delete_announcement)
                    self.ann_hist_container.addWidget(card)
                except Exception as e:
                    print(f"Announcement history card error: {e}")

    def _handle_delete_announcement(self, notif_id):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this announcement?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            sec_dialog = AdminSecurityDialog(self, "delete an announcement")
            if sec_dialog.exec() == QDialog.DialogCode.Accepted:
                if not AuthService.login_user("admin", sec_dialog.get_password()):
                    QMessageBox.critical(self, "Security Error", "Invalid admin password.")
                    return
            else:
                return

            success = AdminNotificationService.delete_notification(notif_id)
            if success:
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete announcement.")

    def _load_overview_stats(self):
        stats = SecurityService.get_security_overview_stats()
        self.card_active.set_value(str(stats.get("active_sessions", 0)))
        self.card_active.set_trend("Current online")

        failed = stats.get("failed_logins", 0)
        failed_today = stats.get("failed_today", 0)
        self.card_failed.set_value(str(failed))
        self.card_failed.set_trend(f"Today: {failed_today}")

        self.card_frozen.set_value(str(stats.get("frozen_accounts", 0)))

    def _load_alerts(self):
        self._clear_layout(self.alerts_container)
        alerts = SecurityService.detect_suspicious_activity()
        self.card_suspicious.set_value(str(len(alerts)))

        if not alerts:
            lbl = QLabel(self.lang_manager.get_text("admin_no_alerts"))
            lbl.setStyleSheet(
                f"color: {theme.TEXT_SECONDARY}; font-size: 13px; "
                f"padding: 16px; background: transparent;"
            )
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.alerts_container.addWidget(lbl)
        else:
            for alert in alerts:
                card = SecurityAlertCard(
                    alert.get("type", "WARNING"),
                    alert.get("title", ""),
                    alert.get("desc", "")
                )
                self.alerts_container.addWidget(card)

    def _load_sessions(self):
        self._clear_layout(self.sessions_container)
        sessions = SecurityService.get_active_sessions()

        if not sessions:
            lbl = QLabel(self.lang_manager.get_text("admin_no_sessions"))
            lbl.setStyleSheet(
                f"color: {theme.TEXT_SECONDARY}; font-size: 13px; "
                f"padding: 16px; background: transparent;"
            )
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sessions_container.addWidget(lbl)
        else:
            for sess in sessions:
                try:
                    sid = sess[0]
                    user = sess[1] if sess[1] else "Unknown"
                    created = sess[3] if len(sess) > 3 and sess[3] else ""
                    card = SessionCard(sid, user, created)
                    card.terminate_requested.connect(self._handle_terminate)
                    self.sessions_container.addWidget(card)
                except Exception as e:
                    print(f"Session card error: {e}")

    def _load_history(self):
        history = SecurityService.get_login_history(25)
        self._populate_history(history)

    def _load_logs(self):
        logs = SecurityService.get_admin_logs(25)
        self._populate_logs(logs)

    # ─── Session Actions ──────────────────────────────────────────────

    def _handle_terminate(self, session_id):
        """Terminate a single session and refresh."""
        try:
            SecurityService.terminate_session(session_id)
            SecurityService.log_admin_action(
                "admin", "TERMINATE_SESSION", f"SessionID:{session_id}"
            )
            self.load_data()
        except Exception as e:
            print(f"Terminate session error: {e}")

    def _handle_terminate_all(self):
        """Terminate all active sessions."""
        try:
            sessions = SecurityService.get_active_sessions()
            terminated_count = 0
            for sess in sessions:
                try:
                    sid = sess[0]
                    SecurityService.terminate_session(sid)
                    terminated_count += 1
                except Exception:
                    pass
            if terminated_count > 0:
                SecurityService.log_admin_action(
                    "admin", "TERMINATE_ALL_SESSIONS",
                    f"Terminated {terminated_count} session(s)"
                )
            self.load_data()
        except Exception as e:
            print(f"Terminate all sessions error: {e}")

    # ─── Layout Helpers ───────────────────────────────────────────────

    def _clear_layout(self, layout):
        """Safely remove all widgets from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # ─── Table Population ─────────────────────────────────────────────

    def _populate_history(self, history):
        """Fill the login history table with data."""
        if not history:
            self.history_table.setRowCount(1)
            item = QTableWidgetItem(self.lang_manager.get_text("admin_no_login_history"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(theme.TEXT_SECONDARY))
            self.history_table.setItem(0, 0, item)
            self.history_table.setSpan(0, 0, 1, 5)
            return

        self.history_table.clearSpans()
        self.history_table.setRowCount(len(history))

        for row, entry in enumerate(history):
            try:
                user = entry[0] if entry[0] else ""
                time_val = entry[1] if entry[1] else ""
                status = entry[2] if entry[2] else ""
                device = entry[3] if entry[3] else "Desktop App"
                location = entry[4] if entry[4] else "Local"

                self.history_table.setItem(row, 0, QTableWidgetItem(user))
                self.history_table.setItem(
                    row, 1, QTableWidgetItem(time_val[:19] if time_val else "")
                )

                # Status with color coding
                stat_item = QTableWidgetItem(status)
                if status == "SUCCESS":
                    stat_item.setForeground(QColor(theme.GREEN))
                elif status == "FAILED":
                    stat_item.setForeground(QColor(theme.ORANGE))
                elif status == "BLOCKED":
                    stat_item.setForeground(QColor(theme.RED))
                elif status == "ERROR":
                    stat_item.setForeground(QColor(theme.RED))
                self.history_table.setItem(row, 2, stat_item)

                self.history_table.setItem(row, 3, QTableWidgetItem(device))
                self.history_table.setItem(row, 4, QTableWidgetItem(location))
            except Exception as e:
                print(f"History row error: {e}")

    def _populate_logs(self, logs):
        """Fill the admin activity logs table with data."""
        if not logs:
            self.logs_table.setRowCount(1)
            item = QTableWidgetItem(self.lang_manager.get_text("admin_no_activity_logs"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(theme.TEXT_SECONDARY))
            self.logs_table.setItem(0, 0, item)
            self.logs_table.setSpan(0, 0, 1, 4)
            return

        self.logs_table.clearSpans()
        self.logs_table.setRowCount(len(logs))

        for row, entry in enumerate(logs):
            try:
                admin = entry[0] if entry[0] else ""
                action = entry[1] if entry[1] else ""
                target = entry[2] if entry[2] else ""
                time_val = entry[3] if entry[3] else ""

                self.logs_table.setItem(row, 0, QTableWidgetItem(admin))

                action_item = QTableWidgetItem(action)
                action_item.setForeground(QColor(theme.CYAN))
                self.logs_table.setItem(row, 1, action_item)

                self.logs_table.setItem(row, 2, QTableWidgetItem(target))
                self.logs_table.setItem(
                    row, 3, QTableWidgetItem(time_val[:19] if time_val else "")
                )
            except Exception as e:
                print(f"Logs row error: {e}")

    # ─── Theme ────────────────────────────────────────────────────────

    def update_theme(self):
        theme.update_globals()
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")

        # Page title
        self.page_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; background: transparent;")
        self.page_icon.setStyleSheet("background: transparent; border: none; font-size: 20px;")

        # Section headers
        section_title_style = (
            f"color: {theme.TEXT_PRIMARY}; background: transparent; border: none;"
        )
        section_icon_style = "background: transparent; border: none; font-size: 14px;"

        for lbl in [self.sys_title, self.tools_title, self.ann_title, self.ann_hist_title, self.overview_title, self.alerts_title,
                    self.sessions_title, self.history_title, self.logs_title]:
            lbl.setStyleSheet(section_title_style)

        for icon in [self.sys_icon, self.tools_icon, self.ann_icon, self.ann_hist_icon, self.overview_icon, self.alerts_icon,
                     self.sessions_icon, self.history_icon, self.logs_icon]:
            icon.setStyleSheet(section_icon_style)

        # Container frames
        for frame in [self.sys_frame, self.ann_frame, self.ann_hist_frame, self.alerts_frame, self.sessions_frame]:
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme.PANEL_BG};
                    border: 1px solid {theme.BORDER};
                    border-radius: 10px;
                    padding: 8px;
                }}
            """)

        self.backup_card.update_theme()
        self.cleanup_card.update_theme()
        self.export_card.update_theme()
        self.maintenance_card.update_theme()

        label_style = f"""
            color: {theme.TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 600;
            border: none;
            background: transparent;
        """
        self.theme_label.setStyleSheet(label_style)
        self.lang_label.setStyleSheet(label_style)

        input_style = f"""
            QLineEdit, QTextEdit {{
                background-color: {theme.CARD_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {theme.CYAN};
            }}
        """
        self.ann_title_input.setStyleSheet(input_style)
        self.ann_msg_input.setStyleSheet(input_style)

        combo_style = f"""
            QComboBox {{
                background-color: {theme.CARD_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
                min-width: 140px;
            }}
            QComboBox:hover {{
                border: 1px solid {theme.CYAN};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme.CARD_BG};
                color: {theme.TEXT_PRIMARY};
                selection-background-color: {theme.CYAN};
                selection-color: white;
            }}
        """
        self.theme_combo.setStyleSheet(combo_style)
        self.lang_combo.setStyleSheet(combo_style)
        self.ann_type_combo.setStyleSheet(combo_style)
        self.ann_priority_combo.setStyleSheet(combo_style)
        self.ann_target_combo.setStyleSheet(combo_style)

        # Tables
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
                padding: 6px 10px;
                border-bottom: 1px solid {theme.BORDER};
            }}
            QTableWidget::item:alternate {{
                background-color: {theme.PANEL_BG};
            }}
            QTableWidget::item:selected {{
                background-color: {theme.CYAN};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_SECONDARY};
                padding: 8px 10px;
                border: none;
                border-bottom: 2px solid {theme.BORDER};
                font-weight: bold;
                font-size: 11px;
            }}
        """
        self.history_table.setStyleSheet(table_style)
        self.logs_table.setStyleSheet(table_style)

        # Buttons
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.CARD_BG};
                color: {theme.RED};
                border: 1px solid {theme.RED};
                border-radius: 6px;
                padding: 0 16px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {theme.RED}; color: white;
            }}
        """)

        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.CARD_BG};
                color: {theme.CYAN};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                padding: 0 16px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {theme.CYAN}; color: white;
                border-color: {theme.CYAN};
            }}
        """)

        self.end_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.ORANGE};
                border: 1px solid {theme.ORANGE};
                border-radius: 6px;
                padding: 0 10px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {theme.ORANGE}; color: white;
            }}
        """)

        # Stat cards
        for card in [self.card_active, self.card_failed,
                     self.card_suspicious, self.card_frozen]:
            card.update_theme()

        # Child alert cards
        for i in range(self.alerts_container.count()):
            item = self.alerts_container.itemAt(i)
            if item and item.widget():
                w = item.widget()
                if hasattr(w, "update_theme"):
                    w.update_theme()

        # Child session cards
        for i in range(self.sessions_container.count()):
            item = self.sessions_container.itemAt(i)
            if item and item.widget():
                w = item.widget()
                if hasattr(w, "update_theme"):
                    w.update_theme()

    # ─── Translations ─────────────────────────────────────────────────

    def update_translations(self):
        self.page_title.setText(self.lang_manager.get_text("admin_security_center_title"))
        self.sys_title.setText(self.lang_manager.get_text("admin_system_settings"))
        self.tools_title.setText(self.lang_manager.get_text("admin_system_tools_title"))
        self.theme_label.setText(self.lang_manager.get_text("theme_mode"))
        self.theme_combo.setItemText(0, self.lang_manager.get_text("dark_mode"))
        self.theme_combo.setItemText(1, self.lang_manager.get_text("light_mode"))
        self.lang_label.setText(self.lang_manager.get_text("language"))
        
        # Tools translations
        self.backup_card.update_translations(self.lang_manager)
        self.cleanup_card.update_translations(
            self.lang_manager, "admin_tool_cleanup_title", "admin_tool_cleanup_desc", "admin_btn_cleanup"
        )
        self.export_card.update_translations(
            self.lang_manager, "admin_tool_export_title", "admin_tool_export_desc", "admin_btn_export"
        )
        self.maintenance_card.update_translations(
            self.lang_manager, "admin_tool_maintenance_title", "admin_tool_maintenance_desc", "admin_btn_toggle_maintenance"
        )
        self._load_maintenance_state()

        # Announcement translations
        self.ann_title.setText(self.lang_manager.get_text("admin_create_announcement"))
        self.ann_title_input.setPlaceholderText(self.lang_manager.get_text("admin_ann_title_placeholder"))
        self.ann_msg_input.setPlaceholderText(self.lang_manager.get_text("admin_ann_msg_placeholder"))
        self.ann_clear_btn.setText(self.lang_manager.get_text("admin_ann_clear"))
        self.ann_send_btn.setText("🚀 " + self.lang_manager.get_text("admin_ann_send"))
        self.ann_hist_title.setText(self.lang_manager.get_text("admin_notification_history"))

        self.overview_title.setText(self.lang_manager.get_text("admin_security_overview"))
        self.alerts_title.setText(self.lang_manager.get_text("admin_security_alerts"))
        self.sessions_title.setText(self.lang_manager.get_text("admin_active_sessions"))
        self.history_title.setText(self.lang_manager.get_text("admin_login_history"))
        self.logs_title.setText(self.lang_manager.get_text("admin_activity_logs"))
        self.logout_btn.setText("🚪 " + self.lang_manager.get_text("logout"))
        self.refresh_btn.setText("🔄 " + self.lang_manager.get_text("admin_refresh"))
        self.end_all_btn.setText("⏹ " + self.lang_manager.get_text("admin_end_all"))

        # Update table headers
        self.history_table.setHorizontalHeaderLabels([
            self.lang_manager.get_text("username"),
            self.lang_manager.get_text("admin_time"),
            self.lang_manager.get_text("admin_status"),
            self.lang_manager.get_text("admin_device"),
            self.lang_manager.get_text("admin_location"),
        ])
        self.logs_table.setHorizontalHeaderLabels([
            self.lang_manager.get_text("admin_admin_col"),
            self.lang_manager.get_text("admin_action_col"),
            self.lang_manager.get_text("admin_target_col"),
            self.lang_manager.get_text("admin_time"),
        ])

        # Refresh child translations
        for i in range(self.sessions_container.count()):
            item = self.sessions_container.itemAt(i)
            if item and item.widget() and hasattr(item.widget(), "update_translations"):
                item.widget().update_translations()

    # ─── Public API ───────────────────────────────────────────────────

    def update_ui(self):
        """Called when the tab becomes visible — refresh everything."""
        self.load_data()
        self.update_theme()
