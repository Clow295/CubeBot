import pygame
from config import *
from logic_core import state, global_stats


def draw_panels(screen):
    h = screen.get_height()
    pygame.draw.rect(screen, PANEL_BG, (0, 0, PANEL_LEFT_W, h))
    pygame.draw.rect(screen, PANEL_BG, (PANEL_RIGHT_X, 0, PANEL_RIGHT_W, h))
    pygame.draw.line(screen, BORDER_COLOR, (PANEL_LEFT_W, 0), (PANEL_LEFT_W, h), 2)
    pygame.draw.line(screen, BORDER_COLOR, (PANEL_RIGHT_X, 0), (PANEL_RIGHT_X, h), 2)


def draw_stats(screen):
    tc, bc = global_stats()
    tb, tt = sum(bc.values()), sum(tc.values())
    y = 80

    for i in range(len(COLORS)):
        b, t = bc.get(i, 0), tc.get(i, 0)
        c = (255, 255, 255) if i < state.tray_color_variety else (50, 50, 50)
        pygame.draw.rect(screen, COLORS[i], (20, y, 20, 20))
        pygame.draw.rect(screen, c, (20, y, 20, 20), 2)

        col_txt = (255, 80, 80) if b > t else (80, 255, 80) if b == t and t > 0 else (255, 255, 255)
        screen.blit(pygame.font.SysFont(None, 22).render(f"{b}/{t}", True, col_txt), (50, y + 2))
        y += 25

    pygame.draw.line(screen, (100, 100, 100), (20, y + 5), (PANEL_LEFT_W - 20, y + 5), 1)
    tot_c = (80, 255, 80) if tb == tt and tt > 0 else (255, 80, 80) if tb > tt else (255, 255, 255)
    screen.blit(pygame.font.SysFont(None, 24).render(f"TOTAL: {tb}/{tt}", True, tot_c), (20, y + 15))


def draw_table(screen):
    pygame.draw.rect(screen, (80, 80, 80), (TABLE_X, TABLE_Y, COL_W_SIZE + COL_W_WEIGHT + COL_W_LIMIT, ROW_H))
    f = pygame.font.SysFont(None, 18)
    screen.blit(f.render("Size", 1, TEXT_WHITE), (TABLE_X + 5, TABLE_Y + 5))
    screen.blit(f.render("Ratio", 1, TEXT_WHITE), (TABLE_X + COL_W_SIZE + 5, TABLE_Y + 5))
    screen.blit(f.render("Limit", 1, TEXT_WHITE), (TABLE_X + COL_W_SIZE + COL_W_WEIGHT + 5, TABLE_Y + 5))

    bp = pygame.Rect(TABLE_X + 160, TABLE_Y, 25, 25)
    bm = pygame.Rect(TABLE_X + 190, TABLE_Y, 25, 25)
    pygame.draw.rect(screen, (60, 150, 60), bp);
    screen.blit(f.render("+", 1, TEXT_WHITE), (bp.x + 8, bp.y + 5))
    pygame.draw.rect(screen, (150, 60, 60), bm);
    screen.blit(f.render("-", 1, TEXT_WHITE), (bm.x + 10, bm.y + 5))

    for r, row in enumerate(state.ratio_ui_rows):
        y = TABLE_Y + 25 + r * ROW_H
        cols = [COL_W_SIZE, COL_W_WEIGHT, COL_W_LIMIT]
        cx = TABLE_X
        for i, w in enumerate(cols):
            rct = pygame.Rect(cx, y, w, ROW_H)
            bg = (80, 80, 120) if state.active_cell == [r, i] else (60, 60, 60)
            pygame.draw.rect(screen, bg, rct);
            pygame.draw.rect(screen, (100, 100, 100), rct, 1)
            key = 'size' if i == 0 else 'weight' if i == 1 else 'limit'
            screen.blit(f.render(row.get(key, ''), 1, TEXT_WHITE), (rct.x + 5, rct.y + 5))
            cx += w

    screen.blit(pygame.font.SysFont(None, 24).render(
        f"Total Ratio: {sum([int(x['weight']) for x in state.ratio_ui_rows if x['weight'].isdigit()])}%", 1,
        (150, 255, 150)), (TABLE_X, TABLE_Y + 25 + len(state.ratio_ui_rows) * ROW_H + 10))


