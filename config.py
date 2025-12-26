# import pygame
#
# # --- WINDOW & UI ---
# WIDTH, HEIGHT = 1600, 900
# PANEL_LEFT_W = 320
# PANEL_RIGHT_W = 280
# PANEL_RIGHT_X = WIDTH - PANEL_RIGHT_W
# CELL_SIZE = 20
# MAX_PER_ROW = 3
# MARGIN_X = PANEL_LEFT_W + 50
# MARGIN_Y = 50
# SLOT_W = (6 * CELL_SIZE) * 2 + 60
# MAX_TRAY_PER_LAYER = 15
#
# # --- COLORS ---
# BG_COLOR = (30, 30, 30)
# PANEL_BG = (50, 50, 50)
# BORDER_COLOR = (100, 100, 100)
# TEXT_WHITE = (255, 255, 255)
#
# COLORS = [
#     (0, 120, 255),  # 0: Blue
#     (0, 200, 255),  # 1: Cyan
#     (50, 200, 50),  # 2: Green
#     (209, 141, 121),  # 3: Skin
#     (200, 0, 200),  # 4: Magenta
#     (255, 150, 0),  # 5: Orange
#     (150, 0, 255),  # 6: Purple
#     (255, 0, 0),  # 7: Red
#     (163, 162, 162),  # 8: White
#     (255, 255, 0)  # 9: Yellow
# ]
#
# COLOR_NAMES = [
#     "Blue", "Cyan", "Green", "Skin", "Magenta",
#     "Orange", "Purple", "Red", "White", "Yellow"
# ]
#
#
# # --- GAME STATE VARS (Shared) ---
# # Dùng class để quản lý state toàn cục dễ dàng hơn
# class State:
#     containers = []
#     undo_stack = []
#     selected_trays = []
#     selected_cells = []
#     paint_mode = False
#     last_action_message = "Ready"
#     active_cell = None
#     current_layer = 1
#     layer_checkbox = [False] * 5
#
#     # Config Params
#     tray_color_variety = 4
#     max_same_color = 4
#     shuffle_ratio = 50
#
#     # Ratio Table
#     ratio_ui_rows = [
#         {'size': '2x2', 'weight': '10', 'limit': '2'},
#         {'size': '2x3', 'weight': '15', 'limit': '2'},
#         {'size': '3x2', 'weight': '15', 'limit': '2'},
#         {'size': '3x3', 'weight': '15', 'limit': '3'},
#         {'size': '2x4', 'weight': '15', 'limit': '3'},
#         {'size': '4x2', 'weight': '10', 'limit': '3'},
#         {'size': '2x5', 'weight': '10', 'limit': '3'},
#         {'size': '5x2', 'weight': '10', 'limit': '3'},
#     ]
#
#
# state = State()
#
# # --- UI POSITIONS ---
# TABLE_X = 20
# TABLE_Y = 500
# COL_W_SIZE = 60
# COL_W_WEIGHT = 50
# COL_W_LIMIT = 50
# ROW_H = 25
# BTN_SIZE = 25
#
# BTN_X = PANEL_RIGHT_X + 20
# BTN_W = 240
# BTN_H = 35
# START_BTN_Y = 350
# SPACING_BTN = 45
#
# FILL_SAME_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y, BTN_W, BTN_H)
# AUTO_FILL_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y + SPACING_BTN, BTN_W, BTN_H)
# FILL_LAYER_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y + SPACING_BTN * 2, BTN_W, BTN_H)
# SHUFFLE_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y + SPACING_BTN * 3, BTN_W, BTN_H)
# CLEAR_LEVEL_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y + SPACING_BTN * 4, BTN_W, BTN_H)
#
# RATIO_LABEL_Y = START_BTN_Y + SPACING_BTN * 5 + 10
# RATIO_MINUS_RECT = pygame.Rect(BTN_X, RATIO_LABEL_Y + 25, 50, 30)
# RATIO_PLUS_RECT = pygame.Rect(BTN_X + 190, RATIO_LABEL_Y + 25, 50, 30)
#
#
# def generate_id(counter):
#     counter[0] += 1
#     return counter[0]


