"""Design Tokens — Centralized typography, radius, and animation constants."""

# Typography Hierarchy
class Typography:
    FAMILY = '"Segoe UI", "Noto Sans", Arial, sans-serif'
    
    # Sizes
    H1_SIZE = 28  # Page Title
    H2_SIZE = 20  # Section Title
    H3_SIZE = 16  # Card Title
    BODY_SIZE = 13 # Body Text
    SMALL_SIZE = 11 # Small/Detail Text
    
    # Weights
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700
    WEIGHT_EXTRABOLD = 800

# Border Radius
class Radius:
    CARD = 18
    DIALOG = 16
    BUTTON = 8
    INPUT = 8
    BADGE = 12

# Icon Sizes
class IconSize:
    SMALL = 16
    MEDIUM = 20
    LARGE = 24
    XLARGE = 32

# Animation
class Animation:
    HOVER_DURATION = 150 # ms
    FADE_DURATION = 200 # ms
