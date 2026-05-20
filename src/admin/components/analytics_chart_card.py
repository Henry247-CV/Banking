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
        self.setMinimumHeight(160)
        self.setMinimumWidth(250)

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
        padding_top = 25
        padding_sides = 15
        padding_bottom = 25
        
        chart_h = h - padding_top - padding_bottom
        chart_w = w - padding_sides * 2

        if len(self._data) == 0:
            painter.end()
            return

        max_val = max(v for _, v in self._data) if self._data else 1
        if max_val == 0:
            max_val = 1

        bar_count = len(self._data)
        gap = max(10, int(chart_w * 0.08))
        bar_w = (chart_w - gap * (bar_count + 1)) // bar_count
        bar_w = max(12, min(bar_w, 40)) # Limit bar width for better spacing

        # Re-calculate padding to center bars if they are thin
        total_bars_w = bar_count * bar_w + (bar_count + 1) * gap
        if total_bars_w < chart_w:
            padding_sides += (chart_w - total_bars_w) // 2

        # Draw grid lines
        grid_color = QColor(theme.BORDER)
        grid_color.setAlpha(40)
        painter.setPen(QPen(grid_color, 1))
        for i in range(4):
            y = padding_top + int(chart_h * i / 3)
            painter.drawLine(padding_sides, y, w - padding_sides, y)

        # Draw bars
        bar_color = QColor(self._bar_color)
        
        for i, (label, value) in enumerate(self._data):
            x = padding_sides + gap + i * (bar_w + gap)
            bar_h = int((value / max_val) * chart_h) if max_val > 0 else 0
            y = padding_top + chart_h - bar_h

            # Bar with rounded top
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bar_color))
            radius = min(4, bar_w // 3)
            painter.drawRoundedRect(
                QRectF(x, y, bar_w, bar_h),
                radius, radius
            )

            # Label below bar
            text_color = QColor(theme.TEXT_SECONDARY)
            painter.setPen(QPen(text_color))
            font = QFont("Segoe UI", 7)
            painter.setFont(font)
            
            # Shorten label: if "2024-05-20", show "20/05"
            short_label = label
            if "-" in label and len(label) >= 10:
                parts = label.split("-")
                short_label = f"{parts[2]}/{parts[1]}"
            elif len(label) > 6:
                short_label = label[-5:]
                
            painter.drawText(
                QRectF(x - gap//2, padding_top + chart_h + 4, bar_w + gap, 16),
                Qt.AlignmentFlag.AlignCenter, short_label
            )

            # Value on top of bar
            if value > 0:
                painter.setPen(QPen(QColor(theme.TEXT_PRIMARY)))
                font.setPointSize(7)
                font.setBold(True)
                painter.setFont(font)
                
                # Format large values
                val_str = str(value)
                if value >= 1000000: val_str = f"{value/1000000:.1f}M"
                elif value >= 1000: val_str = f"{value/1000:.1f}k"
                
                painter.drawText(
                    QRectF(x - gap//2, y - 18, bar_w + gap, 14),
                    Qt.AlignmentFlag.AlignCenter, val_str
                )

        painter.end()


class MiniDonutChart(QWidget):
    """Lightweight donut/ring chart rendered with QPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []   # list of (label, value, color)
        self.setMinimumHeight(160)
        self.setMinimumWidth(250)

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
        
        # Donut position (Left side)
        chart_size = min(h - 40, w // 2)
        cx = padding_left = 20 + chart_size // 2
        cy = h // 2
        outer_r = chart_size // 2
        inner_r = int(outer_r * 0.6)

        total = sum(v for _, v, _ in self._data)
        
        # Draw Arcs
        if total > 0:
            start_angle = 90 * 16
            for label, value, color_hex in self._data:
                if value <= 0: continue
                span = int((value / total) * 360 * 16)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(color_hex)))
                rect = QRectF(cx - outer_r, cy - outer_r, chart_size, chart_size)
                painter.drawPie(rect, start_angle, span)
                start_angle += span
        else:
            painter.setPen(QPen(QColor(theme.BORDER), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(cx - outer_r, cy - outer_r, chart_size, chart_size))

        # Cutout for Donut
        painter.setBrush(QBrush(QColor(theme.CARD_BG)))
        painter.setPen(Qt.PenStyle.NoPen)
        inner_size = inner_r * 2
        painter.drawEllipse(QRectF(cx - inner_r, cy - inner_r, inner_size, inner_size))

        # Center Total text
        painter.setPen(QPen(QColor(theme.TEXT_PRIMARY)))
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            QRectF(cx - inner_r, cy - 10, inner_size, 20),
            Qt.AlignmentFlag.AlignCenter, str(total)
        )

        # Legend (Right side)
        legend_x = cx + outer_r + 20
        legend_y = cy - (len([d for d in self._data if d[1] > 0]) * 20) // 2
        
        font = QFont("Segoe UI", 8)
        painter.setFont(font)
        
        for label, value, color_hex in self._data:
            if value < 0: continue # Allow 0 for legend display if needed, but here we skip negative
            
            # Color dot
            painter.setBrush(QBrush(QColor(color_hex)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(legend_x, legend_y + 4, 8, 8))
            
            # Label & Value
            painter.setPen(QPen(QColor(theme.TEXT_PRIMARY)))
            perc = (value / total * 100) if total > 0 else 0
            text = f"{label}: {value} ({perc:.0f}%)"
            
            painter.drawText(
                QRectF(legend_x + 15, legend_y, w - legend_x - 20, 16),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text
            )
            legend_y += 22

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
