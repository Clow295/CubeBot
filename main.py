# import pygame
# from config import *
# from logic_core import *
# from ui import *
# from logic_export import export_to_unity_json
#
# pygame.init()
# SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("ColorCube Tool - Modular V1")
# CLOCK = pygame.time.Clock()
#
# running = True
# while running:
#     SCREEN.fill(BG_COLOR)
#     draw_panels(SCREEN)
#
#     events = pygame.event.get()
#     for e in events:
#         if e.type == pygame.QUIT: running = False
#
#         if e.type == pygame.MOUSEBUTTONDOWN:
#             mx, my = pygame.mouse.get_pos()
#
#             # --- LEFT PANEL ---
#             if mx < PANEL_LEFT_W:
#                 clicked = None
#                 for r, row in enumerate(state.ratio_ui_rows):
#                     y = TABLE_Y + 25 + r * ROW_H
#                     rects = [
#                         pygame.Rect(TABLE_X, y, COL_W_SIZE, ROW_H),
#                         pygame.Rect(TABLE_X + COL_W_SIZE, y, COL_W_WEIGHT, ROW_H),
#                         pygame.Rect(TABLE_X + COL_W_SIZE + COL_W_WEIGHT, y, COL_W_LIMIT, ROW_H)
#                     ]
#                     for c, rct in enumerate(rects):
#                         if rct.collidepoint(mx, my): clicked = [r, c]
#                 state.active_cell = clicked
#
#                 bp = pygame.Rect(TABLE_X + 160, TABLE_Y, BTN_SIZE, BTN_SIZE)
#                 bm = pygame.Rect(TABLE_X + 190, TABLE_Y, BTN_SIZE, BTN_SIZE)
#                 if bp.collidepoint(mx, my) and len(state.ratio_ui_rows) < 12:
#                     state.ratio_ui_rows.append({'size': '2x2', 'weight': '10', 'limit': '2'})
#                 if bm.collidepoint(mx, my) and len(state.ratio_ui_rows) > 1:
#                     state.ratio_ui_rows.pop();
#                     state.active_cell = None
#
#             # --- RIGHT PANEL ---
#             elif mx > PANEL_RIGHT_X:
#                 for i in range(5):
#                     btn = pygame.Rect(PANEL_RIGHT_X + 40, 50 + i * 50, 120, 35)
#                     cb = pygame.Rect(PANEL_RIGHT_X + 15, 58 + i * 50, 20, 20)
#                     if btn.collidepoint(mx, my):
#                         state.current_layer = i + 1;
#                         state.selected_trays = [];
#                         state.selected_cells = []
#                         layout(state.containers)
#                     if cb.collidepoint(mx, my): state.layer_checkbox[i] = not state.layer_checkbox[i]
#
#                 if FILL_SAME_BTN_RECT.collidepoint(mx, my): save_undo(); fill_same()
#                 if AUTO_FILL_BTN_RECT.collidepoint(mx, my):
#                     if state.selected_trays:
#                         save_undo(); auto_fill_mismatch(state.selected_trays)
#                     else:
#                         state.last_action_message = "Select Trays"
#                 if FILL_LAYER_BTN_RECT.collidepoint(mx, my): save_undo(); fill_layers()
#                 if SHUFFLE_BTN_RECT.collidepoint(mx, my): save_undo(); shuffle_level()
#                 if CLEAR_LEVEL_BTN_RECT.collidepoint(mx,
#                                                      my): save_undo(); state.containers = []; state.selected_trays = []
#
#                 if RATIO_MINUS_RECT.collidepoint(mx, my): state.shuffle_ratio = max(0, state.shuffle_ratio - 10)
#                 if RATIO_PLUS_RECT.collidepoint(mx, my): state.shuffle_ratio = min(100, state.shuffle_ratio + 10)
#
#             # --- CENTER ---
#             else:
#                 state.active_cell = None
#                 if state.paint_mode:
#                     clicked = False
#                     for ct in state.containers:
#                         if ct.layer != state.current_layer: continue
#                         ox = ct.x + ct.cols * CELL_SIZE + 20
#                         if ox <= mx <= ox + ct.cols * CELL_SIZE and ct.y <= my <= ct.y + ct.rows * CELL_SIZE:
#                             c = (mx - ox) // CELL_SIZE;
#                             r = (my - ct.y) // CELL_SIZE
#                             if 0 <= r < ct.rows and 0 <= c < ct.cols:
#                                 t = (ct, int(r), int(c))
#                                 keys = pygame.key.get_pressed()
#                                 if keys[pygame.K_LSHIFT]:
#                                     if t in state.selected_cells:
#                                         state.selected_cells.remove(t)
#                                     else:
#                                         state.selected_cells.append(t)
#                                 else:
#                                     state.selected_cells = [t]
#                                 clicked = True;
#                                 break
#                     if not clicked: state.selected_cells = []
#                 else:
#                     clicked = None
#                     for ct in state.containers:
#                         if ct.layer != state.current_layer: continue
#                         if ct.x <= mx <= ct.x + ct.cols * CELL_SIZE * 2 + 40 and ct.y <= my <= ct.y + ct.rows * CELL_SIZE:
#                             clicked = ct;
#                             break
#                     if clicked:
#                         keys = pygame.key.get_pressed()
#                         if keys[pygame.K_LSHIFT]:
#                             if clicked in state.selected_trays:
#                                 state.selected_trays.remove(clicked)
#                             else:
#                                 state.selected_trays.append(clicked)
#                         else:
#                             state.selected_trays = [clicked]
#                     else:
#                         state.selected_trays = []
#
#         if e.type == pygame.KEYDOWN:
#             if state.active_cell:
#                 r, c = state.active_cell
#                 k = 'size' if c == 0 else 'weight' if c == 1 else 'limit'
#                 if e.key == pygame.K_BACKSPACE:
#                     state.ratio_ui_rows[r][k] = state.ratio_ui_rows[r][k][:-1]
#                 elif e.key == pygame.K_TAB:
#                     state.active_cell[1] = (c + 1) % 3
#                 elif e.key == pygame.K_RETURN:
#                     state.active_cell = None
#                 else:
#                     if len(state.ratio_ui_rows[r][k]) < 6: state.ratio_ui_rows[r][k] += e.unicode
#             else:
#                 if e.key == pygame.K_SPACE: save_undo(); state.containers.append(
#                     Container(state.current_layer)); layout(state.containers)
#                 if e.unicode in "123456" and state.selected_trays: save_undo(); fill_n(int(e.unicode))
#                 if e.key == pygame.K_d: save_undo(); state.containers = [c for c in state.containers if
#                                                                          c not in state.selected_trays]; state.selected_trays = []
#                 if e.key == pygame.K_t and len(state.selected_trays) == 2:
#                     save_undo();
#                     t1, t2 = state.selected_trays
#                     if not t1.cells: t1.cells = [[None] * t1.cols for _ in range(t1.rows)]
#                     if not t2.cells: t2.cells = [[None] * t2.cols for _ in range(t2.rows)]
#                     t1.cells, t2.cells = t2.cells, t1.cells
#                 if e.key == pygame.K_s: save_undo(); shuffle_level()
#                 if e.key == pygame.K_u: undo()
#                 if e.key == pygame.K_e: export_to_unity_json()
#                 if e.key == pygame.K_p: state.paint_mode = not state.paint_mode; state.selected_trays = []; state.selected_cells = []
#
#                 if state.paint_mode and e.unicode.isdigit():
#                     col = int(e.unicode)
#                     save_undo();
#                     keys = pygame.key.get_pressed()
#                     for ct, r, c in state.selected_cells:
#                         if keys[pygame.K_LALT]:
#                             ct.target[r][c] = col
#                         else:
#                             if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#                             ct.cells[r][c] = col
#
#                 if e.key == pygame.K_MINUS: state.tray_color_variety = max(1, state.tray_color_variety - 1)
#                 if e.key == pygame.K_EQUALS: state.tray_color_variety = min(10, state.tray_color_variety + 1)
#                 if e.key == pygame.K_COMMA: state.max_same_color = max(1, state.max_same_color - 1)
#                 if e.key == pygame.K_PERIOD: state.max_same_color = min(10, state.max_same_color + 1)
#
#     draw_stats(SCREEN)
#     draw_table(SCREEN)
#     draw_right_panel(SCREEN)
#     draw_instruction(SCREEN)
#     draw_gameplay(SCREEN)
#
#     pygame.display.flip()
#     CLOCK.tick(60)
#
# pygame.quit()


