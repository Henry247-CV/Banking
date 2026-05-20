from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QPainterPath
import src.core.theme as theme

class SavingsChart(QWidget):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or [] 
        self.setMinimumHeight(180)

    def set_data(self, data):
        self._data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        padding_left = 60
        padding_right = 30
        padding_top = 20
        padding_bottom = 40
        
        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom
        
        # 1. Background Grid & Y-Axis Labels
        max_val = max(self._data) if self._data else 0
        if max_val == 0: max_val = 1000000 # Default range for visual
        
        grid_pen = QPen(QColor(theme.BORDER), 1, Qt.PenStyle.DashLine)
        painter.setFont(QFont("Segoe UI", 8))
        
        for i in range(4): # 4 horizontal lines
            y = padding_top + (i * chart_h / 3)
            painter.setPen(grid_pen)
            painter.drawLine(int(padding_left), int(y), int(w - padding_right), int(y))
            
            # Y-Axis Label
            painter.setPen(QPen(QColor(theme.TEXT_SECONDARY)))
            val_y = max_val - (i * max_val / 3)
            painter.drawText(QRectF(0, y - 10, padding_left - 10, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{int(val_y/1000)}k")

        if not self._data or len(self._data) < 2:
            painter.setPen(QPen(QColor(theme.TEXT_SECONDARY), 1))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No savings history yet")
            return
        
        points = []
        for i, val in enumerate(self._data):
            x = padding_left + (i * chart_w / (len(self._data) - 1))
            y = padding_top + chart_h - (val * chart_h / max_val)
            points.append(QPointF(x, y))
            
            # X-Axis Labels (Date placeholders)
            if i % 2 == 0:
                painter.setPen(QPen(QColor(theme.TEXT_SECONDARY)))
                painter.drawText(QRectF(x - 20, h - padding_bottom + 5, 40, 20), Qt.AlignmentFlag.AlignCenter, f"D{i+1}")
            
        # 2. Draw Area (Gradient)
        path = QPainterPath()
        path.moveTo(points[0])
        for i in range(1, len(points)):
            path.lineTo(points[i])
            
        fill_path = QPainterPath(path)
        fill_path.lineTo(points[-1].x(), padding_top + chart_h)
        fill_path.lineTo(points[0].x(), padding_top + chart_h)
        fill_path.closeSubpath()
        
        grad = QLinearGradient(0, padding_top, 0, padding_top + chart_h)
        c_green = QColor(theme.GREEN)
        c_green.setAlpha(60)
        grad.setColorAt(0, c_green)
        c_green.setAlpha(0)
        grad.setColorAt(1, c_green)
        
        painter.fillPath(fill_path, QBrush(grad))
        
        # 3. Draw Main Line
        painter.setPen(QPen(QColor(theme.GREEN), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)
        
        # 4. Draw Points
        painter.setPen(QPen(QColor(theme.BACKGROUND), 2))
        painter.setBrush(QBrush(QColor(theme.GREEN)))
        for p in points:
            painter.drawEllipse(p, 4, 4)
            
        painter.end()
