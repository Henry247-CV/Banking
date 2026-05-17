import src.core.theme as theme

def get_styles():
    theme.update_globals()
    
    return {
        "PRIMARY_BUTTON": f"""
            QPushButton {{
                background-color: {theme.CYAN};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
                min-height: 46px;
            }}
            QPushButton:hover {{
                background-color: {theme.CYAN_HOVER};
            }}
        """,
        "SECONDARY_BUTTON": f"""
            QPushButton {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                min-height: 46px;
            }}
            QPushButton:hover {{
                border: 1px solid {theme.CYAN};
                background-color: {theme.CARD_BG};
            }}
        """,
        "LINE_EDIT_STYLE": f"""
            QLineEdit {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                min-height: 44px;
            }}
            QLineEdit:focus {{
                border: 1px solid {theme.CYAN};
                background-color: {theme.CARD_BG};
            }}
        """,
        "CARD_STYLE": f"""
            QFrame {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-radius: 20px;
            }}
        """,
        "GLOBAL_STYLE": f"""
            QMainWindow, QWidget {{
                background-color: {theme.BACKGROUND};
                color: {theme.TEXT_PRIMARY};
                font-family: 'Segoe UI', sans-serif;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {theme.BACKGROUND};
                width: 10px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme.BORDER};
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme.CYAN};
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {theme.BACKGROUND};
                height: 10px;
            }}
            QScrollBar::handle:horizontal {{
                background: {theme.BORDER};
                border-radius: 5px;
            }}
        """
    }

# Keep existing constants for backward compatibility if needed, 
# but they won't be dynamic unless get_styles() is called.
styles = get_styles()
PRIMARY_BUTTON = styles["PRIMARY_BUTTON"]
SECONDARY_BUTTON = styles["SECONDARY_BUTTON"]
LINE_EDIT_STYLE = styles["LINE_EDIT_STYLE"]
CARD_STYLE = styles["CARD_STYLE"]
GLOBAL_STYLE = styles["GLOBAL_STYLE"]
