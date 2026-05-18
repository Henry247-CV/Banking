"""Admin Security Center Tab — Replaces Settings tab with full security dashboard.

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

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.admin.components.admin_stat_card import AdminStatCard
from src.admin.components.security_alert_card import SecurityAlertCard
from src.admin.components.session_card import SessionCard
from src.admin.services.security_service import SecurityService


class AdminSettingsTab(QWidget):
    """Admin Security Center (formerly Settings tab)."""
    
    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self._setup_ui()
        self.update_theme()
        
    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(28, 24, 28, 24)
        self.main_layout.setSpacing(24)

        # ── Logout Header ──
        # Keeping a top right logout button since settings was replaced
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.logout_btn = QPushButton("🚪 Logout")
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setFixedHeight(32)
        top_bar.addWidget(self.logout_btn)
        self.main_layout.addLayout(top_bar)

        # ── Section 1: Security Overview ──
        self.overview_title = QLabel(self.lang_manager.get_text("admin_security_overview"))
        self.main_layout.addWidget(self.overview_title)

        cards_grid = QGridLayout()
        cards_grid.setSpacing(12)

        self.card_active = AdminStatCard(title="Active Sessions", value="0", trend_text="Current", icon="🔒", accent_color=theme.CYAN)
        self.card_failed = AdminStatCard(title="Failed Logins", value="0", trend_text="All time", icon="❌", accent_color=theme.ORANGE)
        self.card_suspicious = AdminStatCard(title="Suspicious", value="0", trend_text="Detected", icon="⚠", accent_color=theme.RED)
        self.card_frozen = AdminStatCard(title="Frozen Accounts", value="0", trend_text="Locked", icon="❄️", accent_color=theme.TEXT_SECONDARY)

        cards_grid.addWidget(self.card_active, 0, 0)
        cards_grid.addWidget(self.card_failed, 0, 1)
        cards_grid.addWidget(self.card_suspicious, 0, 2)
        cards_grid.addWidget(self.card_frozen, 0, 3)
        self.main_layout.addLayout(cards_grid)

        # ── Section 2: Security Alerts ──
        self.alerts_title = QLabel(self.lang_manager.get_text("admin_security_alerts"))
        self.main_layout.addWidget(self.alerts_title)
        
        self.alerts_container = QVBoxLayout()
        self.alerts_container.setSpacing(8)
        self.main_layout.addLayout(self.alerts_container)

        # ── Section 3: Active Sessions ──
        self.sessions_title = QLabel(self.lang_manager.get_text("admin_active_sessions"))
        self.main_layout.addWidget(self.sessions_title)
        
        self.sessions_container = QVBoxLayout()
        self.sessions_container.setSpacing(8)
        self.main_layout.addLayout(self.sessions_container)

        # ── Section 4: Login History Table ──
        self.history_title = QLabel(self.lang_manager.get_text("admin_login_history"))
        self.main_layout.addWidget(self.history_title)
        
        self.history_table = QTableWidget(0, 4)
        self.history_table.setHorizontalHeaderLabels([
            "Username", "Time", "Status", "Device/Location"
        ])
        self._setup_table(self.history_table)
        self.main_layout.addWidget(self.history_table)

        # ── Section 5: Admin Activity Logs ──
        self.logs_title = QLabel(self.lang_manager.get_text("admin_activity_logs"))
        self.main_layout.addWidget(self.logs_title)
        
        self.logs_table = QTableWidget(0, 4)
        self.logs_table.setHorizontalHeaderLabels([
            "Admin", "Action", "Target", "Time"
        ])
        self._setup_table(self.logs_table)
        self.main_layout.addWidget(self.logs_table)

        self.main_layout.addStretch()

        scroll.setWidget(content)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def _setup_table(self, table):
        """Common styling for security tables."""
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setMinimumHeight(200)
        table.setMaximumHeight(300)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def load_data(self):
        """Fetch all security data and populate UI."""
        
        # 1. Overview Stats
        stats = SecurityService.get_security_overview_stats()
        self.card_active.set_value(str(stats["active_sessions"]))
        self.card_failed.set_value(str(stats["failed_logins"]))
        self.card_frozen.set_value(str(stats["frozen_accounts"]))
        
        # 2. Alerts
        self._clear_layout(self.alerts_container)
        alerts = SecurityService.detect_suspicious_activity()
        self.card_suspicious.set_value(str(len(alerts)))
        
        if not alerts:
            lbl = QLabel(self.lang_manager.get_text("admin_no_alerts"))
            lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 13px;")
            self.alerts_container.addWidget(lbl)
        else:
            for alert in alerts:
                card = SecurityAlertCard(alert["type"], alert["title"], alert["desc"])
                self.alerts_container.addWidget(card)
                
        # 3. Active Sessions
        self._clear_layout(self.sessions_container)
        sessions = SecurityService.get_active_sessions()
        if not sessions:
            lbl = QLabel("No active sessions.")
            lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 13px;")
            self.sessions_container.addWidget(lbl)
        else:
            for sess in sessions:
                # id, username, token, created_at
                card = SessionCard(sess[0], sess[1], sess[3])
                card.terminate_requested.connect(self._handle_terminate)
                self.sessions_container.addWidget(card)
                
        # 4. Login History
        history = SecurityService.get_login_history(20)
        self._populate_history(history)
        
        # 5. Admin Logs
        logs = SecurityService.get_admin_logs(20)
        self._populate_logs(logs)

    def _handle_terminate(self, session_id):
        """Terminate a session and refresh."""
        SecurityService.terminate_session(session_id)
        # Log this action
        SecurityService.log_admin_action("admin", "TERMINATE_SESSION", f"SessionID:{session_id}")
        self.load_data()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _populate_history(self, history):
        if not history:
            self.history_table.setRowCount(1)
            item = QTableWidgetItem("No login history.")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(theme.TEXT_SECONDARY))
            self.history_table.setItem(0, 0, item)
            self.history_table.setSpan(0, 0, 1, 4)
            return

        self.history_table.clearSpans()
        self.history_table.setRowCount(len(history))
        for row, (user, time, status, device, location) in enumerate(history):
            self.history_table.setItem(row, 0, QTableWidgetItem(user))
            self.history_table.setItem(row, 1, QTableWidgetItem(time[:16] if time else ""))
            
            stat_item = QTableWidgetItem(status)
            if status == "SUCCESS":
                stat_item.setForeground(QColor(theme.GREEN))
            elif status == "FAILED":
                stat_item.setForeground(QColor(theme.ORANGE))
            elif status == "BLOCKED":
                stat_item.setForeground(QColor(theme.RED))
            self.history_table.setItem(row, 2, stat_item)
            
            dev_loc = f"{device or 'Unknown'} / {location or 'Unknown'}"
            self.history_table.setItem(row, 3, QTableWidgetItem(dev_loc))

    def _populate_logs(self, logs):
        if not logs:
            self.logs_table.setRowCount(1)
            item = QTableWidgetItem("No activity logs.")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(theme.TEXT_SECONDARY))
            self.logs_table.setItem(0, 0, item)
            self.logs_table.setSpan(0, 0, 1, 4)
            return

        self.logs_table.clearSpans()
        self.logs_table.setRowCount(len(logs))
        for row, (admin, action, target, time) in enumerate(logs):
            self.logs_table.setItem(row, 0, QTableWidgetItem(admin))
            
            action_item = QTableWidgetItem(action)
            action_item.setForeground(QColor(theme.CYAN))
            self.logs_table.setItem(row, 1, action_item)
            
            self.logs_table.setItem(row, 2, QTableWidgetItem(target or ""))
            self.logs_table.setItem(row, 3, QTableWidgetItem(time[:16] if time else ""))

    def update_theme(self):
        theme.update_globals()
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")

        title_style = f"color: {theme.TEXT_PRIMARY}; font-size: 16px; font-weight: 700;"
        for lbl in [self.overview_title, self.alerts_title, self.sessions_title, 
                    self.history_title, self.logs_title]:
            lbl.setStyleSheet(title_style)

        table_style = f"""
            QTableWidget {{
                background-color: {theme.CARD_BG};
                color: {theme.TEXT_PRIMARY};
                gridline-color: transparent;
                border: 1px solid {theme.BORDER};
                border-radius: 8px;
            }}
            QTableWidget::item {{ padding: 8px; border-bottom: 1px solid {theme.BORDER}; }}
            QHeaderView::section {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_SECONDARY};
                padding: 6px; border: none; border-bottom: 2px solid {theme.BORDER};
                font-weight: bold;
            }}
        """
        self.history_table.setStyleSheet(table_style)
        self.logs_table.setStyleSheet(table_style)
        
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.CARD_BG};
                color: {theme.RED};
                border: 1px solid {theme.RED};
                border-radius: 6px;
                padding: 0 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme.RED}; color: white;
            }}
        """)
        
        for card in [self.card_active, self.card_failed, self.card_suspicious, self.card_frozen]:
            card.update_theme()
            
        # Update child cards
        for i in range(self.alerts_container.count()):
            w = self.alerts_container.itemAt(i).widget()
            if hasattr(w, "update_theme"): w.update_theme()
            
        for i in range(self.sessions_container.count()):
            w = self.sessions_container.itemAt(i).widget()
            if hasattr(w, "update_theme"): w.update_theme()

    def update_translations(self):
        self.overview_title.setText(self.lang_manager.get_text("admin_security_overview"))
        self.alerts_title.setText(self.lang_manager.get_text("admin_security_alerts"))
        self.sessions_title.setText(self.lang_manager.get_text("admin_active_sessions"))
        self.history_title.setText(self.lang_manager.get_text("admin_login_history"))
        self.logs_title.setText(self.lang_manager.get_text("admin_activity_logs"))
        self.logout_btn.setText("🚪 " + self.lang_manager.get_text("logout"))

    def update_ui(self):
        self.load_data()
        self.update_theme()
