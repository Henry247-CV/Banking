from PyQt6 import sip
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
import src.core.theme as theme
from src.core.styles import *
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.core.utils import safe_currency
from src.services.savings_service import SavingsService
from src.services.savings_growth_service import SavingsGrowthService
from src.ui.components.savings_card import SavingsCard
from src.ui.components.savings_chart import SavingsChart
from src.ui.dialogs.create_savings_dialog import CreateSavingsDialog
from src.ui.dialogs.savings_detail_dialog import SavingsDetailDialog
from src.core.app_stabilizer import AppStabilizer
from src.core.debug_logger import DebugLogger

class SavingsTab(QWidget):
    balance_updated = pyqtSignal()

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.plan_cards = {} # Store cards for live updates
        self.stat_labels = {} 
        self.setup_ui()
        self.update_theme()
        self.load_data()
        print("Savings widget loaded")
        
        # Setup Auto-Refresh Timer (10 seconds)
        self.refresh_timer = AppStabilizer().create_safe_timer(
            parent=self, interval_ms=10000, callback=self.live_refresh
        )
        self.refresh_timer.start()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(30, 30, 30, 30)
        self.container_layout.setSpacing(30)

        # 1. Header & Quick Stats
        header_layout = QHBoxLayout()
        self.title_label = QLabel(self.lang_manager.get_text("savings_dashboard"))
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        self.create_btn = QPushButton("+ " + self.lang_manager.get_text("new_plan"))
        # Use single-shot or check for existing connection if needed, 
        # but here it's called once in setup_ui.
        self.create_btn.clicked.connect(self.handle_create_plan)
        header_layout.addWidget(self.create_btn)
        self.container_layout.addLayout(header_layout)

        # Stats Grid
        self.stats_grid = QGridLayout()
        self.container_layout.addLayout(self.stats_grid)

        # 2. Analytics Chart
        self.chart_card = QFrame()
        chart_layout = QVBoxLayout(self.chart_card)
        self.chart_title = QLabel(self.lang_manager.get_text("savings_growth"))
        self.chart = SavingsChart()
        chart_layout.addWidget(self.chart_title)
        chart_layout.addWidget(self.chart)
        self.container_layout.addWidget(self.chart_card)

        # 3. Active Plans Section
        self.plans_title = QLabel(self.lang_manager.get_text("active_plans"))
        self.container_layout.addWidget(self.plans_title)
        
        self.plans_grid = QGridLayout()
        self.container_layout.addLayout(self.plans_grid)
        
        self.container_layout.addStretch()
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

    def live_refresh(self):
        """Dynamic refresh — updates numbers and charts without flickering."""
        if sip.isdeleted(self): return
        
        try:
            # 1. Calculate Growth (Background)
            SavingsGrowthService.calculate_interest_growth(self.user_data['username'])
            
            # 2. Update Stats
            stats = SavingsService.get_savings_stats(self.user_data['username'])
            for key, label in self.stat_labels.items():
                if label and not sip.isdeleted(label) and key in stats:
                    label.setText(safe_currency(stats[key]) if "interest" in key or "saved" in key else str(stats[key]))
                
            # 3. Update Existing Cards
            plans = SavingsService.get_user_savings(self.user_data['username'])
            for plan in plans:
                card = self.plan_cards.get(plan.id)
                if card and not sip.isdeleted(card):
                    if hasattr(card, "update_data"):
                        card.update_data(plan)
            
            # 4. Refresh Chart with Real Analytics
            from src.services.savings_analytics_service import SavingsAnalyticsService
            growth_data = SavingsAnalyticsService.get_growth_data(self.user_data['username'])
            if self.chart and not sip.isdeleted(self.chart):
                self.chart.set_data(growth_data)
        except Exception as e:
            DebugLogger.log_error(f"SavingsTab live_refresh crash: {e}", context="UI_REFRESH")

    def load_data(self):
        """Full data load — rebuilds the active plans list and chart."""
        if sip.isdeleted(self): return

        try:
            # Stats
            stats = SavingsService.get_savings_stats(self.user_data['username'])
            self._clear_layout(self.stats_grid)
            self.stat_labels = {}
            self.add_stat_card("total_saved", safe_currency(stats['total_saved']), 0, 0)
            self.add_stat_card("active_plans", str(stats['active_plans']), 0, 1)
            self.add_stat_card("monthly_interest", safe_currency(stats['monthly_interest']), 0, 2)

            # Chart Data
            from src.services.savings_analytics_service import SavingsAnalyticsService
            growth_data = SavingsAnalyticsService.get_growth_data(self.user_data['username'])
            if self.chart and not sip.isdeleted(self.chart):
                self.chart.set_data(growth_data)

            # Plans
            self._clear_layout(self.plans_grid)
            self.plan_cards = {}
            plans = SavingsService.get_user_savings(self.user_data['username'])
            for i, plan in enumerate(plans):
                card = SavingsCard(plan)
                card.mousePressEvent = lambda e, p=plan: self.show_plan_detail(p)
                self.plan_cards[plan.id] = card
                self.plans_grid.addWidget(card, i // 2, i % 2)
        except Exception as e:
            DebugLogger.log_error(f"SavingsTab load_data crash: {e}", context="UI_LOAD")

    def update_ui(self):
        """Interface update bridge for DashboardWindow."""
        self.load_data()
    def add_stat_card(self, key, value, row, col):
        card = QFrame()
        l = QVBoxLayout(card)
        t = QLabel(self.lang_manager.get_text(key))
        v = QLabel(value)
        self.stat_labels[key] = v
        l.addWidget(t)
        l.addWidget(v)
        card.setStyleSheet(f"background: {theme.PANEL_BG}; border: 1px solid {theme.BORDER}; border-radius: 12px; padding: 15px;")
        t.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 12px; font-weight: 600;")
        v.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 20px; font-weight: 800;")
        self.stats_grid.addWidget(card, row, col)

    def handle_create_plan(self):
        try:
            dialog = CreateSavingsDialog(self)
            if dialog.exec():
                data = dialog.get_data()
                success, msg = SavingsService.create_savings_plan(
                    self.user_data['username'], **data
                )
                self.load_data()
                self.balance_updated.emit()
        except Exception as e:
            DebugLogger.log_error(f"handle_create_plan crash: {e}", context="DIALOG")

    def show_plan_detail(self, plan):
        try:
            dialog = SavingsDetailDialog(plan, self)
            dialog.exec()
            self.load_data()
            self.balance_updated.emit()
        except Exception as e:
            DebugLogger.log_error(f"show_plan_detail crash: {e}", context="DIALOG")

    def _clear_layout(self, layout):
        if not layout: return
        while layout.count():
            child = layout.takeAt(0)
            if child and child.widget():
                widget = child.widget()
                if widget:
                    widget.deleteLater()

    def update_theme(self):
        if sip.isdeleted(self): return
        styles = get_styles()
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")
        self.title_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 28px; font-weight: 800;")
        self.create_btn.setStyleSheet(styles["PRIMARY_BUTTON"])
        self.chart_card.setStyleSheet(f"background: {theme.CARD_BG}; border: 1px solid {theme.BORDER}; border-radius: 16px;")
        self.chart_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: 700; padding: 10px;")
        self.plans_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 20px; font-weight: 800;")
        
        if hasattr(self, 'chart') and self.chart and not sip.isdeleted(self.chart):
            self.chart.update()
