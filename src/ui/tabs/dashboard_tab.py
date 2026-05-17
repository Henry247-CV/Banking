from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.core.theme import *
from src.core.styles import *
from src.ui.components.dashboard_cards import OverviewCard, QuickActionButton
from src.ui.components.transaction_table import TransactionTable
from src.ui.components.notification_card import NotificationCard
from src.ui.components.saving_card import SavingCard
from src.services.transfer_service import TransferService
from src.services.notification_service import NotificationService
from src.services.saving_service import SavingService

from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager

class DashboardTab(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.transfer_service = TransferService()
        self.notification_service = NotificationService()
        self.saving_service = SavingService()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setup_ui()
        self.update_theme()
        self.update_translations()

    def update_theme(self):
        styles = get_styles()
        self.scroll.verticalScrollBar().setStyleSheet(styles["GLOBAL_STYLE"])
        self.welcome_card.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {theme.PANEL_BG}, stop: 1 {theme.BACKGROUND}
                );
                border-radius: 24px;
                border: 1px solid {theme.BORDER};
            }}
        """)
        self.welcome_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 16px; font-weight: 500; border: none; background: transparent;")
        self.user_name_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 32px; font-weight: 800; border: none; background: transparent;")
        self.welcome_sub.setStyleSheet(f"color: {theme.CYAN}; font-size: 14px; font-weight: 500; border: none; background: transparent;")
        
        self.trans_container.setStyleSheet(styles["CARD_STYLE"])
        self.trans_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        self.trans_table.update_theme()

        self.notify_container.setStyleSheet(styles["CARD_STYLE"])
        self.notify_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        
        self.savings_container.setStyleSheet(styles["CARD_STYLE"])
        self.savings_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        
        self.actions_container.setStyleSheet(styles["CARD_STYLE"])
        self.actions_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        
        # Refresh child items theme
        for i in range(self.notify_preview_layout.count()):
            w = self.notify_preview_layout.itemAt(i).widget()
            if hasattr(w, "update_theme"): w.update_theme()

        for i in range(self.savings_preview_layout.count()):
            w = self.savings_preview_layout.itemAt(i).widget()
            if hasattr(w, "update_theme"): w.update_theme()

        self.refresh_balance_cards()

    def update_translations(self):
        self.welcome_lbl.setText(self.lang_manager.get_text("welcome_back"))
        self.welcome_sub.setText(self.lang_manager.get_text("manage_finances"))
        self.trans_title.setText(self.lang_manager.get_text("recent_transactions"))
        self.notify_title.setText(self.lang_manager.get_text("notifications"))
        self.savings_title.setText(self.lang_manager.get_text("savings_progress"))
        self.actions_title.setText(self.lang_manager.get_text("quick_actions"))
        
        # Actions need translation too
        for i in range(self.actions_list_layout.count()):
            widget = self.actions_list_layout.itemAt(i).widget()
            if isinstance(widget, QuickActionButton):
                widget.update_translation()
        
        self.refresh_balance_cards()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(f"background-color: transparent;")
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(30, 30, 30, 30)
        self.container_layout.setSpacing(30)

        # 1. Welcome Card
        self.welcome_card = QFrame()
        self.welcome_card.setFixedHeight(160)
        welcome_layout = QVBoxLayout(self.welcome_card)
        welcome_layout.setContentsMargins(40, 0, 40, 0)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.welcome_lbl = QLabel("Welcome back,")
        display_name = self.user_data['full_name'] if self.user_data['full_name'] else self.user_data['username']
        self.user_name_label = QLabel(display_name)
        self.welcome_sub = QLabel("Manage your finances securely")

        welcome_layout.addWidget(self.welcome_lbl)
        welcome_layout.addWidget(self.user_name_label)
        welcome_layout.addWidget(self.welcome_sub)
        self.container_layout.addWidget(self.welcome_card)

        # 2. Overview Row
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(20)
        self.container_layout.addLayout(self.cards_layout)

        # 3. Middle Section
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(30)

        self.trans_container = QFrame()
        trans_layout = QVBoxLayout(self.trans_container)
        trans_layout.setContentsMargins(25, 25, 25, 25)
        self.trans_title = QLabel("Recent Transactions")
        trans_layout.addWidget(self.trans_title)
        self.trans_table = TransactionTable(rows=5, cols=5)
        trans_layout.addWidget(self.trans_table)
        middle_layout.addWidget(self.trans_container, 65)

        self.notify_container = QFrame()
        notify_layout = QVBoxLayout(self.notify_container)
        notify_layout.setContentsMargins(25, 25, 25, 25)
        self.notify_title = QLabel("Notifications")
        notify_layout.addWidget(self.notify_title)
        self.notify_preview_layout = QVBoxLayout()
        notify_layout.addLayout(self.notify_preview_layout)
        middle_layout.addWidget(self.notify_container, 35)
        self.container_layout.addLayout(middle_layout)

        # 4. Bottom Section
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(30)

        self.savings_container = QFrame()
        savings_layout = QVBoxLayout(self.savings_container)
        savings_layout.setContentsMargins(25, 25, 25, 25)
        self.savings_title = QLabel("Savings Progress")
        savings_layout.addWidget(self.savings_title)
        self.savings_preview_layout = QVBoxLayout()
        savings_layout.addLayout(self.savings_preview_layout)
        bottom_layout.addWidget(self.savings_container, 65)

        self.actions_container = QFrame()
        actions_layout = QVBoxLayout(self.actions_container)
        actions_layout.setContentsMargins(25, 25, 25, 25)
        self.actions_title = QLabel("Quick Actions")
        actions_layout.addWidget(self.actions_title)
        self.actions_list_layout = QVBoxLayout()
        actions_layout.addLayout(self.actions_list_layout)
        
        actions = [
            ("transfer_money", "💸"),
            ("add_wallet", "💳"),
            ("view_bills", "📄"),
            ("create_savings", "🎯")
        ]
        for key, icon in actions:
            btn = QuickActionButton(key, icon)
            self.actions_list_layout.addWidget(btn)
        
        bottom_layout.addWidget(self.actions_container, 35)
        self.container_layout.addLayout(bottom_layout)

        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)
        self.refresh_all()

    def refresh_balance_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        from src.ui.components.dashboard_cards import OverviewCard, TierOverviewCard
        
        formatted_balance = "{:,.0f} VND".format(self.user_data['balance'])
        balance_card = OverviewCard(self.lang_manager.get_text("total_balance"), formatted_balance, icon="💰")
        tier_card = TierOverviewCard(self.user_data.get('customer_tier', 'STANDARD'))
        expense_card = OverviewCard(self.lang_manager.get_text("monthly_expense"), "4,200,000 VND", color=theme.RED, icon="📈")
        savings_card = OverviewCard(self.lang_manager.get_text("total_savings"), "45,000,000 VND", color=theme.ORANGE, icon="🎯")

        self.cards_layout.addWidget(balance_card)
        self.cards_layout.addWidget(tier_card)
        self.cards_layout.addWidget(expense_card)
        self.cards_layout.addWidget(savings_card)

    def refresh_transactions(self):
        transactions = self.transfer_service.get_user_transactions(self.user_data['username'])
        formatted_trans = []
        for t in transactions[:5]:
            formatted_trans.append((t[0], t[1], t[2], -t[3], t[4]))
        self.trans_table.load_data(formatted_trans)

    def refresh_notifications(self):
        while self.notify_preview_layout.count():
            item = self.notify_preview_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        notifications = self.notification_service.get_user_notifications(self.user_data['username'])
        if not notifications:
            lbl = QLabel("No recent alerts.")
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: 500;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notify_preview_layout.addWidget(lbl)
            return

        for n in notifications[:3]:
            card = NotificationCard(n[1], n[2], n[5], is_read=(n[4] == 1))
            card.setFixedHeight(85) 
            self.notify_preview_layout.addWidget(card)

    def refresh_savings(self):
        while self.savings_preview_layout.count():
            item = self.savings_preview_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        savings = self.saving_service.get_user_savings(self.user_data['username'])
        if not savings:
            lbl = QLabel("No active saving goals.")
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: 500;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.savings_preview_layout.addWidget(lbl)
            return

        for s in savings[:2]:
            card = SavingCard(s[1], s[2], s[3])
            self.savings_preview_layout.addWidget(card)

    def refresh_all(self):
        self.refresh_balance_cards()
        self.refresh_transactions()
        self.refresh_notifications()
        self.refresh_savings()

    def update_ui(self):
        display_name = self.user_data['full_name'] if self.user_data['full_name'] else self.user_data['username']
        self.user_name_label.setText(display_name)
        self.refresh_all()
