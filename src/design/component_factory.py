"""Base UI Components — Reusable classes to ensure enterprise consistency."""
from PyQt6.QtWidgets import QFrame, QPushButton, QTableWidget, QDialog, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.design.design_tokens import Radius, Typography
import src.core.theme as theme

class BaseCard(QFrame):
    """Unified enterprise card component."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BaseCard")
        
    def update_theme(self):
        theme.update_globals()
        self.setStyleSheet(f"""
            QFrame#BaseCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: {Radius.CARD}px;
            }}
        """)

class BaseButton(QPushButton):
    """Unified enterprise button component.
    Variants: primary, secondary, danger, ghost
    """
    def __init__(self, text="", variant="primary", parent=None):
        super().__init__(text, parent)
        self.setObjectName("BaseButton")
        self.variant = variant
        self.setMinimumHeight(38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        font = QFont(Typography.FAMILY, Typography.BODY_SIZE, Typography.WEIGHT_SEMIBOLD)
        self.setFont(font)
        self.update_theme()

    def update_theme(self):
        theme.update_globals()
        
        bg_color = "transparent"
        text_color = theme.TEXT_PRIMARY
        border = f"1px solid {theme.BORDER}"
        hover_bg = theme.PANEL_BG
        hover_text = theme.TEXT_PRIMARY
        hover_border = f"1px solid {theme.CYAN}"
        
        if self.variant == "primary":
            bg_color = theme.CYAN
            text_color = theme.BACKGROUND
            border = "none"
            hover_bg = getattr(theme, "CYAN_HOVER", "#38BDF8")
            hover_border = "none"
        elif self.variant == "danger":
            bg_color = f"{theme.RED}20"
            text_color = theme.RED
            border = f"1px solid {theme.RED}40"
            hover_bg = theme.RED
            hover_text = "white"
            hover_border = f"1px solid {theme.RED}"
        elif self.variant == "ghost":
            border = "none"
            hover_bg = theme.PANEL_BG
            hover_border = "none"
            
        self.setStyleSheet(f"""
            QPushButton#BaseButton {{
                background-color: {bg_color};
                color: {text_color};
                border: {border};
                border-radius: {Radius.BUTTON}px;
                padding: 8px 14px;
            }}
            QPushButton#BaseButton:hover {{
                background-color: {hover_bg};
                color: {hover_text};
                border: {hover_border};
            }}
            QPushButton#BaseButton:disabled {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_SECONDARY};
                border: 1px dashed {theme.BORDER};
            }}
        """)

class BaseTable(QTableWidget):
    """Unified enterprise table component."""
    def __init__(self, rows=0, cols=0, parent=None):
        super().__init__(rows, cols, parent)
        self.setObjectName("BaseTable")
        self.setShowGrid(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setMouseTracking(True)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(42)
        font = QFont(Typography.FAMILY, Typography.BODY_SIZE)
        self.setFont(font)

    def update_theme(self):
        theme.update_globals()
        self.setStyleSheet(f"""
            QTableWidget#BaseTable {{
                background-color: {theme.CARD_BG};
                color: {theme.TEXT_PRIMARY};
                gridline-color: transparent;
                border: 1px solid {theme.BORDER};
                border-radius: {Radius.CARD}px;
            }}
            QTableWidget#BaseTable::item {{
                padding: 10px 12px;
                border-bottom: 1px solid {theme.BORDER};
            }}
            QTableWidget#BaseTable::item:selected {{
                background-color: {theme.PANEL_BG};
                color: {theme.CYAN};
            }}
            QTableWidget#BaseTable::item:hover {{
                background-color: {theme.PANEL_BG};
            }}
            QHeaderView::section {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_SECONDARY};
                padding: 12px;
                border: none;
                border-bottom: 2px solid {theme.BORDER};
                font-weight: {Typography.WEIGHT_BOLD};
                font-size: {Typography.SMALL_SIZE}px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)

class BaseDialog(QDialog):
    """Unified enterprise dialog component."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QFrame()
        self.container.setObjectName("BaseDialogContainer")
        self.container_layout = QVBoxLayout(self.container)
        self.main_layout.addWidget(self.container)

    def update_theme(self):
        theme.update_globals()
        self.container.setStyleSheet(f"""
            QFrame#BaseDialogContainer {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: {Radius.DIALOG}px;
            }}
        """)
