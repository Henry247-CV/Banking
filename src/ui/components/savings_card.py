from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QProgressBar, QPushButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
from datetime import datetime
from src.core import theme
from src.core.language_manager import LanguageManager
from src.models.savings_model import SavingsAccount

class SavingsCard(QFrame):
    clicked = pyqtSignal(str) # Emits savings_id

    def __init__(self, plan: SavingsAccount):
        super().__init__()
        self.plan = plan
        self.lang_manager = LanguageManager()
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(300, 180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("savingsCard")
        
        self.setStyleSheet(f"""
            QFrame#savingsCard {{
                background-color: {theme.PANEL_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 20px;
            }}
            QFrame#savingsCard:hover {{
                border: 1px solid {theme.CYAN};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header: Icon + Plan Name
        header = QHBoxLayout()
        icon_label = QLabel("💰")
        icon_label.setStyleSheet("font-size: 24px;")
        
        name_label = QLabel(self.plan.plan_name)
        name_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        
        header.addWidget(icon_label)
        header.addWidget(name_label)
        header.addStretch()
        
        type_tag = QLabel(self.lang_manager.get_text(self.plan.savings_type.lower() + "_savings"))
        type_tag.setStyleSheet(f"""
            background-color: {theme.CYAN}22;
            color: {theme.CYAN};
            border-radius: 8px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: bold;
        """)
        header.addWidget(type_tag)
        
        layout.addLayout(header)

        # Progress Section
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(6)
        
        # Amounts
        amount_layout = QHBoxLayout()
        current_label = QLabel(f"{self.plan.current_amount:,.0f} VND")
        current_label.setStyleSheet(f"color: {theme.CYAN}; font-size: 14px; font-weight: 800;")
        
        target_label = QLabel(f"/ {self.plan.target_amount:,.0f}")
        target_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 12px;")
        
        amount_layout.addWidget(current_label)
        amount_layout.addWidget(target_label)
        amount_layout.addStretch()
        
        progress_layout.addLayout(amount_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        # Ensure we don't divide by zero and cap at 100%
        target = self.plan.target_amount if self.plan.target_amount > 0 else 1
        percentage = min(100, int((self.plan.current_amount / target) * 100))
        self.progress_bar.setValue(percentage)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        
        # Dynamic color based on progress
        progress_color = theme.CYAN
        if percentage >= 100:
            progress_color = theme.GREEN
        elif percentage < 20:
            progress_color = theme.ORANGE

        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {theme.BORDER};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {progress_color};
                border-radius: 4px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addLayout(progress_layout)
        
        # Footer: Stats
        footer = QHBoxLayout()
        
        interest_label = QLabel(f"📈 {self.plan.interest_rate*100:.1f}% APR")
        interest_label.setStyleSheet(f"color: {theme.GREEN}; font-size: 11px; font-weight: bold;")
        
        # Calculate remaining days
        days_left = 0
        if self.plan.end_date:
            try:
                end_dt = datetime.strptime(self.plan.end_date, "%Y-%m-%d %H:%M:%S")
                days_left = max(0, (end_dt - datetime.now()).days)
            except: pass
            
        time_label = QLabel(f"⏳ {days_left}d left")
        time_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 11px;")
        
        footer.addWidget(interest_label)
        footer.addStretch()
        footer.addWidget(time_label)
        
        layout.addLayout(footer)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.plan.savings_id)
        super().mousePressEvent(event)