#######ver2#######
import pygame

# --- WINDOW & UI ---
WIDTH, HEIGHT = 1600, 900
PANEL_LEFT_W = 320
PANEL_RIGHT_W = 280
PANEL_RIGHT_X = WIDTH - PANEL_RIGHT_W
CELL_SIZE = 20
MAX_PER_ROW = 3
MARGIN_X = PANEL_LEFT_W + 50
MARGIN_Y = 50
SLOT_W = (6 * CELL_SIZE) * 2 + 60
MAX_TRAY_PER_LAYER = 15

# --- COLORS ---
BG_COLOR = (30, 30, 30)
PANEL_BG = (50, 50, 50)
BORDER_COLOR = (100, 100, 100)
TEXT_WHITE = (255, 255, 255)

COLORS = [
    (0, 120, 255), (0, 200, 255), (50, 200, 50), (209, 141, 121), (200, 0, 200),
    (255, 150, 0), (150, 0, 255), (255, 0, 0), (163, 162, 162), (255, 255, 0)
]

COLOR_NAMES = [
    "Blue", "Cyan", "Green", "Skin", "Magenta",
    "Orange", "Purple", "Red", "White", "Yellow"
]


# --- GAME STATE VARS ---
class State:
    containers = []
    undo_stack = []
    selected_trays = []
    selected_cells = []
    paint_mode = False
    last_action_message = "Ready"
    active_cell = None
    current_layer = 1
    layer_checkbox = [False] * 5

    # Config Params
    tray_color_variety = 4
    max_same_color = 4
    shuffle_ratio = 50
    symmetry_mode = False  # <--- Mode đối xứng

    # Ratio Table
    ratio_ui_rows = [
        {'size': '2x2', 'weight': '10', 'limit': '2'},
        {'size': '2x3', 'weight': '15', 'limit': '2'},
        {'size': '3x2', 'weight': '15', 'limit': '2'},
        {'size': '3x3', 'weight': '15', 'limit': '3'},
        {'size': '2x4', 'weight': '15', 'limit': '3'},
        {'size': '4x2', 'weight': '10', 'limit': '3'},
        {'size': '2x5', 'weight': '10', 'limit': '3'},
        {'size': '5x2', 'weight': '10', 'limit': '3'},
    ]


state = State()
color_limit = len(COLORS)
GLOBAL_CELL_LIMIT = 9999

# --- UI POSITIONS ---
TABLE_X = 20
TABLE_Y = 500
COL_W_SIZE = 60
COL_W_WEIGHT = 50
COL_W_LIMIT = 50
ROW_H = 25
BTN_SIZE = 25

BTN_X = PANEL_RIGHT_X + 20
BTN_W = 240
BTN_H = 35
START_BTN_Y = 320
SPACING_BTN = 45

# --- BUTTON RECTS ---
FILL_SAME_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y, BTN_W, BTN_H)
SORT_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y + SPACING_BTN, BTN_W, BTN_H)
AUTO_FILL_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y + SPACING_BTN * 2, BTN_W, BTN_H)
FILL_LAYER_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y + SPACING_BTN * 3, BTN_W, BTN_H)
SHUFFLE_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y + SPACING_BTN * 4, BTN_W, BTN_H)
CLEAR_LEVEL_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y + SPACING_BTN * 5, BTN_W, BTN_H)

# --- NÚT MỚI: SYMMETRY ---
SYMMETRY_BTN_RECT = pygame.Rect(BTN_X, START_BTN_Y + SPACING_BTN * 6, BTN_W, BTN_H)

# Controls (Đẩy xuống thấp hơn để không đè lên nút Symmetry)
RATIO_LABEL_Y = START_BTN_Y + SPACING_BTN * 7 + 10
RATIO_MINUS_RECT = pygame.Rect(BTN_X, RATIO_LABEL_Y + 5, 40, 30)
RATIO_PLUS_RECT = pygame.Rect(BTN_X + 150, RATIO_LABEL_Y + 5, 40, 30)


def generate_id(counter):
    counter[0] += 1
    return counter[0]