def draw_right_panel(screen):
    # Layer Controls
    for i in range(5):
        c = (100, 150, 200) if (i + 1) == state.current_layer else (60, 60, 60)
        pygame.draw.rect(screen, c, (PANEL_RIGHT_X + 50, 50 + i * 50, 180, 35))
        screen.blit(pygame.font.SysFont(None, 24).render(f"Layer {i + 1}", 1, TEXT_WHITE),
                    (PANEL_RIGHT_X + 100, 50 + i * 50 + 8))
        cb = pygame.Rect(PANEL_RIGHT_X + 15, 58 + i * 50, 20, 20)
        pygame.draw.rect(screen, TEXT_WHITE, cb, 2)
        if state.layer_checkbox[i]: pygame.draw.rect(screen, (200, 200, 200), (cb.x + 4, cb.y + 4, 12, 12))

    # Buttons
    btns = [
        (FILL_SAME_BTN_RECT, "Fill Same (Green)", (50, 150, 50)),
        (SORT_BTN_RECT, "Sort Blocks", (200, 150, 50)),
        (AUTO_FILL_BTN_RECT, "Auto Fill (Cluster)", (0, 200, 255)),
        (FILL_LAYER_BTN_RECT, "Fill Layers", (255, 100, 200) if any(state.layer_checkbox) else (100, 100, 100)),
        (SHUFFLE_BTN_RECT, "Shuffle", (150, 50, 255)),
        (CLEAR_LEVEL_BTN_RECT, "Clear Level", (200, 50, 50))
    ]
    for rct, txt, col in btns:
        pygame.draw.rect(screen, col, rct);
        pygame.draw.rect(screen, TEXT_WHITE, rct, 1)
        screen.blit(pygame.font.SysFont(None, 22).render(txt, 1, TEXT_WHITE), (rct.x + 10, rct.y + 8))

    # Symmetry Toggle
    sym_col = (0, 200, 0) if state.symmetry_mode else (80, 80, 80)
    pygame.draw.rect(screen, sym_col, SYMMETRY_BTN_RECT)
    pygame.draw.rect(screen, TEXT_WHITE, SYMMETRY_BTN_RECT, 2)
    status = "ON" if state.symmetry_mode else "OFF"
    screen.blit(pygame.font.SysFont(None, 22).render(f"Spawn Symmetry: {status}", 1, TEXT_WHITE),
                (SYMMETRY_BTN_RECT.x + 30, SYMMETRY_BTN_RECT.y + 8))

    # Fix Color Button
    pygame.draw.rect(screen, (50, 100, 150), FIX_COLOR_BTN_RECT)
    pygame.draw.rect(screen, TEXT_WHITE, FIX_COLOR_BTN_RECT, 2)
    screen.blit(pygame.font.SysFont(None, 22).render("Fix Color", 1, TEXT_WHITE),
                (FIX_COLOR_BTN_RECT.x + 70, FIX_COLOR_BTN_RECT.y + 8))

    # Shuffle Ratio
    pygame.draw.rect(screen, (150, 50, 50), RATIO_MINUS_RECT)
    pygame.draw.rect(screen, (50, 150, 50), RATIO_PLUS_RECT)
    f = pygame.font.SysFont(None, 24)
    screen.blit(f.render("-", 1, TEXT_WHITE), (RATIO_MINUS_RECT.x + 15, RATIO_MINUS_RECT.y + 5))
    screen.blit(f.render("+", 1, TEXT_WHITE), (RATIO_PLUS_RECT.x + 15, RATIO_PLUS_RECT.y + 5))
    screen.blit(pygame.font.SysFont(None, 20).render(f"Shuffle Ratio: {state.shuffle_ratio}%", 1, (200, 200, 255)),
                (BTN_X + 60, RATIO_LABEL_Y + 5))


def draw_instruction(screen):
    ins = ["Space:Spawn", "1-6:Fill N", "P:Paint Mode", "0-9:Paint Block", "Alt+0-9:Target", "T:Swap", "S:Shuffle",
           "U:Undo", "D:Del", "E:Export", "R:Rayline Editor"]
    start_y = RATIO_LABEL_Y + 60
    for k, t in enumerate(ins):
        col = (0, 255, 255) if t == "R:Rayline Editor" and state.rayline_enabled else (200, 200, 200)
        screen.blit(pygame.font.SysFont(None, 18).render(t, 1, col), (PANEL_RIGHT_X + 20, start_y + k * 18))


