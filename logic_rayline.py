"""
Rayline/Conveyor Logic Module
Chứa tất cả logic liên quan đến rayline:
- Coordinate conversion (grid ↔ world ↔ screen)
- Spawn zone calculation
- Distance checking
- Valid position checking
"""

import math
import random
from config import *


# ============================================
# COORDINATE CONVERSION
# ============================================

def grid_to_world(grid_x, grid_y):
    """
    Convert grid coordinate to Unity world space
    Grid: (0,0) top-left đến (15,15) bottom-right (Y+ down) - 16x16 grid
    World: (-8,8) top-left đến (8,-8) bottom-right (Y+ up)

    NOTE: Y axis đảo ngược vì grid Y+ down, world Y+ up
    Grid size: 16x16 → center at 7.5
    """
    world_x = (grid_x - 7.5) * 1.0  # Center at 7.5 cho grid 16x16
    world_y = (7.5 - grid_y) * 1.0  # ĐẢO NGƯỢC Y
    return (world_x, world_y)


def world_to_grid(world_x, world_y):
    """
    Convert Unity world coordinate to grid
    NOTE: Y axis đảo ngược
    Grid 16x16 → center at 7.5
    """
    grid_x = int(round(world_x + 7.5))  # Center at 7.5 cho grid 16x16
    grid_y = int(round(7.5 - world_y))  # ĐẢO NGƯỢC Y
    # Clamp to grid bounds
    grid_x = max(0, min(RAYLINE_GRID_SIZE - 1, grid_x))
    grid_y = max(0, min(RAYLINE_GRID_SIZE - 1, grid_y))
    return (grid_x, grid_y)


def world_to_screen_x(world_x):
    """
    Convert Unity world X to Pygame screen X
    Inverse of export formula: ux = ((ct.x - WIDTH/2) / 100.0) * 2
    → ct.x = (ux / 2) * 100.0 + WIDTH/2
    """
    return (world_x / 2.0) * 100.0 + WIDTH / 2


def world_to_screen_y(world_y):
    """
    Convert Unity world Y to Pygame screen Y
    Inverse of: uy = (-(ct.y - HEIGHT/2) / 100.0) * 2
    → ct.y = -uy / 2 * 100.0 + HEIGHT/2
    """
    return (-world_y / 2.0) * 100.0 + HEIGHT / 2


def screen_to_world_x(screen_x):
    """Convert Pygame screen X to Unity world X"""
    return ((screen_x - WIDTH / 2) / 100.0) * 2.0


def screen_to_world_y(screen_y):
    """Convert Pygame screen Y to Unity world Y"""
    return (-(screen_y - HEIGHT / 2) / 100.0) * 2.0


# ============================================
# MOUSE TO GRID CONVERSION (FOR UI)
# ============================================

def mouse_to_grid(mx, my):
    """
    Convert mouse position to grid cell
    Returns (grid_x, grid_y) or None if outside grid
    """
    if mx < RAYLINE_GRID_X or mx >= RAYLINE_GRID_X + RAYLINE_GRID_TOTAL:
        return None
    if my < RAYLINE_GRID_Y or my >= RAYLINE_GRID_Y + RAYLINE_GRID_TOTAL:
        return None

    grid_x = (mx - RAYLINE_GRID_X) // RAYLINE_CELL_SIZE
    grid_y = (my - RAYLINE_GRID_Y) // RAYLINE_CELL_SIZE

    if 0 <= grid_x < RAYLINE_GRID_SIZE and 0 <= grid_y < RAYLINE_GRID_SIZE:
        return (int(grid_x), int(grid_y))
    return None


def grid_to_screen_rect(grid_x, grid_y):
    """Get screen rect for a grid cell"""
    x = RAYLINE_GRID_X + grid_x * RAYLINE_CELL_SIZE
    y = RAYLINE_GRID_Y + grid_y * RAYLINE_CELL_SIZE
    import pygame
    return pygame.Rect(x, y, RAYLINE_CELL_SIZE, RAYLINE_CELL_SIZE)


# ============================================
# DISTANCE CALCULATION
# ============================================

def calculate_min_distance_to_rayline(world_x, world_y, rayline_points):
    """
    Tính khoảng cách ngắn nhất từ (world_x, world_y) đến rayline
    Args:
        world_x, world_y: Unity world coordinates
        rayline_points: List[(grid_x, grid_y)]
    Returns:
        float: minimum distance
    """
    if not rayline_points:
        return float('inf')

    min_dist = float('inf')

    for gx, gy in rayline_points:
        wx, wy = grid_to_world(gx, gy)
        dist = math.sqrt((world_x - wx) ** 2 + (world_y - wy) ** 2)
        min_dist = min(min_dist, dist)

    return min_dist


def calculate_min_distance_point_to_rayline(screen_x, screen_y, rayline_points):
    """
    Tính khoảng cách từ screen point đến rayline (dùng cho container rect)
    """
    world_x = screen_to_world_x(screen_x)
    world_y = screen_to_world_y(screen_y)
    return calculate_min_distance_to_rayline(world_x, world_y, rayline_points)


# ============================================
# SPAWN ZONE CALCULATION
# ============================================