# import pygame
# from config import *
# from logic_core import *
# from ui import *
# from logic_export import export_to_unity_json
#
# pygame.init()
# SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("ColorCube Tool - Directional Gen & Symmetry")
# CLOCK = pygame.time.Clock()
#
# running = True
# while running:
#     SCREEN.fill(BG_COLOR)
#     draw_panels(SCREEN)
#
#     events = pygame.event.get()
#     for e in events:
#         if e.type == pygame.QUIT: running = False
#
#         if e.type == pygame.MOUSEBUTTONDOWN:
#             mx, my = pygame.mouse.get_pos()
#
#             # --- LEFT PANEL ---
#             if mx < PANEL_LEFT_W:
#                 clicked = None
#                 for r, row in enumerate(state.ratio_ui_rows):
#                     y = TABLE_Y + 25 + r * ROW_H
#                     rects = [
#                         pygame.Rect(TABLE_X, y, COL_W_SIZE, ROW_H),
#                         pygame.Rect(TABLE_X + COL_W_SIZE, y, COL_W_WEIGHT, ROW_H),
#                         pygame.Rect(TABLE_X + COL_W_SIZE + COL_W_WEIGHT, y, COL_W_LIMIT, ROW_H)
#                     ]
#                     for c, rct in enumerate(rects):
#                         if rct.collidepoint(mx, my): clicked = [r, c]
#                 state.active_cell = clicked
#
#                 bp = pygame.Rect(TABLE_X + 160, TABLE_Y, BTN_SIZE, BTN_SIZE)
#                 bm = pygame.Rect(TABLE_X + 190, TABLE_Y, BTN_SIZE, BTN_SIZE)
#                 if bp.collidepoint(mx, my) and len(state.ratio_ui_rows) < 12:
#                     state.ratio_ui_rows.append({'size': '2x2', 'weight': '10', 'limit': '2'})
#                 if bm.collidepoint(mx, my) and len(state.ratio_ui_rows) > 1:
#                     state.ratio_ui_rows.pop();
#                     state.active_cell = None
#
#             # --- RIGHT PANEL ---
#             elif mx > PANEL_RIGHT_X:
#                 for i in range(5):
#                     btn = pygame.Rect(PANEL_RIGHT_X + 40, 50 + i * 50, 120, 35)
#                     cb = pygame.Rect(PANEL_RIGHT_X + 15, 58 + i * 50, 20, 20)
#                     if btn.collidepoint(mx, my):
#                         state.current_layer = i + 1;
#                         state.selected_trays = [];
#                         state.selected_cells = []
#                         layout(state.containers)
#                     if cb.collidepoint(mx, my): state.layer_checkbox[i] = not state.layer_checkbox[i]
#
#                 if FILL_SAME_BTN_RECT.collidepoint(mx, my): save_undo(); fill_same()
#                 if SORT_BTN_RECT.collidepoint(mx, my):
#                     if state.selected_trays:
#                         save_undo(); sort_selected_trays(state.selected_trays)
#                     else:
#                         state.last_action_message = "Select trays to sort"
#                 if SORT_BTN_RECT.collidepoint(mx, my):
#                     save_undo()
#                     sort_selected_trays(state.selected_trays)
#                 if AUTO_FILL_BTN_RECT.collidepoint(mx, my):
#                     if state.selected_trays:
#                         save_undo(); auto_fill_mismatch(state.selected_trays)
#                     else:
#                         state.last_action_message = "Select Trays"
#                 if FILL_LAYER_BTN_RECT.collidepoint(mx, my): save_undo(); fill_layers()
#                 if SHUFFLE_BTN_RECT.collidepoint(mx, my): save_undo(); shuffle_level()
#                 if CLEAR_LEVEL_BTN_RECT.collidepoint(mx,
#                                                      my): save_undo(); state.containers = []; state.selected_trays = []
#
#                 if RATIO_MINUS_RECT.collidepoint(mx, my): state.shuffle_ratio = max(0, state.shuffle_ratio - 10)
#                 if RATIO_PLUS_RECT.collidepoint(mx, my): state.shuffle_ratio = min(100, state.shuffle_ratio + 10)
#
#                 if SYMMETRY_BTN_RECT.collidepoint(mx, my): state.symmetry_mode = not state.symmetry_mode
#
#             # --- CENTER ---
#             else:
#                 state.active_cell = None
#                 if state.paint_mode:
#                     clicked = False
#                     for ct in state.containers:
#                         if ct.layer != state.current_layer: continue
#                         ox = ct.x + ct.cols * CELL_SIZE + 20
#                         if ox <= mx <= ox + ct.cols * CELL_SIZE and ct.y <= my <= ct.y + ct.rows * CELL_SIZE:
#                             c = (mx - ox) // CELL_SIZE;
#                             r = (my - ct.y) // CELL_SIZE
#                             if 0 <= r < ct.rows and 0 <= c < ct.cols:
#                                 t = (ct, int(r), int(c))
#                                 keys = pygame.key.get_pressed()
#                                 if keys[pygame.K_LSHIFT]:
#                                     if t in state.selected_cells:
#                                         state.selected_cells.remove(t)
#                                     else:
#                                         state.selected_cells.append(t)
#                                 else:
#                                     state.selected_cells = [t]
#                                 clicked = True;
#                                 break
#                     if not clicked: state.selected_cells = []
#                 else:
#                     clicked = None
#                     for ct in state.containers:
#                         if ct.layer != state.current_layer: continue
#                         if ct.x <= mx <= ct.x + ct.cols * CELL_SIZE * 2 + 40 and ct.y <= my <= ct.y + ct.rows * CELL_SIZE:
#                             clicked = ct;
#                             break
#                     if clicked:
#                         keys = pygame.key.get_pressed()
#                         if keys[pygame.K_LSHIFT]:
#                             if clicked in state.selected_trays:
#                                 state.selected_trays.remove(clicked)
#                             else:
#                                 state.selected_trays.append(clicked)
#                         else:
#                             state.selected_trays = [clicked]
#                     else:
#                         state.selected_trays = []
#
#         if e.type == pygame.KEYDOWN:
#             if state.active_cell:
#                 r, c = state.active_cell
#                 k = 'size' if c == 0 else 'weight' if c == 1 else 'limit'
#                 if e.key == pygame.K_BACKSPACE:
#                     state.ratio_ui_rows[r][k] = state.ratio_ui_rows[r][k][:-1]
#                 elif e.key == pygame.K_TAB:
#                     state.active_cell[1] = (c + 1) % 3
#                 elif e.key == pygame.K_RETURN:
#                     state.active_cell = None
#                 else:
#                     if len(state.ratio_ui_rows[r][k]) < 6: state.ratio_ui_rows[r][k] += e.unicode
#             else:
#                 if e.key == pygame.K_SPACE: save_undo(); spawn_new_trays(); layout(state.containers)
#                 if e.unicode in "123456" and state.selected_trays: save_undo(); fill_n(int(e.unicode))
#                 if e.key == pygame.K_d: save_undo(); state.containers = [c for c in state.containers if
#                                                                          c not in state.selected_trays]; state.selected_trays = []
#                 if e.key == pygame.K_t and len(state.selected_trays) == 2:
#                     save_undo();
#                     t1, t2 = state.selected_trays
#                     if not t1.cells: t1.cells = [[None] * t1.cols for _ in range(t1.rows)]
#                     if not t2.cells: t2.cells = [[None] * t2.cols for _ in range(t2.rows)]
#                     t1.cells, t2.cells = t2.cells, t1.cells
#                 if e.key == pygame.K_s: save_undo(); shuffle_level()
#                 if e.key == pygame.K_u: undo()
#                 if e.key == pygame.K_e: export_to_unity_json()
#                 if e.key == pygame.K_p: state.paint_mode = not state.paint_mode; state.selected_trays = []; state.selected_cells = []
#
#                 if state.paint_mode and e.unicode.isdigit():
#                     col = int(e.unicode)
#                     save_undo();
#                     keys = pygame.key.get_pressed()
#                     for ct, r, c in state.selected_cells:
#                         if keys[pygame.K_LALT]:
#                             ct.target[r][c] = col
#                         else:
#                             if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#                             ct.cells[r][c] = col
#
#                 if e.key == pygame.K_MINUS: state.tray_color_variety = max(1, state.tray_color_variety - 1)
#                 if e.key == pygame.K_EQUALS: state.tray_color_variety = min(10, state.tray_color_variety + 1)
#                 if e.key == pygame.K_COMMA: state.max_same_color = max(1, state.max_same_color - 1)
#                 if e.key == pygame.K_PERIOD: state.max_same_color = min(10, state.max_same_color + 1)
#
#     draw_stats(SCREEN)
#     draw_table(SCREEN)
#     draw_right_panel(SCREEN)
#     draw_instruction(SCREEN)
#     draw_gameplay(SCREEN)
#
#     pygame.display.flip()
#     CLOCK.tick(60)
#
# pygame.quit()