def draw_gameplay(screen):
    # Vẽ rayline trong gameplay area (nếu enabled)
    if state.rayline_enabled and state.rayline_points:
        from logic_rayline import grid_to_world, world_to_screen_x, world_to_screen_y

        # Vẽ rayline path với màu mờ
        for i in range(len(state.rayline_points)):
            gx, gy = state.rayline_points[i]
            wx, wy = grid_to_world(gx, gy)
            sx = world_to_screen_x(wx)
            sy = world_to_screen_y(wy)

            # Vẽ circle tại mỗi điểm
            pygame.draw.circle(screen, (100, 200, 255), (int(sx), int(sy)), 8, 3)

            # Vẽ line nối giữa các điểm
            if i > 0:
                prev_gx, prev_gy = state.rayline_points[i-1]
                prev_wx, prev_wy = grid_to_world(prev_gx, prev_gy)
                prev_sx = world_to_screen_x(prev_wx)
                prev_sy = world_to_screen_y(prev_wy)
                pygame.draw.line(screen, (100, 200, 255),
                               (int(prev_sx), int(prev_sy)),
                               (int(sx), int(sy)), 4)

    # Vẽ containers
    vis = [c for c in state.containers if c.layer == state.current_layer]
    for ct in vis:
        ct.draw_target(screen)
        ct.draw_block(screen)
        sel = (not state.paint_mode and ct in state.selected_trays)
        if sel: pygame.draw.rect(screen, (0, 255, 0),
                                 (ct.x - 5, ct.y - 5, ct.cols * CELL_SIZE + 10, ct.rows * CELL_SIZE + 10), 2)

    if state.paint_mode:
        for ct, r, c in state.selected_cells:
            if ct.layer == state.current_layer:
                ox = ct.x + ct.cols * CELL_SIZE + 20 + c * CELL_SIZE
                oy = ct.y + r * CELL_SIZE
                pygame.draw.rect(screen, (255, 255, 255), (ox, oy, CELL_SIZE, CELL_SIZE), 2)

        w, h = screen.get_size()
        screen.blit(pygame.font.SysFont(None, 40).render("PAINT MODE", 1, (255, 50, 50)), (w / 2 - 100, 20))

    h = screen.get_height()
    info = f"Var:{state.tray_color_variety} | MaxSame:{state.max_same_color}"
    screen.blit(pygame.font.SysFont(None, 24).render(info, 1, (150, 255, 150)), (20, h - 40))
    screen.blit(pygame.font.SysFont(None, 30).render(state.last_action_message, 1, (255, 255, 0)), (20, h - 70))


# ============================================
# RAYLINE MODAL UI
# ============================================

def draw_rayline_modal(screen):
    """Vẽ rayline editor modal"""
    # Dim background
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Modal background
    modal_rect = pygame.Rect(RAYLINE_MODAL_X, RAYLINE_MODAL_Y, RAYLINE_MODAL_W, RAYLINE_MODAL_H)
    pygame.draw.rect(screen, RAYLINE_MODAL_BG, modal_rect)
    pygame.draw.rect(screen, TEXT_WHITE, modal_rect, 3)

    # Title
    title_font = pygame.font.SysFont(None, 36)
    title_text = title_font.render("RAYLINE EDITOR", True, TEXT_WHITE)
    title_x = RAYLINE_MODAL_X + (RAYLINE_MODAL_W - title_text.get_width()) // 2
    screen.blit(title_text, (title_x, RAYLINE_MODAL_Y + 20))

    # Draw grid
    draw_rayline_grid(screen)

    # Draw path
    draw_rayline_path(screen)

    # Draw controls
    draw_rayline_controls(screen)

    # Status text
    num_points = len(state.rayline_temp_drawing) if state.rayline_is_drawing else len(state.rayline_points)
    status_text = f"Points: {num_points}"
    if state.rayline_enabled:
        status_text += " | Rayline ENABLED"

    status_font = pygame.font.SysFont(None, 24)
    status_surface = status_font.render(status_text, True, (200, 200, 200))
    screen.blit(status_surface, (RAYLINE_MODAL_X + 20, RAYLINE_BTN_Y + 50))


