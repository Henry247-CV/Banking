from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
)
from PyQt6.QtCore import Qt
import src.core.theme as theme
from src.core.theme_manager import ThemeManager
from src.design.component_factory import BaseCard


class AdminStatCard(BaseCard):
    """Enterprise-style stat card for admin dashboard overview."""

    def __init__(self, title="", value="", trend_text="", icon="📊", accent_color=None):
        super().__init__()
        self.title_text = title
        self.value_text = value
        self.trend_text_str = trend_text
        self.icon_text = icon
        self.accent_color = accent_color
        self.theme_manager = ThemeManager()

        self.setObjectName("AdminStatCard")
        self.setMinimumHeight(120)
        self.setMaximumHeight(160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        # Top row: icon + title
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        self.icon_label = QLabel(self.icon_text)
        self.icon_label.setObjectName("AdminStatIcon")
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel(self.title_text)
        self.title_label.setObjectName("AdminStatTitle")

        header_row.addWidget(self.icon_label)
        header_row.addWidget(self.title_label)
        header_row.addStretch()

        # Value
        self.value_label = QLabel(self.value_text)
        self.value_label.setObjectName("AdminStatValue")

        # Trend
        self.trend_label = QLabel(self.trend_text_str)
        self.trend_label.setObjectName("AdminStatTrend")

        layout.addLayout(header_row)
        layout.addStretch()
        layout.addWidget(self.value_label)
        if self.trend_text_str:
            layout.addWidget(self.trend_label)

    def set_value(self, value):
        """Update the displayed value."""
        self.value_text = value
        self.value_label.setText(value)

    def set_trend(self, trend):
        """Update the trend text."""
        self.trend_text_str = trend
        self.trend_label.setText(trend)
        self.trend_label.setVisible(bool(trend))

    def update_theme(self):
        super().update_theme()
        theme.update_globals()
        accent = self.accent_color or theme.CYAN

        self.setStyleSheet(self.styleSheet() + f"""
            QFrame#AdminStatCard {{
                border-left: 3px solid {accent};
            }}
            QFrame#AdminStatCard:hover {{
                border: 1px solid {accent};
                border-left: 3px solid {accent};
            }}
            QLabel#AdminStatIcon {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border-radius: 6px;
                font-size: 16px;
                border: 1px solid {theme.BORDER};
            }}
            QLabel#AdminStatTitle {{
                color: {theme.TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }}
            QLabel#AdminStatValue {{
                color: {theme.TEXT_PRIMARY};
                font-size: 22px;
                font-weight: 800;
            }}
            QLabel#AdminStatTrend {{
                color: {accent if not (self.trend_text_str.startswith('+') or self.trend_text_str.startswith('↑')) else theme.GREEN};
                font-size: 11px;
                font-weight: 600;
            }}
        """)
