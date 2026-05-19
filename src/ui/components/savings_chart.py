"""
Savings Chart Component — Đăng Khoa Bank
Lightweight QPainter-based chart for savings analytics.
"""

from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush
from src.core.theme import CYAN, BORDER, TEXT_SECONDARY
from src.core import theme

class SavingsBarChart(QWidget):
    """Bar chart for savings growth and deposits."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = [] # list of (label, value)
        self._bar_color = CYAN
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, data, color=None):
        self._data = data
        if color:
            self._bar_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        padding_top = 40
        padding_bottom = 40
        padding_side = 30
        chart_h = h - padding_top - padding_bottom
        chart_w = w - padding_side * 2

        if not self._data or (len(self._data) == 1 and self._data[0][0] == "No Data"):
            painter.setPen(QPen(QColor(TEXT_SECONDARY)))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No savings data available")
            painter.end()
            return

        max_val = max(v for _, v in self._data) if self._data else 1
        if max_val == 0: max_val = 1
        max_val *= 1.2 # Headroom

        bar_count = len(self._data)
        gap = 15
        bar_w = max(10, (chart_w - gap * (bar_count + 1)) // bar_count)

        # Draw Grid
        grid_color = QColor(BORDER)
        grid_color.setAlpha(40)
        grid_pen = QPen(grid_color, 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        for i in range(5):
            y = padding_top + int(chart_h * i / 4)
            painter.drawLine(padding_side, y, w - padding_side, y)
            
            # Grid labels
            val = max_val * (4-i) / 4
            painter.setPen(QPen(QColor(TEXT_SECONDARY)))
            painter.setFont(QFont("Segoe UI", 7))
            painter.drawText(QRectF(5, y-10, padding_side-10, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{val/1e6:.1f}M")
            painter.setPen(grid_pen)

        # Draw Bars
        for i, (label, value) in enumerate(self._data):
            x = padding_side + gap + i * (bar_w + gap)
            bar_h = int((value / max_val) * chart_h)
            y = padding_top + chart_h - bar_h

            # Bar Gradient
            grad = QColor(self._bar_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(QRectF(x, y, bar_w, bar_h), 6, 6)

            # Value text on hover or always
            if bar_w > 30:
                painter.setPen(QPen(QColor(TEXT_SECONDARY)))
                painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
                painter.drawText(
                    QRectF(x - gap//2, y - 20, bar_w + gap, 20),
                    Qt.AlignmentFlag.AlignCenter, f"{value/1e6:.1f}M"
                )

            # Label
            painter.setPen(QPen(QColor(TEXT_SECONDARY)))
            painter.setFont(QFont("Segoe UI", 8))
            # Rotate label if too many bars
            if bar_count > 6:
                painter.save()
                painter.translate(x + bar_w/2, padding_top + chart_h + 10)
                painter.rotate(45)
                painter.drawText(0, 0, label)
                painter.restore()
            else:
                painter.drawText(
                    QRectF(x - gap//2, padding_top + chart_h + 5, bar_w + gap, 20),
                    Qt.AlignmentFlag.AlignCenter, label
                )

        painter.end()
