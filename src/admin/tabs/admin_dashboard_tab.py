"""Admin Dashboard Tab — Full analytics dashboard with charts, reports, and monitoring.

Layout:
┌──────────────────────────────────────────────────────────┐
│ Overview Stat Cards (4)                                  │
├─────────────────────────────┬────────────────────────────┤
│ Daily Transactions Chart    │ Tier Distribution Chart    │
├─────────────────────────────┼────────────────────────────┤
│ User Growth Chart           │ Risk Distribution Chart    │
├─────────────────────────────┴────────────────────────────┤
│ Fraud Monitoring Overview                                │
├──────────────────────────────────────────────────────────┤
│ System Health                                            │
├──────────────────────────────────────────────────────────┤
│ Recent Activity                                          │
└──────────────────────────────────────────────────────────┘
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.admin.components.admin_stat_card import AdminStatCard
from src.admin.components.analytics_chart_card import (
    AnalyticsChartCard, MiniBarChart, MiniDonutChart,
)
from src.admin.components.report_summary_card import (
    RiskMonitoringCard, SystemHealthCard, RecentActivityCard,
)
from src.admin.services.analytics_service import AnalyticsService
from src.admin.services.notification_service import AdminNotificationService
from src.admin.components.announcement_card import AnnouncementCard
from src.core.utils import safe_currency


class AdminDashboardTab(QWidget):
    """Admin analytics dashboard with stat cards, charts, monitoring, and activity feed."""

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setObjectName("AdminDashboardTab")
        self._setup_ui()
        self.update_theme()
        self.load_dashboard_data()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setObjectName("AdminDashboardScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("AdminDashboardContent")
        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(28, 24, 28, 24)
        self.main_layout.setSpacing(16)

        # ── Section 1: Overview Stat Cards ──
        self.overview_title = QLabel(self.lang_manager.get_text("admin_overview"))
        self.overview_title.setObjectName("AdminDashboardSectionTitle_Overview")
        self.main_layout.addWidget(self.overview_title)

        cards_grid = QGridLayout()
        cards_grid.setSpacing(12)

        self.card_total_users = AdminStatCard(
            title=self.lang_manager.get_text("admin_total_users"),
            value="0", trend_text="↑ Loading...", icon="👥",
            accent_color=theme.CYAN,
        )
        self.card_total_users.setObjectName("StatCard_TotalUsers")
        
        self.card_total_balance = AdminStatCard(
            title=self.lang_manager.get_text("admin_total_balance"),
            value="0 VND", trend_text="System total", icon="💰",
            accent_color=theme.GREEN,
        )
        self.card_total_balance.setObjectName("StatCard_TotalBalance")

        self.card_monthly_volume = AdminStatCard(
            title=self.lang_manager.get_text("admin_monthly_volume"),
            value="0", trend_text="Last 30 days", icon="💹",
            accent_color=theme.ORANGE,
        )
        self.card_monthly_volume.setObjectName("StatCard_MonthlyVolume")

        self.card_flagged = AdminStatCard(
            title=self.lang_manager.get_text("admin_flagged_count"),
            value="0", trend_text="Needs review", icon="🚩",
            accent_color=theme.RED,
        )
        self.card_flagged.setObjectName("StatCard_Flagged")

        cards_grid.addWidget(self.card_total_users, 0, 0)
        cards_grid.addWidget(self.card_total_balance, 0, 1)
        cards_grid.addWidget(self.card_monthly_volume, 0, 2)
        cards_grid.addWidget(self.card_flagged, 0, 3)
        self.main_layout.addLayout(cards_grid)

        # ── Section 2: Analytics Charts (2x2 grid) ──
        self.charts_title = QLabel(self.lang_manager.get_text("admin_analytics_charts"))
        self.charts_title.setObjectName("AdminDashboardSectionTitle_Charts")
        self.main_layout.addWidget(self.charts_title)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(12)

        # Daily Transactions Bar Chart
        self.txn_bar_chart = MiniBarChart()
        self.chart_daily_txn = AnalyticsChartCard(
            title=self.lang_manager.get_text("admin_daily_transactions"),
            chart_widget=self.txn_bar_chart,
        )
        self.chart_daily_txn.setObjectName("ChartCard_DailyTxn")

        # Tier Distribution Donut
        self.tier_donut = MiniDonutChart()
        self.chart_tier = AnalyticsChartCard(
            title=self.lang_manager.get_text("admin_tier_distribution"),
            chart_widget=self.tier_donut,
        )
        self.chart_tier.setObjectName("ChartCard_Tier")

        # User Growth Bar Chart
        self.user_bar_chart = MiniBarChart()
        self.chart_user_growth = AnalyticsChartCard(
            title=self.lang_manager.get_text("admin_user_growth"),
            chart_widget=self.user_bar_chart,
        )
        self.chart_user_growth.setObjectName("ChartCard_UserGrowth")

        # Risk Distribution Donut
        self.risk_donut = MiniDonutChart()
        self.chart_risk = AnalyticsChartCard(
            title=self.lang_manager.get_text("admin_risk_distribution"),
            chart_widget=self.risk_donut,
        )
        self.chart_risk.setObjectName("ChartCard_Risk")

        charts_grid.addWidget(self.chart_daily_txn, 0, 0)
        charts_grid.addWidget(self.chart_tier, 0, 1)
        charts_grid.addWidget(self.chart_user_growth, 1, 0)
        charts_grid.addWidget(self.chart_risk, 1, 1)
        self.main_layout.addLayout(charts_grid)

        # ── Section 3: System Announcements ──
        self.announcements_title = QLabel("System Announcements")
        self.announcements_title.setObjectName("AdminDashboardSectionTitle_Announcements")
        self.main_layout.addWidget(self.announcements_title)

        self.announcements_container = QVBoxLayout()
        self.announcements_container.setSpacing(8)
        self.main_layout.addLayout(self.announcements_container)

        self.no_announcements_lbl = QLabel("No announcements available.")
        self.no_announcements_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.no_announcements_lbl)

        # ── Section 4: Fraud Monitoring Overview ──
        self.risk_card = RiskMonitoringCard()
        self.risk_card.setObjectName("RiskMonitoringCard")
        self.main_layout.addWidget(self.risk_card)

        # ── Section 5: System Health ──
        self.health_card = SystemHealthCard()
        self.health_card.setObjectName("SystemHealthCard")
        self.main_layout.addWidget(self.health_card)

        # ── Section 6: Recent Activity ──
        self.activity_card = RecentActivityCard()
        self.activity_card.setObjectName("RecentActivityCard")
        self.main_layout.addWidget(self.activity_card)

        self.main_layout.addStretch()

        scroll.setWidget(content)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def load_dashboard_data(self):
        """Load all analytics data from database."""
        try:
            # Stat cards
            total_users = AnalyticsService.get_total_users()
            self.card_total_users.set_value(f"{total_users:,}")
            self.card_total_users.set_trend(f"↑ {total_users} registered")

            total_balance = AnalyticsService.get_total_balance()
            self.card_total_balance.set_value(safe_currency(total_balance))

            monthly_volume = AnalyticsService.get_transaction_volume(30)
            self.card_monthly_volume.set_value(f"{monthly_volume:,}")
            self.card_monthly_volume.set_trend("Last 30 days")

            risk_stats = AnalyticsService.get_risk_statistics()
            flagged = risk_stats.get("flagged", 0)
            self.card_flagged.set_value(str(flagged))
            self.card_flagged.set_trend("Needs review" if flagged > 0 else "All clear")

            # Charts
            daily_txns = AnalyticsService.get_daily_transaction_counts(7)
            self.txn_bar_chart.set_data(daily_txns, bar_color=theme.CYAN)

            user_growth = AnalyticsService.get_daily_user_registrations(7)
            self.user_bar_chart.set_data(user_growth, bar_color="#22C55E")

            tier_dist = AnalyticsService.get_tier_distribution()
            self.tier_donut.set_data([
                ("Standard", tier_dist.get("STANDARD", 0), theme.TEXT_SECONDARY),
                ("Gold", tier_dist.get("GOLD", 0), "#D4AF37"),
                ("Diamond", tier_dist.get("DIAMOND", 0), theme.CYAN),
            ])

            risk_dist = AnalyticsService.get_risk_distribution()
            self.risk_donut.set_data([
                ("Low", risk_dist.get("LOW", 0), "#4ADE80"),
                ("Medium", risk_dist.get("MEDIUM", 0), "#FBBF24"),
                ("High", risk_dist.get("HIGH", 0), "#FB923C"),
                ("Critical", risk_dist.get("CRITICAL", 0), "#F87171"),
            ])

            # Risk monitoring
            self.risk_card.set_data(
                flagged=risk_stats.get("flagged", 0),
                critical=risk_stats.get("critical", 0),
                blocked=risk_stats.get("blocked", 0),
                suspicious_users=risk_stats.get("suspicious_users", 0),
            )

            # System health
            health = AnalyticsService.get_system_health()
            self.health_card.set_data(health)

            # Recent activity
            activities = AnalyticsService.get_recent_activity(8)
            self.activity_card.set_data(activities)

            # Announcements
            self._load_announcements()

        except Exception as e:
            print(f"Admin dashboard data error: {e}")

    def _load_announcements(self):
        """Load recent global announcements."""
        while self.announcements_container.count():
            item = self.announcements_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        announcements = AdminNotificationService.get_recent_announcements(3)
        if not announcements:
            self.no_announcements_lbl.setVisible(True)
        else:
            self.no_announcements_lbl.setVisible(False)
            for ann in announcements:
                card = AnnouncementCard(
                    title=ann[0], n_type=ann[1], priority=ann[2],
                    time_str=str(ann[3])[:16], message=ann[4]
                )
                self.announcements_container.addWidget(card)

    def update_theme(self):
        theme.update_globals()
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")

        section_title_style = f"""
            color: {theme.TEXT_PRIMARY}; font-size: 16px; font-weight: 700;
            border: none; background: transparent; padding-bottom: 4px;
        """
        self.overview_title.setStyleSheet(section_title_style)
        self.charts_title.setStyleSheet(section_title_style)
        self.announcements_title.setStyleSheet(section_title_style)

        self.no_announcements_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; padding: 20px;")

        # Stat cards
        for card in [self.card_total_users, self.card_total_balance,
                      self.card_monthly_volume, self.card_flagged]:
            card.update_theme()

        # Chart cards
        for chart_card in [self.chart_daily_txn, self.chart_tier,
                            self.chart_user_growth, self.chart_risk]:
            chart_card.update_theme()

        # Summary cards
        self.risk_card.update_theme()
        self.health_card.update_theme()
        self.activity_card.update_theme()

    def update_translations(self):
        self.overview_title.setText(self.lang_manager.get_text("admin_overview"))
        self.charts_title.setText(self.lang_manager.get_text("admin_analytics_charts"))
        self.announcements_title.setText(self.lang_manager.get_text("admin_system_announcements"))
        self.no_announcements_lbl.setText(self.lang_manager.get_text("admin_no_announcements"))
        self.chart_daily_txn.set_title(self.lang_manager.get_text("admin_daily_transactions"))
        self.chart_tier.set_title(self.lang_manager.get_text("admin_tier_distribution"))
        self.chart_user_growth.set_title(self.lang_manager.get_text("admin_user_growth"))
        self.chart_risk.set_title(self.lang_manager.get_text("admin_risk_distribution"))
        self.risk_card.update_translations()
        self.health_card.update_translations()
        self.activity_card.update_translations()

    def update_ui(self):
        """Refresh all dashboard data."""
        self.load_dashboard_data()
        self.update_theme()
