"""Analytics Chart Card — Lightweight QPainter-based chart widgets for admin dashboard.

No external dependencies. Uses pure Qt painting for:
- Bar charts (daily transactions, user growth)
- Donut charts (tier distribution, risk distribution)
All charts are theme-aware and responsive.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush
import math
import src.core.theme as theme
from src.core.theme_manager import ThemeManager


class MiniBarChart(QWidget):
    """Lightweight bar chart rendered with QPainter. Zero dependencies."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []   # list of (label, value)
        self._bar_color = "#00D4AA"
        self.setMinimumHeight(120)
        self.setMinimumWidth(200)

    def set_data(self, data, bar_color="#00D4AA"):
        """data: list of (label, value) tuples."""
        self._data = data
        self._bar_color = bar_color
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme.update_globals()
        is_dark = ThemeManager().current_theme == "dark"

        w = self.width()
        h = self.height()
        padding = 8
        label_h = 16
        chart_h = h - padding * 2 - label_h
        chart_w = w - padding * 2

        if len(self._data) == 0:
            painter.end()
            return

        max_val = max(v for _, v in self._data) if self._data else 1
        if max_val == 0:
            max_val = 1

        bar_count = len(self._data)
        gap = max(2, int(chart_w * 0.05))
        bar_w = max(6, (chart_w - gap * (bar_count + 1)) // bar_count)

        # Draw grid lines
        grid_color = QColor(theme.BORDER)
        grid_color.setAlpha(60)
        painter.setPen(QPen(grid_color, 1))
        for i in range(4):
            y = padding + int(chart_h * i / 3)
            painter.drawLine(padding, y, w - padding, y)

        # Draw bars
        bar_color = QColor(self._bar_color)
        hover_color = QColor(self._bar_color)
        hover_color.setAlpha(180)

        for i, (label, value) in enumerate(self._data):
            x = padding + gap + i * (bar_w + gap)
            bar_h = int((value / max_val) * chart_h) if max_val > 0 else 0
            y = padding + chart_h - bar_h

            # Bar with rounded top
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bar_color))
            radius = min(3, bar_w // 2)
            painter.drawRoundedRect(
                QRectF(x, y, bar_w, bar_h),
                radius, radius
            )

            # Label below bar
            text_color = QColor(theme.TEXT_SECONDARY)
            painter.setPen(QPen(text_color))
            font = QFont("Segoe UI", 7)
            painter.setFont(font)
            # Show last chars of date label
            short_label = label[-5:] if len(label) > 5 else label
            painter.drawText(
                QRectF(x - 2, padding + chart_h + 2, bar_w + 4, label_h),
                Qt.AlignmentFlag.AlignCenter, short_label
            )

            # Value on top of bar
            if bar_h > 14:
                painter.setPen(QPen(QColor("#FFFFFF" if is_dark else "#1A1A2E")))
                font.setPointSize(7)
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(
                    QRectF(x, y - 14, bar_w, 14),
                    Qt.AlignmentFlag.AlignCenter, str(value)
                )

        painter.end()


class MiniDonutChart(QWidget):
    """Lightweight donut/ring chart rendered with QPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []   # list of (label, value, color)
        self.setMinimumHeight(130)
        self.setMinimumWidth(130)

    def set_data(self, data):
        """data: list of (label, value, color_hex) tuples."""
        self._data = data
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme.update_globals()

        w = self.width()
        h = self.height()
        size = min(w, h) - 16
        if size < 40:
            painter.end()
            return

        cx = w // 2
        cy = h // 2
        outer_r = size // 2
        inner_r = int(outer_r * 0.55)

        total = sum(v for _, v, _ in self._data)
        if total == 0:
            # Draw empty ring
            painter.setPen(QPen(QColor(theme.BORDER), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(cx - outer_r, cy - outer_r, size, size))
            painter.end()
            return

        # Draw arcs
        start_angle = 90 * 16  # Start from top
        for label, value, color_hex in self._data:
            if value <= 0:
                continue
            span = int((value / total) * 360 * 16)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(color_hex)))

            rect = QRectF(cx - outer_r, cy - outer_r, size, size)
            painter.drawPie(rect, start_angle, span)
            start_angle += span

        # Cut out center for donut effect
        bg_color = QColor(theme.CARD_BG)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        inner_size = inner_r * 2
        painter.drawEllipse(QRectF(cx - inner_r, cy - inner_r, inner_size, inner_size))

        # Center text — total
        painter.setPen(QPen(QColor(theme.TEXT_PRIMARY)))
        font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            QRectF(cx - inner_r, cy - 10, inner_size, 20),
            Qt.AlignmentFlag.AlignCenter, str(total)
        )

        # Legend below
        painter.setPen(QPen(QColor(theme.TEXT_SECONDARY)))
        font = QFont("Segoe UI", 7)
        painter.setFont(font)
        legend_y = cy + outer_r + 4
        legend_x = 4
        for label, value, color_hex in self._data:
            if value <= 0:
                continue
            # Color dot
            painter.setBrush(QBrush(QColor(color_hex)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(legend_x, legend_y, 6, 6))
            # Label
            painter.setPen(QPen(QColor(theme.TEXT_SECONDARY)))
            text = f"{label}: {value}"
            painter.drawText(
                QRectF(legend_x + 9, legend_y - 2, 80, 12),
                Qt.AlignmentFlag.AlignLeft, text
            )
            legend_x += max(60, len(text) * 6 + 14)

        painter.end()


class AnalyticsChartCard(QFrame):
    """Card container for a chart widget with title."""

    def __init__(self, title="Chart", chart_widget=None):
        super().__init__()
        self._title_text = title
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        layout.addWidget(self.title_label)

        self.chart = chart_widget or QWidget()
        layout.addWidget(self.chart)

        self.update_theme()

    def set_title(self, title):
        self._title_text = title
        self.title_label.setText(title)

    def update_theme(self):
        theme.update_globals()
        self.setStyleSheet(f"""
            AnalyticsChartCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 10px;
            }}
        """)
        self.title_label.setStyleSheet(f"""
            color: {theme.TEXT_PRIMARY}; font-size: 13px;
            font-weight: 700; border: none; background: transparent;
        """)
        if hasattr(self.chart, 'update'):
            self.chart.update()  # Trigger repaint
