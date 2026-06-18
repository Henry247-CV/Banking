"""Report Summary Card — Enterprise-grade summary panels for admin dashboard.

Includes: Risk Monitoring Panel, System Health Panel, Recent Activity Feed.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QWidget, QScrollArea,
)
from PyQt6.QtCore import Qt
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager


class RiskMonitoringCard(QFrame):
    """Fraud monitoring overview panel with 4 stat indicators."""

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.setMinimumHeight(100)
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        self.title_label = QLabel(self.lang_manager.get_text("admin_fraud_overview"))
        layout.addWidget(self.title_label)

        grid = QGridLayout()
        grid.setSpacing(12)

        self.lbl_flagged_k = QLabel("🚩 " + self.lang_manager.get_text("admin_flagged_txns"))
        self.lbl_flagged_v = QLabel("0")
        self.lbl_critical_k = QLabel("⚠ " + self.lang_manager.get_text("admin_high_risk_txns"))
        self.lbl_critical_v = QLabel("0")
        self.lbl_blocked_k = QLabel("⛔ " + self.lang_manager.get_text("admin_blocked_transfers"))
        self.lbl_blocked_v = QLabel("0")
        self.lbl_suspicious_k = QLabel("👤 " + self.lang_manager.get_text("admin_suspicious_users"))
        self.lbl_suspicious_v = QLabel("0")

        grid.addWidget(self.lbl_flagged_k, 0, 0)
        grid.addWidget(self.lbl_flagged_v, 0, 1)
        grid.addWidget(self.lbl_critical_k, 0, 2)
        grid.addWidget(self.lbl_critical_v, 0, 3)
        grid.addWidget(self.lbl_blocked_k, 1, 0)
        grid.addWidget(self.lbl_blocked_v, 1, 1)
        grid.addWidget(self.lbl_suspicious_k, 1, 2)
        grid.addWidget(self.lbl_suspicious_v, 1, 3)

        layout.addLayout(grid)

    def set_data(self, flagged=0, critical=0, blocked=0, suspicious_users=0):
        self.lbl_flagged_v.setText(str(flagged))
        self.lbl_critical_v.setText(str(critical))
        self.lbl_blocked_v.setText(str(blocked))
        self.lbl_suspicious_v.setText(str(suspicious_users))

    def update_theme(self):
        theme.update_globals()
        self.setStyleSheet(f"""
            RiskMonitoringCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-left: 3px solid {theme.RED};
                border-radius: 10px;
            }}
        """)
        self.title_label.setStyleSheet(f"""
            color: {theme.TEXT_PRIMARY}; font-size: 14px; font-weight: 700;
            border: none; background: transparent;
        """)
        key_style = f"""
            color: {theme.TEXT_SECONDARY}; font-size: 12px; font-weight: 500;
            border: none; background: transparent;
        """
        val_style = f"""
            font-size: 18px; font-weight: 800; border: none; background: transparent;
        """
        for lbl in [self.lbl_flagged_k, self.lbl_critical_k,
                     self.lbl_blocked_k, self.lbl_suspicious_k]:
            lbl.setStyleSheet(key_style)

        self.lbl_flagged_v.setStyleSheet(val_style + f"color: {theme.ORANGE};")
        self.lbl_critical_v.setStyleSheet(val_style + f"color: {theme.RED};")
        self.lbl_blocked_v.setStyleSheet(val_style + f"color: {theme.RED};")
        self.lbl_suspicious_v.setStyleSheet(val_style + f"color: {theme.ORANGE};")

    def update_translations(self):
        self.title_label.setText(self.lang_manager.get_text("admin_fraud_overview"))
        self.lbl_flagged_k.setText("🚩 " + self.lang_manager.get_text("admin_flagged_txns"))
        self.lbl_critical_k.setText("⚠ " + self.lang_manager.get_text("admin_high_risk_txns"))
        self.lbl_blocked_k.setText("⛔ " + self.lang_manager.get_text("admin_blocked_transfers"))
        self.lbl_suspicious_k.setText("👤 " + self.lang_manager.get_text("admin_suspicious_users"))


class SystemHealthCard(QFrame):
    """System health overview panel."""

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.setMinimumHeight(100)
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        self.title_label = QLabel(self.lang_manager.get_text("admin_system_health"))
        layout.addWidget(self.title_label)

        grid = QGridLayout()
        grid.setSpacing(8)

        self.k_db = QLabel("💾 " + self.lang_manager.get_text("admin_db_status"))
        self.v_db = QLabel("—")
        self.k_theme = QLabel("🎨 " + self.lang_manager.get_text("theme_mode"))
        self.v_theme = QLabel("—")
        self.k_lang = QLabel("🌐 " + self.lang_manager.get_text("language"))
        self.v_lang = QLabel("—")
        self.k_records = QLabel("📊 " + self.lang_manager.get_text("admin_total_records"))
        self.v_records = QLabel("—")

        grid.addWidget(self.k_db, 0, 0)
        grid.addWidget(self.v_db, 0, 1)
        grid.addWidget(self.k_theme, 0, 2)
        grid.addWidget(self.v_theme, 0, 3)
        grid.addWidget(self.k_lang, 1, 0)
        grid.addWidget(self.v_lang, 1, 1)
        grid.addWidget(self.k_records, 1, 2)
        grid.addWidget(self.v_records, 1, 3)

        layout.addLayout(grid)

    def set_data(self, health_data):
        status = health_data.get("db_status", "UNKNOWN")
        self.v_db.setText(f"● {status}")
        self.v_theme.setText(health_data.get("current_theme", "—"))
        self.v_lang.setText(health_data.get("current_language", "—"))
        total = health_data.get("total_records", 0)
        self.v_records.setText(f"{total:,}")

    def update_theme(self):
        theme.update_globals()
        self.setStyleSheet(f"""
            SystemHealthCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-left: 3px solid {theme.CYAN};
                border-radius: 10px;
            }}
        """)
        self.title_label.setStyleSheet(f"""
            color: {theme.TEXT_PRIMARY}; font-size: 14px; font-weight: 700;
            border: none; background: transparent;
        """)
        key_style = f"""
            color: {theme.TEXT_SECONDARY}; font-size: 12px; font-weight: 500;
            border: none; background: transparent;
        """
        val_style = f"""
            color: {theme.TEXT_PRIMARY}; font-size: 13px; font-weight: 700;
            border: none; background: transparent;
        """
        for lbl in [self.k_db, self.k_theme, self.k_lang, self.k_records]:
            lbl.setStyleSheet(key_style)
        for lbl in [self.v_theme, self.v_lang, self.v_records]:
            lbl.setStyleSheet(val_style)

        # DB status color
        self.v_db.setStyleSheet(f"""
            color: {theme.GREEN}; font-size: 13px; font-weight: 700;
            border: none; background: transparent;
        """)

    def update_translations(self):
        self.title_label.setText(self.lang_manager.get_text("admin_system_health"))
        self.k_db.setText("💾 " + self.lang_manager.get_text("admin_db_status"))
        self.k_theme.setText("🎨 " + self.lang_manager.get_text("theme_mode"))
        self.k_lang.setText("🌐 " + self.lang_manager.get_text("language"))
        self.k_records.setText("📊 " + self.lang_manager.get_text("admin_total_records"))


class RecentActivityCard(QFrame):
    """Recent activity feed showing latest system events."""

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self.title_label = QLabel(self.lang_manager.get_text("admin_recent_activity"))
        layout.addWidget(self.title_label)

        self.activity_container = QVBoxLayout()
        self.activity_container.setSpacing(4)
        layout.addLayout(self.activity_container)

        self.empty_label = QLabel(self.lang_manager.get_text("admin_no_activity"))
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_label)

        layout.addStretch()

    def set_data(self, activities):
        """activities: list of dicts with 'type', 'desc', 'time'."""
        # Clear old items
        while self.activity_container.count():
            item = self.activity_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not activities:
            self.empty_label.setVisible(True)
            return

        self.empty_label.setVisible(False)
        for act in activities[:8]:
            row = QHBoxLayout()
            row.setSpacing(8)

            type_lbl = QLabel(act.get("type", "—"))
            type_lbl.setFixedWidth(90)
            desc_lbl = QLabel(act.get("desc", ""))
            time_lbl = QLabel(act.get("time", ""))
            time_lbl.setFixedWidth(110)

            theme.update_globals()
            type_lbl.setStyleSheet(f"""
                color: {theme.CYAN}; font-size: 11px; font-weight: 600;
                border: none; background: transparent;
            """)
            desc_lbl.setStyleSheet(f"""
                color: {theme.TEXT_PRIMARY}; font-size: 11px;
                border: none; background: transparent;
            """)
            time_lbl.setStyleSheet(f"""
                color: {theme.TEXT_SECONDARY}; font-size: 10px;
                border: none; background: transparent;
            """)

            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 2, 0, 2)
            row_layout.setSpacing(8)
            row_layout.addWidget(type_lbl)
            row_layout.addWidget(desc_lbl)
            row_layout.addStretch()
            row_layout.addWidget(time_lbl)
            row_widget.setFixedHeight(24)

            self.activity_container.addWidget(row_widget)

    def update_theme(self):
        theme.update_globals()
        self.setStyleSheet(f"""
            RecentActivityCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 10px;
            }}
        """)
        self.title_label.setStyleSheet(f"""
            color: {theme.TEXT_PRIMARY}; font-size: 14px; font-weight: 700;
            border: none; background: transparent;
        """)
        self.empty_label.setStyleSheet(f"""
            color: {theme.TEXT_SECONDARY}; font-size: 12px;
            border: none; background: transparent;
        """)

    def update_translations(self):
        self.title_label.setText(self.lang_manager.get_text("admin_recent_activity"))
        self.empty_label.setText(self.lang_manager.get_text("admin_no_activity"))
