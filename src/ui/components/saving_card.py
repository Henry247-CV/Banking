from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.design.component_factory import BaseCard

class SavingCard(BaseCard):
    def __init__(self, goal_name, target, current):
        super().__init__()
        self.setObjectName("SavingCard")
        self.goal_name = goal_name
        self.target = target
        self.current = current
        self.setup_ui()
        self.update_theme()

    def update_theme(self):
        super().update_theme()
        self.setStyleSheet(self.styleSheet() + f"""
            QFrame#SavingCard:hover {{
                border: 1px solid {theme.CYAN};
            }}
        """)
        self.title_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 16px; font-weight: bold; border: none; background: transparent;")
        self.percent_label.setStyleSheet(f"color: {theme.CYAN}; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        self.amt_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 12px; border: none; background: transparent;")
        
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {theme.PANEL_BG};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {theme.CYAN};
                border-radius: 4px;
            }}
        """)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        self.title_label = QLabel(self.goal_name)
        
        percent = int((self.current / self.target) * 100) if self.target > 0 else 0
        self.percent_label = QLabel(f"{percent}%")
        
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.percent_label)

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(8)
        self.progress.setMaximum(100)
        self.progress.setValue(percent)
        self.progress.setTextVisible(False)

        # Amounts
        amounts = QHBoxLayout()
        current_formatted = "{:,.0f}".format(self.current)
        target_formatted = "{:,.0f}".format(self.target)
        
        self.amt_label = QLabel(f"{current_formatted} / {target_formatted} VND")
        
        amounts.addWidget(self.amt_label)
        amounts.addStretch()

        layout.addLayout(header)
        layout.addWidget(self.progress)
        layout.addLayout(amounts)