def draw_rayline_grid(screen):
    """Vẽ grid 10x10"""
    # Grid background
    grid_rect = pygame.Rect(RAYLINE_GRID_X, RAYLINE_GRID_Y, RAYLINE_GRID_TOTAL, RAYLINE_GRID_TOTAL)
    pygame.draw.rect(screen, RAYLINE_GRID_BG, grid_rect)

    # Grid lines
    for i in range(RAYLINE_GRID_SIZE + 1):
        # Vertical lines
        x = RAYLINE_GRID_X + i * RAYLINE_CELL_SIZE
        pygame.draw.line(screen, RAYLINE_GRID_LINE,
                        (x, RAYLINE_GRID_Y),
                        (x, RAYLINE_GRID_Y + RAYLINE_GRID_TOTAL), 1)

        # Horizontal lines
        y = RAYLINE_GRID_Y + i * RAYLINE_CELL_SIZE
        pygame.draw.line(screen, RAYLINE_GRID_LINE,
                        (RAYLINE_GRID_X, y),
                        (RAYLINE_GRID_X + RAYLINE_GRID_TOTAL, y), 1)

    # Hover effect
    mx, my = pygame.mouse.get_pos()
    from logic_rayline import mouse_to_grid
    grid_pos = mouse_to_grid(mx, my)
    if grid_pos:
        gx, gy = grid_pos
        cell_x = RAYLINE_GRID_X + gx * RAYLINE_CELL_SIZE
        cell_y = RAYLINE_GRID_Y + gy * RAYLINE_CELL_SIZE
        hover_rect = pygame.Rect(cell_x, cell_y, RAYLINE_CELL_SIZE, RAYLINE_CELL_SIZE)
        pygame.draw.rect(screen, RAYLINE_HOVER_COLOR, hover_rect)

    # Grid border
    pygame.draw.rect(screen, TEXT_WHITE, grid_rect, 2)


def draw_rayline_path(screen):
    """Vẽ rayline path"""
    # Vẽ temp drawing khi đang trong edit mode (hiển thị ngay khi vẽ)
    # Nếu không trong edit mode, vẽ saved path
    if state.rayline_edit_mode:
        points_to_draw = state.rayline_temp_drawing
    else:
        points_to_draw = state.rayline_points

    if len(points_to_draw) < 1:
        return

    # Draw cells
    for gx, gy in points_to_draw:
        cell_x = RAYLINE_GRID_X + gx * RAYLINE_CELL_SIZE
        cell_y = RAYLINE_GRID_Y + gy * RAYLINE_CELL_SIZE
        cell_rect = pygame.Rect(cell_x, cell_y, RAYLINE_CELL_SIZE, RAYLINE_CELL_SIZE)
        pygame.draw.rect(screen, RAYLINE_PATH_COLOR, cell_rect)
        pygame.draw.rect(screen, TEXT_WHITE, cell_rect, 2)

    # Draw connecting lines
    if len(points_to_draw) > 1:
        for i in range(len(points_to_draw) - 1):
            gx1, gy1 = points_to_draw[i]
            gx2, gy2 = points_to_draw[i + 1]

            x1 = RAYLINE_GRID_X + gx1 * RAYLINE_CELL_SIZE + RAYLINE_CELL_SIZE // 2
            y1 = RAYLINE_GRID_Y + gy1 * RAYLINE_CELL_SIZE + RAYLINE_CELL_SIZE // 2
            x2 = RAYLINE_GRID_X + gx2 * RAYLINE_CELL_SIZE + RAYLINE_CELL_SIZE // 2
            y2 = RAYLINE_GRID_Y + gy2 * RAYLINE_CELL_SIZE + RAYLINE_CELL_SIZE // 2

            pygame.draw.line(screen, (255, 255, 255), (x1, y1), (x2, y2), 3)


def draw_rayline_controls(screen):
    """Vẽ control buttons"""
    font = pygame.font.SysFont(None, 28)

    # Save button
    pygame.draw.rect(screen, (50, 150, 50), RAYLINE_SAVE_BTN)
    pygame.draw.rect(screen, TEXT_WHITE, RAYLINE_SAVE_BTN, 2)
    save_text = font.render("Save", True, TEXT_WHITE)
    screen.blit(save_text, (RAYLINE_SAVE_BTN.x + (RAYLINE_BTN_W - save_text.get_width()) // 2,
                           RAYLINE_SAVE_BTN.y + 8))

    # Clear button
    pygame.draw.rect(screen, (150, 50, 50), RAYLINE_CLEAR_BTN)
    pygame.draw.rect(screen, TEXT_WHITE, RAYLINE_CLEAR_BTN, 2)
    clear_text = font.render("Clear", True, TEXT_WHITE)
    screen.blit(clear_text, (RAYLINE_CLEAR_BTN.x + (RAYLINE_BTN_W - clear_text.get_width()) // 2,
                            RAYLINE_CLEAR_BTN.y + 8))

    # Close button
    pygame.draw.rect(screen, (100, 100, 100), RAYLINE_CLOSE_BTN)
    pygame.draw.rect(screen, TEXT_WHITE, RAYLINE_CLOSE_BTN, 2)
    close_text = font.render("Close", True, TEXT_WHITE)
    screen.blit(close_text, (RAYLINE_CLOSE_BTN.x + (RAYLINE_BTN_W - close_text.get_width()) // 2,
                            RAYLINE_CLOSE_BTN.y + 8))