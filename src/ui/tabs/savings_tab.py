from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QPushButton, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from src.core import theme
from src.core.language_manager import LanguageManager
from src.services.savings_service import SavingsService
from src.services.savings_analytics_service import SavingsAnalyticsService
from src.ui.components.savings_card import SavingsCard
from src.ui.components.savings_chart import SavingsBarChart
from src.ui.dialogs.create_savings_dialog import CreateSavingsDialog
from src.ui.dialogs.savings_detail_dialog import SavingsDetailDialog

class SavingsTab(QWidget):
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.lang_manager = LanguageManager()
        self.setup_ui()
        
        # Auto-refresh timer for analytics
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_analytics)
        self.refresh_timer.start(10000) # Every 10 seconds
        
        self.refresh_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Header
        header = QHBoxLayout()
        title_container = QVBoxLayout()
        self.title_label = QLabel(self.lang_manager.get_text("savings"))
        self.title_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 32px; font-weight: 800;")
        
        self.subtitle_label = QLabel("Grow your wealth with smart savings plans")
        self.subtitle_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 14px;")
        
        title_container.addWidget(self.title_label)
        title_container.addWidget(self.subtitle_label)
        
        header.addLayout(title_container)
        header.addStretch()
        
        self.create_btn = QPushButton(f"＋ {self.lang_manager.get_text('create_new_plan')}")
        self.create_btn.clicked.connect(self.show_create_dialog)
        self.create_btn.setStyleSheet(f"""
            background-color: {theme.CYAN};
            color: white;
            border-radius: 12px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
        """)
        header.addWidget(self.create_btn)
        layout.addLayout(header)

        # Stats Row
        stats_layout = QHBoxLayout()
        self.total_saved_card = self.create_stat_card("total_saved", "0 VND", "💰")
        self.active_plans_card = self.create_stat_card("active_plans", "0", "📈")
        self.interest_card = self.create_stat_card("monthly_interest", "0 VND", "✨")
        
        stats_layout.addWidget(self.total_saved_card)
        stats_layout.addWidget(self.active_plans_card)
        stats_layout.addWidget(self.interest_card)
        layout.addLayout(stats_layout)

        # Main Content: Plans + Chart
        content_layout = QHBoxLayout()
        
        # Left: Plans Grid
        plans_container = QVBoxLayout()
        plans_container.addWidget(QLabel(self.lang_manager.get_text("active_plans"), styleSheet=f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: bold;"))
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        self.plans_widget = QWidget()
        self.plans_grid = QGridLayout(self.plans_widget)
        self.plans_grid.setSpacing(20)
        scroll.setWidget(self.plans_widget)
        
        plans_container.addWidget(scroll)
        content_layout.addLayout(plans_container, 2)
        
        # Right: Analytics
        analytics_container = QVBoxLayout()
        analytics_container.addWidget(QLabel(self.lang_manager.get_text("savings_growth"), styleSheet=f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: bold;"))
        
        self.chart_card = QFrame()
        self.chart_card.setStyleSheet(f"background-color: {theme.PANEL_BG}; border-radius: 20px; border: 1px solid {theme.BORDER};")
        chart_layout = QVBoxLayout(self.chart_card)
        self.chart = SavingsBarChart()
        chart_layout.addWidget(self.chart)
        
        analytics_container.addWidget(self.chart_card)
        content_layout.addLayout(analytics_container, 1)
        
        layout.addLayout(content_layout)

    def create_stat_card(self, label_key, value, icon):
        card = QFrame()
        card.setStyleSheet(f"background-color: {theme.PANEL_BG}; border-radius: 20px; border: 1px solid {theme.BORDER};")
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 20, 20, 20)
        
        h = QHBoxLayout()
        h.addWidget(QLabel(icon, styleSheet="font-size: 20px;"))
        h.addStretch()
        l.addLayout(h)
        
        val_label = QLabel(value)
        val_label.setObjectName("value")
        val_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 22px; font-weight: 800;")
        l.addWidget(val_label)
        
        text_label = QLabel(self.lang_manager.get_text(label_key))
        text_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 12px;")
        l.addWidget(text_label)
        
        return card

    def refresh_data(self):
        # Refresh Stats
        stats = SavingsService.get_savings_stats(self.username)
        self.total_saved_card.findChild(QLabel, "value").setText(f"{stats['total_saved']:,.0f} VND")
        self.active_plans_card.findChild(QLabel, "value").setText(str(stats["active_count"]))
        self.interest_card.findChild(QLabel, "value").setText(f"{stats['total_interest']:,.0f} VND")

        # Refresh Plans
        # Clear grid
        for i in reversed(range(self.plans_grid.count())): 
            widget = self.plans_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            
        plans = SavingsService.get_user_plans(self.username)
        for i, plan in enumerate(plans):
            card = SavingsCard(plan)
            card.clicked.connect(self.show_detail_dialog)
            self.plans_grid.addWidget(card, i // 2, i % 2)

        self.refresh_analytics()

    def refresh_analytics(self):
        """Refreshes chart data without rebuilding the entire UI."""
        growth_data = SavingsAnalyticsService.get_growth_data(self.username)
        if growth_data:
            self.chart.set_data(growth_data)
        else:
            # Fallback to monthly deposits if no active growth
            monthly_data = SavingsAnalyticsService.get_monthly_deposits(self.username)
            if any(v > 0 for _, v in monthly_data):
                self.chart.set_data(monthly_data)
            else:
                self.chart.set_data([("No Data", 0)])

    def update_ui(self):
        """Standard lifecycle method for tab refresh."""
        self.refresh_data()

    def update_translations(self):
        """Standard lifecycle method for language refresh."""
        self.title_label.setText(self.lang_manager.get_text("savings"))
        self.create_btn.setText(f"＋ {self.lang_manager.get_text('create_new_plan')}")
        # Refresh card labels
        self.refresh_data()

    def update_theme(self):
        """Standard lifecycle method for theme refresh."""
        # Theme is mostly handled by refresh_data and dynamic styles, 
        # but we could force update widgets if needed.
        self.refresh_data()

    def show_create_dialog(self):
        dialog = CreateSavingsDialog(self.username, self)
        if dialog.exec():
            self.refresh_data()

    def show_detail_dialog(self, savings_id):
        # Find the plan
        plans = SavingsService.get_user_plans(self.username)
        plan = next((p for p in plans if p.savings_id == savings_id), None)
        if plan:
            dialog = SavingsDetailDialog(self.username, plan, self)
            if dialog.exec():
                self.refresh_data()
