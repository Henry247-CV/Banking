from src.core.theme_manager import ThemeManager

def get_theme_colors():
    return ThemeManager().get_all_colors()

# This is a bit tricky because variables are already imported in many places.
# We will use a proxy object or just functions if needed.
# But for simplicity, we'll keep the names and update them via a function.

def update_globals():
    colors = get_theme_colors()
    global BACKGROUND, SIDEBAR_BG, PANEL_BG, CARD_BG, TEXT_PRIMARY, TEXT_SECONDARY, BORDER, CYAN, CYAN_HOVER, GREEN, RED, ORANGE, SHADOW
    BACKGROUND = colors["BACKGROUND"]
    SIDEBAR_BG = colors["SIDEBAR_BG"]
    PANEL_BG = colors["PANEL_BG"]
    CARD_BG = colors["CARD_BG"]
    TEXT_PRIMARY = colors["TEXT_PRIMARY"]
    TEXT_SECONDARY = colors["TEXT_SECONDARY"]
    BORDER = colors["BORDER"]
    CYAN = colors["CYAN"]
    CYAN_HOVER = colors["CYAN_HOVER"]
    GREEN = colors["GREEN"]
    RED = colors["RED"]
    ORANGE = colors["ORANGE"]
    SHADOW = colors["SHADOW"]

# Initial load
update_globals()

RADIUS = 14
SPACING = 12
FONT_LARGE = 24
FONT_MEDIUM = 16
FONT_SMALL = 12
