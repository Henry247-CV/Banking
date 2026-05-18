from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
)
from PyQt6.QtCore import Qt
import src.core.theme as theme
from src.core.theme_manager import ThemeManager


class AdminStatCard(QFrame):
    """Enterprise-style stat card for admin dashboard overview."""

    def __init__(self, title="", value="", trend_text="", icon="📊", accent_color=None):
        super().__init__()
        self.title_text = title
        self.value_text = value
        self.trend_text_str = trend_text
        self.icon_text = icon
        self.accent_color = accent_color
        self.theme_manager = ThemeManager()

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
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel(self.title_text)

        header_row.addWidget(self.icon_label)
        header_row.addWidget(self.title_label)
        header_row.addStretch()

        # Value
        self.value_label = QLabel(self.value_text)

        # Trend
        self.trend_label = QLabel(self.trend_text_str)

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
        theme.update_globals()
        accent = self.accent_color or theme.CYAN

        # Card background — slightly deeper than user cards for enterprise feel
        card_bg = theme.CARD_BG
        border_color = theme.BORDER
        text_primary = theme.TEXT_PRIMARY
        text_secondary = theme.TEXT_SECONDARY

        self.setStyleSheet(f"""
            AdminStatCard {{
                background-color: {card_bg};
                border: 1px solid {border_color};
                border-radius: 14px;
                border-left: 3px solid {accent};
            }}
            AdminStatCard:hover {{
                border: 1px solid {accent};
                border-left: 3px solid {accent};
            }}
        """)

        self.icon_label.setStyleSheet(f"""
            background-color: {theme.PANEL_BG};
            border-radius: 6px;
            font-size: 16px;
            border: 1px solid {border_color};
        """)

        self.title_label.setStyleSheet(f"""
            color: {text_secondary};
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            border: none;
            background: transparent;
        """)

        self.value_label.setStyleSheet(f"""
            color: {text_primary};
            font-size: 22px;
            font-weight: 800;
            border: none;
            background: transparent;
        """)

        trend_color = theme.GREEN if self.trend_text_str.startswith("+") or self.trend_text_str.startswith("↑") else accent
        self.trend_label.setStyleSheet(f"""
            color: {trend_color};
            font-size: 11px;
            font-weight: 600;
            border: none;
            background: transparent;
        """)