def calculate_spawn_zones(rayline_points, num_zones=8):
    """
    Chia rayline thành các zones để spawn container

    Args:
        rayline_points: List[(grid_x, grid_y)]
        num_zones: Số zones chia

    Returns:
        List[dict] - mỗi zone chứa center point và radius
        [{'center': (wx, wy), 'radius': 3.0, 'used': False}, ...]
    """
    zones = []
    if len(rayline_points) < 2:
        # Rayline quá ngắn, tạo 1 zone duy nhất
        if len(rayline_points) == 1:
            gx, gy = rayline_points[0]
            wx, wy = grid_to_world(gx, gy)
            zones.append({
                'center': (wx, wy),
                'radius': 5.0,  # Radius lớn hơn cho single point (grid 16x16)
                'used': False
            })
        return zones

    # Chia đều rayline thành num_zones segments
    step = len(rayline_points) / num_zones

    for i in range(num_zones):
        idx = int(i * step)
        if idx >= len(rayline_points):
            idx = len(rayline_points) - 1

        gx, gy = rayline_points[idx]
        wx, wy = grid_to_world(gx, gy)

        zones.append({
            'center': (wx, wy),
            'radius': 6.0,  # Tăng lên 6.0 cho grid 16x16 (world range -8 to +8)
            'used': False
        })

    return zones


# ============================================
# VALID POSITION CHECK
# ============================================

def check_rect_overlap(rect1, rect2):
    """Check if two rects overlap"""
    return not (rect1['x'] + rect1['w'] <= rect2['x'] or
                rect1['x'] >= rect2['x'] + rect2['w'] or
                rect1['y'] + rect1['h'] <= rect2['y'] or
                rect1['y'] >= rect2['y'] + rect2['h'])


def is_valid_spawn_position(world_x, world_y, container_cols, container_rows,
                            rayline_points, existing_containers, current_layer):
    """
    Kiểm tra vị trí spawn có hợp lệ không

    Constraints:
    1. Cách rayline ít nhất 2 units
    2. Không overlap với containers khác trong cùng layer
    3. Nằm trong boundaries

    Args:
        world_x, world_y: Unity world coordinates (top-left corner)
        container_cols, container_rows: Kích thước container
        rayline_points: Rayline path
        existing_containers: Danh sách containers hiện có
        current_layer: Layer hiện tại

    Returns:
        bool: True nếu hợp lệ
    """
    # Check 1: Distance from rayline
    # IMPORTANT: Kiểm tra khoảng cách từ TẤT CẢ các điểm quan trọng của container
    # (4 góc + center) đến rayline, không chỉ top-left corner

    # Tính kích thước container trong world space
    # Công thức: 100 pixels = 2.0 world units → 1 pixel = 0.02 world units
    # Container width in screen = cols * CELL_SIZE * 2 + 40
    # Container height in screen = rows * CELL_SIZE
    container_w_world = (container_cols * CELL_SIZE * 2 + 40) * 0.02
    container_h_world = (container_rows * CELL_SIZE) * 0.02

    # Các điểm cần kiểm tra (4 góc + center)
    check_points = [
        (world_x, world_y),  # Top-left
        (world_x + container_w_world, world_y),  # Top-right
        (world_x, world_y + container_h_world),  # Bottom-left
        (world_x + container_w_world, world_y + container_h_world),  # Bottom-right
        (world_x + container_w_world/2, world_y + container_h_world/2),  # Center
    ]

    # Tất cả các điểm phải cách rayline ít nhất 2.5 units (tăng từ 2.0)
    for px, py in check_points:
        min_dist = calculate_min_distance_to_rayline(px, py, rayline_points)
        if min_dist < 2.5:
            return False

    # Convert world to screen
    screen_x = world_to_screen_x(world_x)
    screen_y = world_to_screen_y(world_y)

    # Container size in screen space
    container_w = container_cols * CELL_SIZE * 2 + 40  # Full width including target
    container_h = container_rows * CELL_SIZE

    # Check 2: Overlap với containers khác trong cùng layer
    # Thêm buffer 20px để containers cách nhau xa hơn
    BUFFER = 20
    new_rect = {
        'x': screen_x - BUFFER,
        'y': screen_y - BUFFER,
        'w': container_w + BUFFER * 2,
        'h': container_h + BUFFER * 2
    }

    for ct in existing_containers:
        if ct.layer != current_layer:
            continue

        ct_rect = {
            'x': ct.x - BUFFER,
            'y': ct.y - BUFFER,
            'w': ct.cols * CELL_SIZE * 2 + 40 + BUFFER * 2,
            'h': ct.rows * CELL_SIZE + BUFFER * 2
        }

        if check_rect_overlap(new_rect, ct_rect):
            return False

    # Check 3: Boundaries (screen space)
    # Đảm bảo container nằm trong gameplay area
    if screen_x < MARGIN_X or screen_x + container_w > PANEL_RIGHT_X:
        return False
    if screen_y < MARGIN_Y or screen_y + container_h > HEIGHT - 50:
        return False

    return True


# ============================================
# FIND SPAWN POSITION
# ============================================

def find_spawn_position_near_zone(zone, container_cols, container_rows,
                                   rayline_points, existing_containers, current_layer,
                                   max_attempts=50):
    """
    Tìm vị trí spawn hợp lệ quanh một zone

    Args:
        zone: {'center': (wx, wy), 'radius': r, 'used': bool}
        container_cols, container_rows: Kích thước container
        rayline_points: Rayline path
        existing_containers: Danh sách containers
        current_layer: Layer hiện tại
        max_attempts: Số lần thử tối đa

    Returns:
        (screen_x, screen_y, world_x, world_y) hoặc None nếu không tìm được
    """
    for _ in range(max_attempts):
        # Random offset từ center (tăng min radius từ 2.5 lên 3.0)
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(3.0, zone['radius'])

        world_x = zone['center'][0] + radius * math.cos(angle)
        world_y = zone['center'][1] + radius * math.sin(angle)

        if is_valid_spawn_position(world_x, world_y, container_cols, container_rows,
                                    rayline_points, existing_containers, current_layer):
            screen_x = world_to_screen_x(world_x)
            screen_y = world_to_screen_y(world_y)
            return (screen_x, screen_y, world_x, world_y)

    return None