import pygame
from config import *
from logic_core import *
from ui import *
from logic_export import export_to_unity_json

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ColorCube Tool - Pro V3")
CLOCK = pygame.time.Clock()

running = True
while running:
    SCREEN.fill(BG_COLOR)
    draw_panels(SCREEN)

    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT: running = False

        if e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # --- LEFT PANEL ---
            if mx < PANEL_LEFT_W:
                clicked = None
                for r, row in enumerate(state.ratio_ui_rows):
                    y = TABLE_Y + 25 + r * ROW_H
                    rects = [
                        pygame.Rect(TABLE_X, y, COL_W_SIZE, ROW_H),
                        pygame.Rect(TABLE_X + COL_W_SIZE, y, COL_W_WEIGHT, ROW_H),
                        pygame.Rect(TABLE_X + COL_W_SIZE + COL_W_WEIGHT, y, COL_W_LIMIT, ROW_H)
                    ]
                    for c, rct in enumerate(rects):
                        if rct.collidepoint(mx, my): clicked = [r, c]
                state.active_cell = clicked

                bp = pygame.Rect(TABLE_X + 160, TABLE_Y, BTN_SIZE, BTN_SIZE)
                bm = pygame.Rect(TABLE_X + 190, TABLE_Y, BTN_SIZE, BTN_SIZE)
                if bp.collidepoint(mx, my) and len(state.ratio_ui_rows) < 12:
                    state.ratio_ui_rows.append({'size': '2x2', 'weight': '10', 'limit': '2'})
                if bm.collidepoint(mx, my) and len(state.ratio_ui_rows) > 1:
                    state.ratio_ui_rows.pop();
                    state.active_cell = None

            # --- RIGHT PANEL ---
            elif mx > PANEL_RIGHT_X:
                for i in range(5):
                    btn = pygame.Rect(PANEL_RIGHT_X + 40, 50 + i * 50, 120, 35)
                    cb = pygame.Rect(PANEL_RIGHT_X + 15, 58 + i * 50, 20, 20)
                    if btn.collidepoint(mx, my):
                        state.current_layer = i + 1;
                        state.selected_trays = [];
                        state.selected_cells = []
                        layout(state.containers)
                    if cb.collidepoint(mx, my): state.layer_checkbox[i] = not state.layer_checkbox[i]

                if FILL_SAME_BTN_RECT.collidepoint(mx, my): save_undo(); fill_same()

                if SORT_BTN_RECT.collidepoint(mx, my):
                    save_undo();
                    sort_selected_trays(state.selected_trays)

                if AUTO_FILL_BTN_RECT.collidepoint(mx, my):
                    if state.selected_trays:
                        save_undo(); auto_fill_mismatch(state.selected_trays)
                    else:
                        state.last_action_message = "Select Trays"

                if FILL_LAYER_BTN_RECT.collidepoint(mx, my): save_undo(); fill_layers()
                if SHUFFLE_BTN_RECT.collidepoint(mx, my): save_undo(); shuffle_level()
                if CLEAR_LEVEL_BTN_RECT.collidepoint(mx,
                                                     my): save_undo(); state.containers = []; state.selected_trays = []

                if SYMMETRY_BTN_RECT.collidepoint(mx, my):
                    state.symmetry_mode = not state.symmetry_mode

                if RATIO_MINUS_RECT.collidepoint(mx, my): state.shuffle_ratio = max(0, state.shuffle_ratio - 10)
                if RATIO_PLUS_RECT.collidepoint(mx, my): state.shuffle_ratio = min(100, state.shuffle_ratio + 10)

            # --- CENTER ---
            else:
                state.active_cell = None
                if state.paint_mode:
                    clicked = False
                    for ct in state.containers:
                        if ct.layer != state.current_layer: continue
                        ox = ct.x + ct.cols * CELL_SIZE + 20
                        if ox <= mx <= ox + ct.cols * CELL_SIZE and ct.y <= my <= ct.y + ct.rows * CELL_SIZE:
                            c = (mx - ox) // CELL_SIZE;
                            r = (my - ct.y) // CELL_SIZE
                            if 0 <= r < ct.rows and 0 <= c < ct.cols:
                                t = (ct, int(r), int(c))
                                keys = pygame.key.get_pressed()
                                if keys[pygame.K_LSHIFT]:
                                    if t in state.selected_cells:
                                        state.selected_cells.remove(t)
                                    else:
                                        state.selected_cells.append(t)
                                else:
                                    state.selected_cells = [t]
                                clicked = True;
                                break
                    if not clicked: state.selected_cells = []
                else:
                    clicked = None
                    for ct in state.containers:
                        if ct.layer != state.current_layer: continue
                        if ct.x <= mx <= ct.x + ct.cols * CELL_SIZE * 2 + 40 and ct.y <= my <= ct.y + ct.rows * CELL_SIZE:
                            clicked = ct;
                            break
                    if clicked:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LSHIFT]:
                            if clicked in state.selected_trays:
                                state.selected_trays.remove(clicked)
                            else:
                                state.selected_trays.append(clicked)
                        else:
                            state.selected_trays = [clicked]
                    else:
                        state.selected_trays = []

        if e.type == pygame.KEYDOWN:
            if state.active_cell:
                r, c = state.active_cell
                k = 'size' if c == 0 else 'weight' if c == 1 else 'limit'
                if e.key == pygame.K_BACKSPACE:
                    state.ratio_ui_rows[r][k] = state.ratio_ui_rows[r][k][:-1]
                elif e.key == pygame.K_TAB:
                    state.active_cell[1] = (c + 1) % 3
                elif e.key == pygame.K_RETURN:
                    state.active_cell = None
                else:
                    if len(state.ratio_ui_rows[r][k]) < 6: state.ratio_ui_rows[r][k] += e.unicode
            else:
                if e.key == pygame.K_SPACE:
                    save_undo();
                    spawn_new_trays();
                    layout(state.containers)  # Sử dụng hàm spawn_new_trays
                if e.unicode in "123456" and state.selected_trays: save_undo(); fill_n(int(e.unicode))
                if e.key == pygame.K_d: save_undo(); state.containers = [c for c in state.containers if
                                                                         c not in state.selected_trays]; state.selected_trays = []
                if e.key == pygame.K_t and len(state.selected_trays) == 2:
                    save_undo();
                    t1, t2 = state.selected_trays
                    if not t1.cells: t1.cells = [[None] * t1.cols for _ in range(t1.rows)]
                    if not t2.cells: t2.cells = [[None] * t2.cols for _ in range(t2.rows)]
                    t1.cells, t2.cells = t2.cells, t1.cells
                if e.key == pygame.K_s: save_undo(); shuffle_level()
                if e.key == pygame.K_u: undo()
                if e.key == pygame.K_e: export_to_unity_json()
                if e.key == pygame.K_p: state.paint_mode = not state.paint_mode; state.selected_trays = []; state.selected_cells = []

                if state.paint_mode and e.unicode.isdigit():
                    col = int(e.unicode)
                    save_undo();
                    keys = pygame.key.get_pressed()
                    for ct, r, c in state.selected_cells:
                        if keys[pygame.K_LALT]:
                            ct.target[r][c] = col
                        else:
                            if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
                            ct.cells[r][c] = col

                if e.key == pygame.K_MINUS: state.tray_color_variety = max(1, state.tray_color_variety - 1)
                if e.key == pygame.K_EQUALS: state.tray_color_variety = min(10, state.tray_color_variety + 1)
                if e.key == pygame.K_COMMA: state.max_same_color = max(1, state.max_same_color - 1)
                if e.key == pygame.K_PERIOD: state.max_same_color = min(10, state.max_same_color + 1)

    draw_stats(SCREEN)
    draw_table(SCREEN)
    draw_right_panel(SCREEN)
    draw_instruction(SCREEN)
    draw_gameplay(SCREEN)

    pygame.display.flip()
    CLOCK.tick(60)

pygame.quit()