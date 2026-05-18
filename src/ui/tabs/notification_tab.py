from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.ui.components.notification_card import NotificationCard
from src.services.notification_service import NotificationService
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager

class NotificationTab(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.notification_service = NotificationService()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setup_ui()
        self.update_theme()
        self.update_translations()

    def update_theme(self):
        styles = get_styles()
        self.scroll.verticalScrollBar().setStyleSheet(styles["GLOBAL_STYLE"])
        self.header_panel.setStyleSheet(f"background-color: {theme.PANEL_BG}; border-bottom: 1px solid {theme.BORDER};")
        self.title_lbl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 28px; font-weight: 800; border: none; background: transparent;")
        self.sub_lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 14px; border: none; background: transparent;")
        
        self.mark_read_btn.setStyleSheet(styles["SECONDARY_BUTTON"] + "font-size: 13px; font-weight: bold;")
        self.clear_btn.setStyleSheet(styles["SECONDARY_BUTTON"] + f"border-color: {theme.RED}; color: {theme.RED}; font-size: 13px; font-weight: bold;")

        for i in range(self.list_layout.count()):
            w = self.list_layout.itemAt(i).widget()
            if hasattr(w, "update_theme"): w.update_theme()

    def update_translations(self):
        self.title_lbl.setText(self.lang_manager.get_text("notifications"))
        self.mark_read_btn.setText("Mark All Read") # Add to lang if needed
        self.clear_btn.setText("Clear Inbox")

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header Section
        self.header_panel = QFrame()
        self.header_panel.setFixedHeight(120)
        header_layout = QHBoxLayout(self.header_panel)
        header_layout.setContentsMargins(30, 0, 30, 0)

        title_box = QVBoxLayout()
        self.title_lbl = QLabel("Notifications")
        self.sub_lbl = QLabel("Stay updated with your account activities.")
        title_box.addWidget(self.title_lbl)
        title_box.addWidget(self.sub_lbl)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.mark_read_btn = QPushButton("Mark All Read")
        self.mark_read_btn.setFixedSize(140, 40)
        self.mark_read_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mark_read_btn.clicked.connect(self.mark_all_read)
        
        self.clear_btn = QPushButton("Clear Inbox")
        self.clear_btn.setFixedSize(140, 40)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_all)
        
        btn_layout.addWidget(self.mark_read_btn)
        btn_layout.addWidget(self.clear_btn)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addLayout(btn_layout)
        
        self.main_layout.addWidget(self.header_panel)

        # Notification List (Scroll Area)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(30, 30, 30, 30)
        self.list_layout.setSpacing(15)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.list_container)
        self.main_layout.addWidget(self.scroll)

        self.load_notifications()

    def load_notifications(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tier = self.user_data.get('customer_tier', 'STANDARD')
        notifications = self.notification_service.get_user_notifications(self.user_data['username'], tier)
        
        if not notifications:
            empty_container = QFrame()
            empty_layout = QVBoxLayout(empty_container)
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addSpacing(100)

            icon = QLabel("📭")
            icon.setStyleSheet("font-size: 64px;")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            lbl = QLabel(self.lang_manager.get_text("no_alerts"))
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 16px; font-weight: 500;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            empty_layout.addWidget(icon)
            empty_layout.addWidget(lbl)
            self.list_layout.addWidget(empty_container)
            return

        for n in notifications:
            # n[0]: id, n[1]: title, n[2]: message, n[3]: type, n[4]: is_read, n[5]: created_at, n[6]: priority
            card = NotificationCard(
                title=n[1], message=n[2], timestamp=n[5], 
                is_read=(n[4] == 1), priority=n[6], n_type=n[3]
            )
            self.list_layout.addWidget(card)

    def mark_all_read(self):
        if self.notification_service.mark_all_as_read(self.user_data['username']):
            self.load_notifications()

    def clear_all(self):
        confirm = QMessageBox.question(self, "Clear All", "Are you sure you want to delete all notifications?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            if self.notification_service.clear_notifications(self.user_data['username']):
                self.load_notifications()

    def update_ui(self):
        self.load_notifications()
