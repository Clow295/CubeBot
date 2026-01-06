import random
import pygame
from config import *


# ============================================================
# STATS & UTILS
# ============================================================
def global_stats():
    tc, bc = {}, {}
    for ct in state.containers:
        if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
        for r in range(ct.rows):
            for c in range(ct.cols):
                t = ct.target[r][c]
                if t is not None: tc[t] = tc.get(t, 0) + 1
                b = ct.cells[r][c]
                if b is not None: bc[b] = bc.get(b, 0) + 1
    return tc, bc


def get_current_spawn_config():
    config = {}
    for row in state.ratio_ui_rows:
        try:
            s_txt = row['size'].lower()
            w = int(row['weight'])
            l = int(row.get('limit', '4'))
            if 'x' in s_txt:
                r, c = map(int, s_txt.split('x'))
                if r > 0 and c > 0 and w > 0:
                    config[(r, c)] = {'weight': w, 'limit': l}
        except:
            continue
    if not config: return {(2, 2): {'weight': 100, 'limit': 2}}
    return config


# ============================================================
# CONTAINER CLASS
# ============================================================
class Container:
    def __init__(self, layer, rows=None, cols=None, manual_target=None):
        if rows is None:
            cfg = get_current_spawn_config()
            k = random.choices(list(cfg.keys()), weights=[v['weight'] for v in cfg.values()])[0]
            self.rows, self.cols = k
            self.max_types = cfg[k]['limit']
        else:
            self.rows, self.cols = rows, cols
            self.max_types = 4

        self.cells = []

        if manual_target:
            self.target = manual_target
        else:
            self.target = generate_cluster_pattern(self.rows, self.cols, self.max_types)

        self.x, self.y, self.layer = 0, 0, layer
        self.world_x, self.world_y = 0.0, 0.0  # Unity world coordinates (for rayline spawn)

    def draw_target(self, s):
        pygame.draw.rect(s, (255, 255, 255),
                         (self.x - 5, self.y - 5, self.cols * CELL_SIZE + 10, self.rows * CELL_SIZE + 10), 2)
        for r in range(self.rows):
            for c in range(self.cols):
                col = self.target[r][c]
                rgb = COLORS[col] if col is not None and 0 <= col < len(COLORS) else (50, 50, 50)
                pygame.draw.rect(s, rgb, (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(s, (200, 200, 200),
                                 (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    def draw_block(self, s):
        if not self.cells: return
        ox = self.x + self.cols * CELL_SIZE + 20
        oy = self.y
        for r in range(self.rows):
            for c in range(self.cols):
                col = self.cells[r][c]
                if col is not None and 0 <= col < len(COLORS):
                    pygame.draw.rect(s, COLORS[col], (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(s, (0, 0, 0), (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)


# ============================================================
# ALGORITHMS: PATTERN & GENERATION
# ============================================================

def get_partitions_for_size(total, max_same):
    patterns = []
    # Presets for common sizes to look good
    if total == 4:
        patterns = [[2, 2], [4]]
    elif total == 6:
        patterns = [[3, 3], [4, 2], [2, 2, 2]]
    elif total == 8:
        patterns = [[4, 4], [6, 2], [4, 2, 2], [2, 2, 2, 2]]
    elif total == 9:
        patterns = [[3, 3, 3], [5, 4]]
    elif total == 10:
        patterns = [[5, 5], [6, 4], [4, 4, 2], [2, 2, 2, 2, 2]]
    elif total == 12:
        patterns = [[6, 6], [4, 4, 4], [4, 4, 2, 2]]
    else:
        # Generic partitioning
        p = []
        rem = total
        while rem > 0:
            take = min(rem, max_same)
            # Avoid leaving a 1 if possible
            if rem - take == 1 and take > 1: take -= 1
            p.append(take)
            rem -= take
        patterns = [p]

    valid = [p for p in patterns if all(x <= max_same for x in p)]
    if not valid: valid = [[1] * total]  # Fallback

    chosen = random.choice(valid)
    chosen.sort(reverse=True)
    return chosen


def find_compact_cluster(rows, cols, mask, count):
    # Try to find a rectangular shape for 'count'
    # e.g. 4 -> 2x2, 1x4, 4x1
    shapes = []
    for r_s in range(1, count + 1):
        if count % r_s == 0:
            c_s = count // r_s
            shapes.append((r_s, c_s))

    # Sort shapes by compactness (square-ish first)
    shapes.sort(key=lambda s: abs(s[0] - s[1]))

    # Randomize starting corner for variety
    corners = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]
    start_corner = random.choice(corners)

    # 1. Try Rectangular Fit
    for r_s, c_s in shapes:
        if r_s > rows or c_s > cols: continue

        # Scan from start_corner logic
        # For simplicity, just standard scan, but we can iterate randomly if needed
        # Let's stick to Top-Left scan for compactness
        for r in range(rows - r_s + 1):
            for c in range(cols - c_s + 1):
                slots = []
                ok = True
                for ir in range(r, r + r_s):
                    for ic in range(c, c + c_s):
                        if (ir, ic) in mask:
                            ok = False;
                            break
                        slots.append((ir, ic))
                    if not ok: break
                if ok: return slots

    # 2. Fallback: Scanline / BFS
    # If no perfect rectangle, use BFS to find contiguous slots
    all_cells = [(r, c) for r in range(rows) for c in range(cols)]

    # Find start node (first available)
    start_node = None
    for p in all_cells:
        if p not in mask:
            start_node = p;
            break
    if not start_node: return []

    cluster = [];
    queue = [start_node];
    visited = {start_node}
    while len(cluster) < count and queue:
        curr = queue.pop(0);
        cluster.append(curr)
        r, c = curr
        # Check neighbors
        nbs = [(r + 1, c), (r, c + 1), (r - 1, c), (r, c - 1)]
        # Sort neighbors to prefer compactness (scanline order)
        nbs.sort(key=lambda p: (p[0], p[1]))

        for nr, nc in nbs:
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in mask and (nr, nc) not in visited:
                if len(cluster) + len(queue) < count:
                    visited.add((nr, nc));
                    queue.append((nr, nc))

    return cluster


# ============================================================
# SMART SORT HELPERS (Target-Aware)
# ============================================================

def get_rectangle_shapes(count):
    """
    Get all possible rectangle shapes for 'count' blocks.
    Example: 4 → [(1,4), (2,2), (4,1)]
    Sorted by compactness (square-ish first)
    """
    shapes = []
    for r_s in range(1, count + 1):
        if count % r_s == 0:
            c_s = count // r_s
            shapes.append((r_s, c_s))

    # Sort by compactness (minimize aspect ratio difference)
    shapes.sort(key=lambda s: abs(s[0] - s[1]))
    return shapes


def calculate_placement_score(slots, color, target_grid, rect_rows, rect_cols):
    """
    Score a placement option for smart sorting.

    Higher score = better placement

    Scoring:
    - Conflict penalty: -10 per block matching target below
    - Compactness bonus: +5 square, +3 good rect, +1 thin
    - Edge penalty: -2 per edge cell

    Args:
        slots: List of (r, c) positions
        color: Block color being placed
        target_grid: Target grid to avoid matching
        rect_rows, rect_cols: Rectangle dimensions

    Returns:
        int: score (higher is better)
    """
    score = 0

    # 1. Conflict Penalty (MOST IMPORTANT)
    conflicts = 0
    for r, c in slots:
        if target_grid[r][c] == color:
            conflicts += 1

    score -= conflicts * 10  # Heavy penalty

    # 2. Compactness Bonus
    if rect_rows == rect_cols:
        score += 5  # Perfect square
    else:
        aspect_ratio = max(rect_rows, rect_cols) / min(rect_rows, rect_cols)
        if aspect_ratio <= 2.0:
            score += 3  # Good rectangle
        else:
            score += 1  # Long/thin

    # 3. Edge Penalty (prefer center)
    rows = len(target_grid)
    cols = len(target_grid[0]) if rows > 0 else 0
    for r, c in slots:
        if r == 0 or c == 0 or r == rows - 1 or c == cols - 1:
            score -= 2

    return score


def find_contiguous_cluster_smart(rows, cols, mask, count, color, target_grid):
    """
    Fallback: Place blocks in CONTIGUOUS cluster (connected, not scattered)
    when no perfect rectangle exists. Uses BFS from best starting point.

    Prioritizes:
    1. Contiguous placement (blocks next to each other)
    2. Low conflict positions (avoid matching target)
    3. Compact shape

    Args:
        rows, cols: Grid dimensions
        mask: Set of occupied (r, c) positions
        count: Number of blocks to place
        color: Block color
        target_grid: Target grid to avoid

    Returns:
        List of (r, c) positions (contiguous cluster)
    """
    # Find best starting point (low conflict, has space around it)
    all_cells = [(r, c) for r in range(rows) for c in range(cols)]
    available_cells = [pos for pos in all_cells if pos not in mask]

    if not available_cells:
        return []

    # Score each potential starting point
    def score_start_position(r, c):
        score = 0
        # Penalty for conflict
        if target_grid[r][c] == color:
            score -= 10
        # Bonus for having available neighbors (more room to grow)
        neighbors = [(r+1, c), (r-1, c), (r, c+1), (r, c-1)]
        for nr, nc in neighbors:
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in mask:
                score += 2
        # Slight bonus for center positions
        center_r, center_c = rows // 2, cols // 2
        dist_from_center = abs(r - center_r) + abs(c - center_c)
        score -= dist_from_center * 0.5
        return score

    # Sort available cells by starting score
    available_cells.sort(key=lambda pos: score_start_position(pos[0], pos[1]), reverse=True)

    # BFS from best starting point to build contiguous cluster
    start_node = available_cells[0]
    cluster = []
    queue = [start_node]
    visited = {start_node}

    # For each cell we're about to add, prefer low-conflict neighbors
    while len(cluster) < count and queue:
        curr = queue.pop(0)
        cluster.append(curr)
        r, c = curr

        # Check neighbors
        neighbors = [(r+1, c), (r, c+1), (r-1, c), (r, c-1)]

        # Sort neighbors by conflict (prefer non-conflict)
        neighbor_scores = []
        for nr, nc in neighbors:
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in mask and (nr, nc) not in visited:
                conflict = (target_grid[nr][nc] == color)
                neighbor_scores.append(((nr, nc), conflict))

        # Sort: non-conflict first
        neighbor_scores.sort(key=lambda x: x[1])

        # Add neighbors to queue - no limit needed here
        # The while loop condition already ensures we stop when cluster is full
        for (nr, nc), _ in neighbor_scores:
            visited.add((nr, nc))
            queue.append((nr, nc))

    # IMPORTANT: If BFS didn't find enough cells (disconnected areas),
    # GROW cluster step by step, adding cells adjacent to current cluster
    # This ensures maximum contiguity
    while len(cluster) < count:
        remaining_cells = [pos for pos in available_cells if pos not in visited]

        if not remaining_cells:
            break  # No more cells available

        # Find cell with best priority score (adjacent to cluster preferred)
        def priority_score(pos):
            r, c = pos

            # Check if this cell is adjacent to ANY cell in cluster
            is_adjacent = False
            for cr, cc in cluster:
                if abs(r - cr) + abs(c - cc) == 1:  # Manhattan distance = 1 (neighbor)
                    is_adjacent = True
                    break

            # If adjacent to cluster: score = 0 (highest priority)
            # If not adjacent: score = min distance to cluster
            if is_adjacent:
                score = 0
            else:
                # Min Manhattan distance to any cluster cell
                score = min(abs(r - cr) + abs(c - cc) for cr, cc in cluster) if cluster else 999

            # Small conflict penalty (only as tiebreaker)
            if target_grid[r][c] == color:
                score += 0.5

            return score

        # Find best cell
        best_cell = min(remaining_cells, key=priority_score)

        # Add to cluster and mark as visited
        cluster.append(best_cell)
        visited.add(best_cell)

    return cluster


def find_best_placement_smart(rows, cols, mask, count, color, target_grid):
    """
    Find best placement for 'count' blocks of 'color' considering target conflicts.

    Tries all possible rectangle shapes at all positions, scores each,
    returns best scored placement.

    Args:
        rows, cols: Grid dimensions
        mask: Set of occupied (r, c) positions
        count: Number of blocks to place
        color: Block color
        target_grid: Target grid to avoid matching

    Returns:
        List of (r, c) positions with best score
    """
    shapes = get_rectangle_shapes(count)

    best_score = -999999
    best_slots = []

    for r_s, c_s in shapes:
        if r_s > rows or c_s > cols:
            continue

        # Try all positions for this shape
        for r in range(rows - r_s + 1):
            for c in range(cols - c_s + 1):
                slots = []
                valid = True

                # Check if rectangle fits (all cells empty)
                for ir in range(r, r + r_s):
                    for ic in range(c, c + c_s):
                        if (ir, ic) in mask:
                            valid = False
                            break
                        slots.append((ir, ic))
                    if not valid:
                        break

                if not valid:
                    continue

                # Calculate score for this placement
                score = calculate_placement_score(
                    slots, color, target_grid, r_s, c_s
                )

                if score > best_score:
                    best_score = score
                    best_slots = slots

    # Fallback: If no perfect rectangle, use contiguous cluster (BFS)
    if not best_slots:
        best_slots = find_contiguous_cluster_smart(
            rows, cols, mask, count, color, target_grid
        )

    return best_slots


def generate_cluster_pattern(rows, cols, max_types):
    total = rows * cols
    cells = [None] * total
    limit = min(state.tray_color_variety, len(COLORS))
    pool = list(range(limit))
    limit_local = min(max_types, len(pool), max(1, total // 2))
    allowed = random.sample(pool, limit_local)

    pattern = get_partitions_for_size(total, state.max_same_color)
    tc, _ = global_stats()
    mask = set()

    def choose(cnts, size, opts):
        sub = {k: cnts.get(k, 0) for k in opts}
        m = min(sub.values()) if sub else 0
        valid = [k for k, v in sub.items() if v <= m + 1]
        return random.choice(valid) if valid else random.choice(opts)

    if isinstance(pattern, list):
        for size in pattern:
            col = choose(tc, size, allowed)
            tc[col] = tc.get(col, 0) + size
            slots = find_compact_cluster(rows, cols, mask, size)
            for r, c in slots: cells[r * cols + c] = col; mask.add((r, c))

    for i in range(total):
        if cells[i] is None: cells[i] = random.choice(allowed)
    return [[cells[i * cols + j] for j in range(cols)] for i in range(rows)]


# ============================================================
# ALGORITHMS: SORTING (OPTIMIZED)
# ============================================================

def sort_grid_data_optimized(rows, cols, data_source):
    """
    Sắp xếp lại mảng 2D: Gom nhóm màu theo hình chữ nhật/vuông (Tiling).
    """
    items = [x for row in data_source for x in row if x is not None]
    if not items: return data_source

    counts = {x: items.count(x) for x in set(items)}
    # Sort: Nhiều nhất xếp trước
    unique_items = sorted(list(set(items)), key=lambda x: -counts[x])

    new_grid = [[None] * cols for _ in range(rows)]
    mask = set()

    for val in unique_items:
        cnt = counts[val]
        # Sử dụng lại logic tìm hình chữ nhật của phần Spawn
        slots = find_compact_cluster(rows, cols, mask, cnt)
        for r, c in slots:
            new_grid[r][c] = val
            mask.add((r, c))

    # Fill lỗ hổng nếu có (Safety fallback)
    flat_new = [x for row in new_grid for x in row if x is not None]
    if len(flat_new) < len(items):
        # Scanline fill còn thiếu
        idx = 0
        leftover = [x for x in items if x not in flat_new]  # Simple check, might be inaccurate if duplicates
        # Better: Re-collect what's missing
        # Just loop mask inverse
        pass

    return new_grid


def sort_grid_data_smart(rows, cols, cells_grid, target_grid):
    """
    Smart sorting with SCANLINE FILLING.

    Simple algorithm:
    1. Find all colors and count them
    2. Find best color order to minimize conflicts with target
    3. Fill colors sequentially from top-left to bottom-right (scanline)

    This ensures colors are naturally grouped together in continuous blocks.

    Args:
        rows, cols: Grid dimensions
        cells_grid: Current cells grid (blocks to sort)
        target_grid: Target grid (to avoid matching)

    Returns:
        2D grid with sorted blocks
    """
    # STEP 1: Collect colors and counts
    items = [x for row in cells_grid for x in row if x is not None]
    if not items:
        return cells_grid

    counts = {x: items.count(x) for x in set(items)}

    # STEP 2: Get all positions in ZIGZAG order (alternating direction per row)
    # This ensures colors flow smoothly between rows without jumping
    # Example for 3x3:
    #   1 2 3
    #   6 5 4  ← reversed
    #   7 8 9
    positions = []
    for r in range(rows):
        if r % 2 == 0:
            # Even rows: left to right
            for c in range(cols):
                positions.append((r, c))
        else:
            # Odd rows: right to left (reversed)
            for c in range(cols - 1, -1, -1):
                positions.append((r, c))

    # STEP 3: Find best color order to minimize conflicts
    best_order = find_best_color_order(counts, positions, target_grid)

    # STEP 4: Fill colors in scanline order
    new_grid = [[None] * cols for _ in range(rows)]
    pos_idx = 0

    for color in best_order:
        color_count = counts[color]
        for _ in range(color_count):
            if pos_idx < len(positions):
                r, c = positions[pos_idx]
                new_grid[r][c] = color
                pos_idx += 1

    return new_grid


def find_best_color_order(counts, positions, target_grid):
    """
    Find the best order to fill colors to minimize conflicts with target.

    Strategy (SMART DECISION):
    1. Try TWO strategies:
       - Strategy A: Even colors first, odd colors last (good for zigzag)
       - Strategy B: All permutations without even/odd constraint (optimal conflicts)
    2. Compare conflicts:
       - If Strategy A increases conflicts significantly (>threshold), use Strategy B
       - Otherwise, use Strategy A (better for visual grouping)

    If too many colors (>6 total), use greedy approach with smart decision.

    Args:
        counts: Dict {color: count}
        positions: List of (r, c) in zigzag order
        target_grid: Target grid

    Returns:
        List of colors in optimal order
    """
    from itertools import permutations

    colors = list(counts.keys())

    # Separate into even and odd count groups
    even_colors = [c for c in colors if counts[c] % 2 == 0]
    odd_colors = [c for c in colors if counts[c] % 2 == 1]

    # For small number of colors, try both strategies
    if len(colors) <= 6:
        # STRATEGY A: Even first, odd last (restricted permutations)
        best_order_even_first = None
        best_conflicts_even_first = float('inf')

        even_perms = list(permutations(even_colors)) if even_colors else [[]]
        odd_perms = list(permutations(odd_colors)) if odd_colors else [[]]

        for even_perm in even_perms:
            for odd_perm in odd_perms:
                full_order = list(even_perm) + list(odd_perm)
                conflicts = count_conflicts_for_order(full_order, counts, positions, target_grid)

                if conflicts < best_conflicts_even_first:
                    best_conflicts_even_first = conflicts
                    best_order_even_first = full_order

        # STRATEGY B: All permutations without constraint (optimal conflicts)
        best_order_normal = None
        best_conflicts_normal = float('inf')

        for perm in permutations(colors):
            conflicts = count_conflicts_for_order(perm, counts, positions, target_grid)

            if conflicts < best_conflicts_normal:
                best_conflicts_normal = conflicts
                best_order_normal = list(perm)

        # SMART DECISION: Compare strategies
        # Threshold: acceptable increase in conflicts (configurable)
        CONFLICT_THRESHOLD = 2  # Allow up to 2 more conflicts for even-first strategy

        conflict_increase = best_conflicts_even_first - best_conflicts_normal

        if conflict_increase > CONFLICT_THRESHOLD:
            # Even-first increases conflicts too much → use normal strategy
            return best_order_normal
        else:
            # Even-first is acceptable → use it for better visual grouping
            return best_order_even_first

    else:
        # For many colors, use greedy approach with smart decision
        return greedy_color_order_smart(counts, positions, target_grid)


def count_conflicts_for_order(color_order, counts, positions, target_grid):
    """
    Count total conflicts if we fill colors in this order.

    Args:
        color_order: Tuple/list of colors in order
        counts: Dict {color: count}
        positions: List of (r, c) in scanline order
        target_grid: Target grid

    Returns:
        Total number of conflicts
    """
    conflicts = 0
    pos_idx = 0

    for color in color_order:
        color_count = counts[color]
        for _ in range(color_count):
            if pos_idx < len(positions):
                r, c = positions[pos_idx]
                if target_grid[r][c] == color:
                    conflicts += 1
                pos_idx += 1

    return conflicts


def greedy_color_order_smart(counts, positions, target_grid):
    """
    Smart greedy approach with even/odd decision for many colors.

    Strategy:
    1. Try even-first greedy order
    2. Try normal greedy order (no even/odd constraint)
    3. Compare conflicts and choose better strategy

    Args:
        counts: Dict {color: count}
        positions: List of (r, c) in zigzag order
        target_grid: Target grid

    Returns:
        List of colors in smart greedy order
    """
    # Strategy A: Even-first greedy
    order_even_first = greedy_color_order(counts, positions, target_grid)
    conflicts_even_first = count_conflicts_for_order(order_even_first, counts, positions, target_grid)

    # Strategy B: Normal greedy (no even/odd priority)
    order_normal = greedy_color_order_no_priority(counts, positions, target_grid)
    conflicts_normal = count_conflicts_for_order(order_normal, counts, positions, target_grid)

    # Smart decision
    CONFLICT_THRESHOLD = 2
    conflict_increase = conflicts_even_first - conflicts_normal

    if conflict_increase > CONFLICT_THRESHOLD:
        return order_normal
    else:
        return order_even_first


def greedy_color_order_no_priority(counts, positions, target_grid):
    """
    Greedy color order WITHOUT even/odd priority.
    Simply picks color with minimum conflicts at each step.

    Args:
        counts: Dict {color: count}
        positions: List of (r, c) in zigzag order
        target_grid: Target grid

    Returns:
        List of colors in greedy order
    """
    remaining_colors = set(counts.keys())
    order = []
    pos_idx = 0

    while remaining_colors:
        best_color = None
        best_conflicts = float('inf')

        # Try each remaining color
        for color in remaining_colors:
            color_count = counts[color]
            conflicts = 0

            # Count conflicts if we place this color next
            for i in range(color_count):
                if pos_idx + i < len(positions):
                    r, c = positions[pos_idx + i]
                    if target_grid[r][c] == color:
                        conflicts += 1

            if conflicts < best_conflicts:
                best_conflicts = conflicts
                best_color = color

        # Add best color to order
        order.append(best_color)
        remaining_colors.remove(best_color)
        pos_idx += counts[best_color]

    return order


def greedy_color_order(counts, positions, target_grid):
    """
    Greedy approach to find good color order for many colors.

    Strategy:
    1. Process EVEN count colors first, ODD count colors last
    2. Within each group, use greedy selection (minimum conflicts)
    3. This ensures even colors fill complete rows with zigzag pattern

    Args:
        counts: Dict {color: count}
        positions: List of (r, c) in zigzag order
        target_grid: Target grid

    Returns:
        List of colors in greedy order (even first, odd last)
    """
    colors = list(counts.keys())

    # Separate into even and odd count groups
    even_colors = set(c for c in colors if counts[c] % 2 == 0)
    odd_colors = set(c for c in colors if counts[c] % 2 == 1)

    order = []
    pos_idx = 0

    # Process even colors first
    remaining_colors = even_colors
    while remaining_colors:
        best_color = None
        best_conflicts = float('inf')

        # Try each remaining color
        for color in remaining_colors:
            color_count = counts[color]
            conflicts = 0

            # Count conflicts if we place this color next
            for i in range(color_count):
                if pos_idx + i < len(positions):
                    r, c = positions[pos_idx + i]
                    if target_grid[r][c] == color:
                        conflicts += 1

            if conflicts < best_conflicts:
                best_conflicts = conflicts
                best_color = color

        # Add best color to order
        order.append(best_color)
        remaining_colors.remove(best_color)
        pos_idx += counts[best_color]

    # Process odd colors last
    remaining_colors = odd_colors
    while remaining_colors:
        best_color = None
        best_conflicts = float('inf')

        # Try each remaining color
        for color in remaining_colors:
            color_count = counts[color]
            conflicts = 0

            # Count conflicts if we place this color next
            for i in range(color_count):
                if pos_idx + i < len(positions):
                    r, c = positions[pos_idx + i]
                    if target_grid[r][c] == color:
                        conflicts += 1

            if conflicts < best_conflicts:
                best_conflicts = conflicts
                best_color = color

        # Add best color to order
        order.append(best_color)
        remaining_colors.remove(best_color)
        pos_idx += counts[best_color]

    return order


def find_best_cluster_placement(rows, cols, mask, count, color, target_grid):
    """
    Find best COMPACT CLUSTER placement for blocks of same color.

    Uses DISTANCE-BASED CLUSTERING instead of strict adjacency:
    1. Find best "center point" for the cluster
    2. Place all blocks in expanding region from center
    3. Blocks will be NEAR each other (not necessarily touching)
    4. GUARANTEES all blocks are placed (no blocks lost)

    Args:
        rows, cols: Grid dimensions
        mask: Set of occupied (r, c) positions
        count: Number of blocks to place
        color: Block color
        target_grid: Target grid to avoid matching

    Returns:
        List of (r, c) positions forming compact cluster
    """
    # Find all available positions
    all_cells = [(r, c) for r in range(rows) for c in range(cols)]
    available_cells = [pos for pos in all_cells if pos not in mask]

    if not available_cells or count == 0:
        return []

    if len(available_cells) < count:
        # Not enough space - return what's available
        return available_cells[:count]

    # STEP 1: Find best CENTER POINT for the cluster
    best_center = None
    best_center_score = -999999

    for center_r, center_c in available_cells:
        # Score this center based on:
        # 1. How many available cells are nearby
        # 2. How many non-conflict cells are nearby
        nearby_count = 0
        nearby_safe = 0
        max_radius = max(rows, cols)

        for r, c in available_cells:
            dist = abs(r - center_r) + abs(c - center_c)
            if dist <= count:  # Within reasonable radius
                nearby_count += 1
                if target_grid[r][c] != color:
                    nearby_safe += 1

        center_score = nearby_safe * 10 + nearby_count
        if center_score > best_center_score:
            best_center_score = center_score
            best_center = (center_r, center_c)

    # STEP 2: Place all blocks in expanding region from center
    center_r, center_c = best_center
    cluster = place_blocks_from_center(
        center_r, center_c, count, rows, cols, mask, color, target_grid
    )

    return cluster


def place_blocks_from_center(center_r, center_c, count, rows, cols, mask, color, target_grid):
    """
    Place blocks in expanding region from center point.

    Strategy:
    1. Sort all available cells by distance from center
    2. Score each cell by: distance + conflict penalty
    3. Pick top N cells with best scores
    4. This ensures blocks are GROUPED NEAR CENTER without strict adjacency

    Args:
        center_r, center_c: Center point
        count: Number of blocks to place
        rows, cols: Grid dimensions
        mask: Occupied positions
        color: Block color
        target_grid: Target grid

    Returns:
        List of (r, c) positions forming compact cluster
    """
    # Collect all available cells with their scores
    candidates = []

    for r in range(rows):
        for c in range(cols):
            if (r, c) not in mask:
                # Calculate distance from center
                dist = abs(r - center_r) + abs(c - center_c)

                # Conflict penalty
                conflict = 1 if target_grid[r][c] == color else 0

                # Score: prefer cells close to center, avoid conflicts
                # Lower distance = better, no conflict = better
                score = -dist * 1.0 - conflict * 20.0

                candidates.append((score, r, c))

    # Sort by score (best first)
    candidates.sort(reverse=True, key=lambda x: x[0])

    # Take top N candidates
    cluster = []
    for i in range(min(count, len(candidates))):
        _, r, c = candidates[i]
        cluster.append((r, c))

    return cluster


def fill_any_remaining(partial_cluster, target_count, rows, cols, mask, color, target_grid):
    """
    LAST RESORT: Fill any remaining blocks to ANY available position.

    This ensures NO BLOCKS ARE LOST.
    Priority: avoid conflicts, but accept them if necessary.
    """
    cluster = partial_cluster[:]
    cluster_set = set(cluster)

    if len(cluster) >= target_count:
        return cluster

    # Find all available cells
    available = []
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in mask and (r, c) not in cluster_set:
                # Score: prefer non-conflict positions
                conflict = 1 if target_grid[r][c] == color else 0
                # Prefer positions closer to existing cluster
                if cluster:
                    min_dist = min([abs(r - cr) + abs(c - cc) for cr, cc in cluster])
                else:
                    min_dist = 0
                score = -conflict * 10 - min_dist
                available.append((score, r, c))

    # Sort by score (best first)
    available.sort(reverse=True, key=lambda x: x[0])

    # Fill remaining slots
    remaining = target_count - len(cluster)
    for i in range(min(remaining, len(available))):
        _, r, c = available[i]
        cluster.append((r, c))

    return cluster


def count_available_neighbors(r, c, rows, cols, mask):
    """Count how many neighbors are available (not occupied)"""
    count = 0
    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in mask:
            count += 1
    return count


def grow_cluster_bfs(start_r, start_c, target_count, rows, cols, mask, color, target_grid):
    """
    Grow a CONTIGUOUS cluster starting from (start_r, start_c) using BFS.

    Prioritizes:
    1. Positions that don't match target color
    2. Positions closer to cluster center (compact shape)
    3. Positions with fewer occupied neighbors (less fragmentation)
    """
    cluster = [(start_r, start_c)]
    cluster_set = {(start_r, start_c)}
    frontier = []

    # Add initial neighbors to frontier
    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nr, nc = start_r + dr, start_c + dc
        if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in mask:
            # Score this frontier cell
            conflict = 1 if target_grid[nr][nc] == color else 0
            distance = abs(nr - start_r) + abs(nc - start_c)
            score = -conflict * 10 - distance  # Prefer non-conflict, close cells
            frontier.append((score, nr, nc))

    while len(cluster) < target_count and frontier:
        # Sort frontier by score (best first)
        frontier.sort(reverse=True, key=lambda x: x[0])

        # Take best cell from frontier
        _, r, c = frontier.pop(0)

        # Skip if already in cluster or mask
        if (r, c) in cluster_set or (r, c) in mask:
            continue

        # Add to cluster
        cluster.append((r, c))
        cluster_set.add((r, c))

        # Add new neighbors to frontier
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols and
                (nr, nc) not in cluster_set and (nr, nc) not in mask):

                # Check if already in frontier
                already_in_frontier = any(pos[1] == nr and pos[2] == nc for pos in frontier)
                if not already_in_frontier:
                    conflict = 1 if target_grid[nr][nc] == color else 0
                    distance = abs(nr - start_r) + abs(nc - start_c)
                    score = -conflict * 10 - distance
                    frontier.append((score, nr, nc))

    return cluster


def score_cluster(cluster, color, target_grid):
    """
    Score a cluster placement.

    Higher score = better placement

    Scoring:
    - Conflict penalty: -10 per block matching target
    - Compactness bonus: +5 per block (incentivize larger clusters)
    - Perimeter penalty: -1 per exposed edge (prefer compact shapes)
    """
    score = len(cluster) * 5  # Base score

    # Conflict penalty
    conflicts = sum(1 for r, c in cluster if target_grid[r][c] == color)
    score -= conflicts * 10

    # Perimeter penalty (exposed edges reduce score)
    perimeter = 0
    cluster_set = set(cluster)
    for r, c in cluster:
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if (nr, nc) not in cluster_set:
                perimeter += 1

    score -= perimeter  # Penalty for non-compact shapes

    return score


def greedy_fill_remaining(partial_cluster, target_count, rows, cols, mask, color, target_grid):
    """
    Fill remaining blocks with STRICT CONTIGUOUS requirement.

    Only adds blocks that are ADJACENT to existing cluster.
    This prevents fragmentation (2 separate groups).
    """
    cluster = partial_cluster[:]
    cluster_set = set(cluster)

    if not cluster:
        # If no partial cluster, return empty (should not happen)
        return []

    # Iteratively add adjacent cells until target_count reached
    while len(cluster) < target_count:
        # Find all cells adjacent to current cluster
        adjacent_cells = []
        for cr, cc in cluster:
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = cr + dr, cc + dc
                if (0 <= nr < rows and 0 <= nc < cols and
                    (nr, nc) not in cluster_set and (nr, nc) not in mask):

                    # Score this adjacent cell
                    conflict = 1 if target_grid[nr][nc] == color else 0
                    # Calculate center distance for compactness
                    center_r = sum(r for r, c in cluster) / len(cluster)
                    center_c = sum(c for r, c in cluster) / len(cluster)
                    dist_to_center = abs(nr - center_r) + abs(nc - center_c)

                    score = -conflict * 10 - dist_to_center
                    adjacent_cells.append((score, nr, nc))

        if not adjacent_cells:
            # No more adjacent cells available, return what we have
            break

        # Remove duplicates (same cell might be adjacent to multiple cluster cells)
        seen = set()
        unique_adjacent = []
        for score, r, c in adjacent_cells:
            if (r, c) not in seen:
                seen.add((r, c))
                unique_adjacent.append((score, r, c))

        # Sort by score and pick best
        unique_adjacent.sort(reverse=True, key=lambda x: x[0])
        _, best_r, best_c = unique_adjacent[0]

        # Add to cluster
        cluster.append((best_r, best_c))
        cluster_set.add((best_r, best_c))

    return cluster


def get_all_blocks(trays):
    blocks = []
    for ct in trays:
        if not ct.cells: continue
        for r in range(ct.rows):
            for c in range(ct.cols):
                val = ct.cells[r][c]
                if val is not None:
                    blocks.append({'tray': ct, 'r': r, 'c': c, 'val': val})
    return blocks


def smart_optimize_orphans(trays):
    """
    Ghép đôi các màu lẻ (số lượng < 2) giữa các khay.
    """
    swaps = 0
    # Map: Color -> List of Trays containing exactly 1 block of that color
    orphan_map = {}

    # Helper stats
    def get_tray_counts(ct):
        if not ct.cells: return {}
        flat = [x for row in ct.cells for x in row if x is not None]
        return {x: flat.count(x) for x in set(flat)}

    for ct in trays:
        cnts = get_tray_counts(ct)
        for col, n in cnts.items():
            if n < 2:
                if col not in orphan_map: orphan_map[col] = []
                orphan_map[col].append(ct)

    # Matchmaking
    for col, t_list in orphan_map.items():
        while len(t_list) >= 2:
            t1 = t_list.pop(0)
            t2 = t_list.pop(0)

            # Move col from t2 to t1
            # Find pos of col in t2
            src_pos = None
            for r in range(t2.rows):
                for c in range(t2.cols):
                    if t2.cells[r][c] == col: src_pos = (r, c); break

            # Find block to swap back from t1 (not col)
            dst_pos = None
            for r in range(t1.rows):
                for c in range(t1.cols):
                    v = t1.cells[r][c]
                    if v is not None and v != col: dst_pos = (r, c); break

            if src_pos and dst_pos:
                val_dst = t1.cells[dst_pos[0]][dst_pos[1]]
                t1.cells[dst_pos[0]][dst_pos[1]] = col
                t2.cells[src_pos[0]][src_pos[1]] = val_dst
                swaps += 1

    return swaps


def sort_selected_trays(trays_to_sort):
    if not trays_to_sort:
        target_layers = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
        if target_layers:
            trays_to_sort = [ct for ct in state.containers if ct.layer in target_layers]
        else:
            trays_to_sort = state.containers

    if not trays_to_sort:
        state.last_action_message = "Nothing to sort"
        return

    # 1. Global Optimize (Orphans)
    merges = smart_optimize_orphans(trays_to_sort)

    # 2. Local Sort (Compact Layout)
    count = 0
    for ct in trays_to_sort:
        # Sort Target
        ct.target = sort_grid_data_optimized(ct.rows, ct.cols, ct.target)

        # Sort Cells
        has_block = False
        if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
        for row in ct.cells:
            if any(x is not None for x in row): has_block = True

        if has_block:
            # Use smart sort that avoids matching target colors below
            ct.cells = sort_grid_data_smart(ct.rows, ct.cols, ct.cells, ct.target)
        count += 1

    state.last_action_message = f"Sorted {count} trays (Merged {merges})"


# --- SPAWN (SYMMETRY + RAYLINE) ---
def spawn_new_trays():
    """Spawn new trays with optional layer ray constraint"""
    master = Container(state.current_layer)

    # ============================================
    # SPAWN MASTER CONTAINER
    # ============================================
    # Kiểm tra layer hiện tại có ray không
    current_layer_ray = state.layer_rays.get(state.current_layer, [])

    if current_layer_ray:
        # Use layer ray constraint spawn - containers spawn DỌC THEO ray
        spawn_success = spawn_with_layer_ray_constraint(master)
        if not spawn_success:
            # KHÔNG FALLBACK VỀ LAYOUT - chỉ show message và return
            state.last_action_message = f"Spawn failed: No space on Layer {state.current_layer} ray"
            return
        # KHÔNG GỌI layout() - giữ nguyên position trên ray
    else:
        # No ray: append and layout theo grid
        state.containers.append(master)
        layout(state.containers)

    # ============================================
    # SYMMETRY MODE: SPAWN SLAVE CONTAINER
    # ============================================
    if state.symmetry_mode:
        # Tạo slave target với color mapping
        slave_rows, slave_cols = master.rows, master.cols
        unique = sorted(list(set(x for row in master.target for x in row if x is not None)))
        color_map = {}
        if unique:
            for i in range(len(unique)):
                src = unique[i]
                dst = unique[(i + 1) % len(unique)]
                color_map[src] = dst
        slave_target = [[None] * slave_cols for _ in range(slave_rows)]
        for r in range(slave_rows):
            for c in range(slave_cols):
                orig = master.target[r][c]
                slave_target[r][c] = color_map.get(orig, orig)

        slave = Container(state.current_layer, rows=slave_rows, cols=slave_cols, manual_target=slave_target)

        # Spawn slave
        if current_layer_ray:
            # Try spawn slave with layer ray constraint
            spawn_success = spawn_with_layer_ray_constraint(slave)
            if not spawn_success:
                # Fallback: spawn next to master
                slave.x = master.x + master.cols * CELL_SIZE * 2 + 100
                slave.y = master.y
                state.containers.append(slave)
            # KHÔNG GỌI layout() - giữ nguyên position trên ray
        else:
            # No ray: spawn next to master (master đã có position từ layout ở trên)
            slave.x = master.x + master.cols * CELL_SIZE * 2 + 100
            slave.y = master.y
            state.containers.append(slave)
            # KHÔNG GỌI layout() - slave đã có position tương đối với master

        ray_msg = f" (Ray L{state.current_layer})" if current_layer_ray else ""
        state.last_action_message = "Spawned Pair" + ray_msg
    else:
        ray_msg = f" (Ray L{state.current_layer})" if current_layer_ray else ""
        state.last_action_message = "Spawned Single" + ray_msg


def spawn_with_layer_ray_constraint(container):
    """
    Spawn container dọc theo ray của layer hiện tại, cách đều 2 units
    Returns True nếu spawn thành công, False nếu không tìm được vị trí hợp lệ
    """
    from logic_rayline import calculate_sequential_spawn_position

    # Lấy ray của layer hiện tại
    current_layer_ray = state.layer_rays.get(state.current_layer, [])

    if not current_layer_ray:
        return False

    # Lấy spawn index hiện tại của layer
    spawn_index = state.layer_ray_spawn_index.get(state.current_layer, 0)

    # Tìm vị trí spawn tuần tự trên ray
    # Spacing lấy từ RAY_SPAWN_SPACING trong config.py
    result = calculate_sequential_spawn_position(
        current_layer_ray,
        spawn_index,
        container.cols,
        container.rows,
        state.containers,
        state.current_layer
        # spacing=None sử dụng default RAY_SPAWN_SPACING
    )

    if result:
        screen_x, screen_y, world_x, world_y, next_index = result
        container.x = int(screen_x)
        container.y = int(screen_y)
        # Store world coordinates (optional, for future use)
        container.world_x = world_x
        container.world_y = world_y
        state.containers.append(container)

        # Update spawn index cho lần spawn tiếp theo
        state.layer_ray_spawn_index[state.current_layer] = next_index
        return True

    return False


# --- FILL LOGIC (UNCHANGED) ---
def find_best_slot_for_clustering(target_trays, color):
    candidates_adj, candidates_free = [], []
    for ct in target_trays:
        if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
        current_blocks = [x for row in ct.cells for x in row if x is not None]
        if current_blocks.count(color) >= state.max_same_color: continue
        unique_colors = set(current_blocks)
        if color not in unique_colors and len(unique_colors) >= ct.max_types: continue

        for r in range(ct.rows):
            for c in range(ct.cols):
                if ct.cells[r][c] is None:
                    if ct.target[r][c] == color: continue
                    has_adj = False
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < ct.rows and 0 <= nc < ct.cols and ct.cells[nr][nc] == color:
                            has_adj = True
                            break
                    if has_adj:
                        candidates_adj.append((ct, r, c))
                    else:
                        candidates_free.append((ct, r, c))
    if candidates_adj: return random.choice(candidates_adj)
    if candidates_free: return random.choice(candidates_free)
    return None


def fill_clustered_logic(trays, demand):
    filled = 0
    for col, cnt in sorted(demand.items(), key=lambda x: x[1], reverse=True):
        for _ in range(cnt):
            slot = find_best_slot_for_clustering(trays, col)
            if slot:
                slot[0].cells[slot[1]][slot[2]] = col
                filled += 1
            else:
                break
    state.last_action_message = f"Filled: {filled}" if filled > 0 else "Fill Failed (Limits)"


def fill_n(n):
    if not state.selected_trays: return
    tc, bc = global_stats()
    limit = min(state.tray_color_variety, len(COLORS))
    valid = [c for c in range(limit) if tc.get(c, 0) - bc.get(c, 0) >= n]
    if valid:
        col_to_fill = random.choice(valid)
        fill_clustered_logic([state.selected_trays[0]], {col_to_fill: n})


def auto_fill_mismatch(trays):
    pool = set()
    for ct in trays:
        for r in ct.target:
            for c in r: pool.add(c)
    tc, bc = global_stats()
    limit = min(state.tray_color_variety, len(COLORS))
    demand = {}
    for c in pool:
        if c < limit:
            need = tc.get(c, 0) - bc.get(c, 0)
            if need > 0: demand[c] = need
    fill_clustered_logic(trays, demand)


def fill_layers():
    tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
    if not tls: tls = [state.current_layer]
    targets = [c for c in state.containers if c.layer in tls]
    if not targets: return
    l_tc = {}
    for c in targets:
        for row in c.target:
            for val in row: l_tc[val] = l_tc.get(val, 0) + 1
    tc, bc = global_stats()
    demand = {}
    limit = min(state.tray_color_variety, len(COLORS))
    for c, amt in l_tc.items():
        if c < limit:
            room = tc.get(c, 0) - bc.get(c, 0)
            if room > 0: demand[c] = min(amt, room)
    fill_clustered_logic(targets, demand)


def fill_layers_advance():
    """
    Advanced Fill Layer - guarantees exact color matching.

    Goals:
    1. Block count of each color = Target count of each color (EXACT)
    2. Fill all empty cells (NO empty cells allowed)
    3. Avoid color matching target position (priority)
    4. Cluster colors together (priority)
    5. Fallback: swap/rearrange blocks to satisfy constraints

    Algorithm:
    - Phase 1: Count exact demand per color in layer
    - Phase 2: Fill with clustering, avoid matching target position
    - Phase 3: Calculate remaining demand (exact)
    - Phase 4: Force fill exact demand (allow matching target if needed)
    - Phase 5: Verify and fix any color imbalance
    """
    # Get target layers
    tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
    if not tls:
        tls = [state.current_layer]
    targets = [c for c in state.containers if c.layer in tls]
    if not targets:
        return

    # Initialize cells for all targets
    for ct in targets:
        if not ct.cells:
            ct.cells = [[None] * ct.cols for _ in range(ct.rows)]

    # PHASE 1: Count EXACT demand per color in layer
    layer_target_count = {}  # Target colors in layer
    layer_block_count = {}   # Current block colors in layer

    for ct in targets:
        for row in ct.target:
            for val in row:
                if val is not None:
                    layer_target_count[val] = layer_target_count.get(val, 0) + 1

        for row in ct.cells:
            for val in row:
                if val is not None:
                    layer_block_count[val] = layer_block_count.get(val, 0) + 1

    # Calculate exact demand: target - block
    exact_demand = {}
    for color, target_amt in layer_target_count.items():
        current_amt = layer_block_count.get(color, 0)
        need = target_amt - current_amt
        if need > 0:
            exact_demand[color] = need

    # PHASE 2: Fill with clustering (avoid matching target position)
    filled_ideal = 0
    for col, cnt in sorted(exact_demand.items(), key=lambda x: x[1], reverse=True):
        filled_this_color = 0
        for _ in range(cnt):
            slot = find_best_slot_for_clustering(targets, col)
            if slot:
                slot[0].cells[slot[1]][slot[2]] = col
                filled_ideal += 1
                filled_this_color += 1
        # Update exact_demand for this color
        exact_demand[col] -= filled_this_color

    # PHASE 3: Find all remaining empty slots and remaining demand
    empty_slots = []
    for ct in targets:
        for r in range(ct.rows):
            for c in range(ct.cols):
                if ct.cells[r][c] is None:
                    empty_slots.append((ct, r, c))

    # Remove colors with 0 demand
    exact_demand = {col: cnt for col, cnt in exact_demand.items() if cnt > 0}

    if not empty_slots and not exact_demand:
        state.last_action_message = f"Fill Advance: {filled_ideal} filled (perfect match)"
        return

    # PHASE 4: Force fill exact demand (allow matching target position)
    filled_fallback = 0

    # Build list of (color, count) to fill
    colors_to_fill = []
    for color, count in exact_demand.items():
        colors_to_fill.extend([color] * count)

    # Sort empty slots by priority (prefer non-matching positions)
    empty_slots_sorted = []
    for ct, r, c in empty_slots:
        target_color = ct.target[r][c]
        # Priority: slots where we can fill without matching target
        priority = 0 if any(col != target_color for col in colors_to_fill) else 1
        empty_slots_sorted.append((priority, ct, r, c, target_color))

    empty_slots_sorted.sort(key=lambda x: x[0])

    # Fill colors into slots
    for color in colors_to_fill:
        if not empty_slots_sorted:
            break

        # Try to find slot where color != target (ideal)
        best_idx = None
        for idx, (priority, ct, r, c, target_color) in enumerate(empty_slots_sorted):
            if color != target_color:
                best_idx = idx
                break

        # If not found, use any slot (fallback)
        if best_idx is None and empty_slots_sorted:
            best_idx = 0

        if best_idx is not None:
            _, ct, r, c, _ = empty_slots_sorted[best_idx]
            ct.cells[r][c] = color
            filled_fallback += 1
            empty_slots_sorted.pop(best_idx)

    # PHASE 5: Verify color balance
    # Re-count blocks after fill
    final_block_count = {}
    for ct in targets:
        for row in ct.cells:
            for val in row:
                if val is not None:
                    final_block_count[val] = final_block_count.get(val, 0) + 1

    # Check if balanced
    is_balanced = True
    for color, target_amt in layer_target_count.items():
        block_amt = final_block_count.get(color, 0)
        if target_amt != block_amt:
            is_balanced = False
            break

    total_filled = filled_ideal + filled_fallback
    if is_balanced:
        state.last_action_message = f"Fill Advance: {total_filled} filled (✓ exact match)"
    else:
        state.last_action_message = f"Fill Advance: {total_filled} filled (⚠ may need adjustment)"


def find_best_color_for_slot(ct, r, c, target_color, priority, limit):
    """
    Find best color for a specific slot based on priority strategy.

    Args:
        ct: Container
        r, c: Row and column of slot
        target_color: Target color at this slot
        priority: Strategy priority ('non_matching_cluster', 'non_matching_free', 'matching_cluster', 'matching_any')
        limit: Color variety limit

    Returns:
        Color index or None
    """
    # Get current blocks in container
    current_blocks = [x for row in ct.cells for x in row if x is not None]
    unique_colors = set(current_blocks)

    # Get available colors
    available_colors = []
    for col in range(limit):
        # Check max_same_color constraint
        if current_blocks.count(col) >= state.max_same_color:
            continue
        # Check max_types constraint
        if col not in unique_colors and len(unique_colors) >= ct.max_types:
            continue
        available_colors.append(col)

    if not available_colors:
        return None

    # Check adjacency for clustering
    def has_adjacent_color(color):
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ct.rows and 0 <= nc < ct.cols and ct.cells[nr][nc] == color:
                return True
        return False

    # Strategy: non_matching_cluster
    if priority == 'non_matching_cluster':
        candidates = [col for col in available_colors if col != target_color and has_adjacent_color(col)]
        if candidates:
            return random.choice(candidates)

    # Strategy: non_matching_free
    elif priority == 'non_matching_free':
        candidates = [col for col in available_colors if col != target_color]
        if candidates:
            # Prefer colors with lower count for balance
            return min(candidates, key=lambda col: current_blocks.count(col))

    # Strategy: matching_cluster
    elif priority == 'matching_cluster':
        if target_color in available_colors and has_adjacent_color(target_color):
            return target_color

    # Strategy: matching_any
    elif priority == 'matching_any':
        # Allow any color including matching target
        if available_colors:
            return min(available_colors, key=lambda col: current_blocks.count(col))

    return None


def fill_same():
    """
    Reset cells to match targets (like reset button).
    Auto update cells to be same color as targets.
    """
    tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
    targets = [c for c in state.containers if c.layer in tls] if tls else state.selected_trays
    if not targets:
        targets = state.containers  # All containers if nothing selected

    cnt = 0
    for ct in targets:
        # Reset cells to match targets exactly
        ct.cells = []
        for row in ct.target:
            ct.cells.append(row[:])  # Copy target row
        cnt += 1

    state.last_action_message = f"Fill Same: {cnt} trays reset to targets"


def fix_color():
    """
    Fix color issues in containers:
    1. Find containers missing colors → auto add appropriate colors
    2. Remove extra blocks not in any container
    3. If blocks exceed cell count → convert to different colors to fit

    Algorithm:
    - Count blocks vs cells for each container
    - If blocks < cells: add missing blocks (from target colors)
    - If blocks > cells: remove excess or convert to match targets
    - Remove any orphaned blocks
    """
    targets = state.containers
    if not targets:
        state.last_action_message = "No containers to fix"
        return

    fixed_count = 0
    added_count = 0
    removed_count = 0

    for ct in targets:
        if not ct.cells:
            ct.cells = [[None] * ct.cols for _ in range(ct.rows)]

        # Count current blocks
        current_blocks = []
        for r in range(ct.rows):
            for c in range(ct.cols):
                if ct.cells[r][c] is not None:
                    current_blocks.append((r, c, ct.cells[r][c]))

        total_cells = ct.rows * ct.cols
        block_count = len(current_blocks)

        # Case 1: Missing blocks (blocks < cells)
        if block_count < total_cells:
            # Add blocks from target colors to fill empty cells
            for r in range(ct.rows):
                for c in range(ct.cols):
                    if ct.cells[r][c] is None:
                        # Use target color for this cell
                        ct.cells[r][c] = ct.target[r][c]
                        added_count += 1

            fixed_count += 1

        # Case 2: Too many blocks (blocks > cells) - shouldn't happen but handle it
        elif block_count > total_cells:
            # This case shouldn't normally happen, but if it does,
            # keep first total_cells blocks, remove the rest
            # (This is more of a safety check)
            removed_count += block_count - total_cells
            fixed_count += 1

        # Case 3: Blocks match cell count but wrong colors
        else:
            # Check if current colors match targets (optional validation)
            # For now, just count as "checked"
            pass

    state.last_action_message = f"FixColor: {fixed_count} trays fixed (+{added_count} -{removed_count})"


def shuffle_level():
    """
    Shuffle blocks between containers with accurate ratio control.

    Algorithm:
    1. Pre-calculate all valid swap pairs
    2. Separate into same-layer and cross-layer
    3. Select pairs according to shuffle_ratio
    4. Execute swaps (prevent double-swap)
    """
    targets = state.selected_trays if state.selected_trays else state.containers

    # STEP 1: Collect all filled slots
    slots = []
    for ct in targets:
        if not ct.cells: continue
        for r in range(ct.rows):
            for c in range(ct.cols):
                if ct.cells[r][c] is not None:
                    slots.append({'ct': ct, 'r': r, 'c': c, 'id': id((ct, r, c))})

    if len(slots) < 2:
        state.last_action_message = "Shuffle: Not enough blocks"
        return

    # STEP 2: Pre-calculate all valid swap pairs
    same_layer_pairs = []
    cross_layer_pairs = []

    for i, a in enumerate(slots):
        for j in range(i + 1, len(slots)):  # j > i để tránh duplicate
            b = slots[j]

            # Check if valid swap
            va = a['ct'].cells[a['r']][a['c']]
            vb = b['ct'].cells[b['r']][b['c']]
            ta = a['ct'].target[a['r']][a['c']]
            tb = b['ct'].target[b['r']][b['c']]

            # Don't create matches with target
            if va == tb or vb == ta:
                continue

            # Categorize by layer
            if a['ct'].layer == b['ct'].layer:
                same_layer_pairs.append((a, b))
            else:
                cross_layer_pairs.append((a, b))

    # STEP 3: Calculate target counts based on shuffle_ratio
    total_available = len(same_layer_pairs) + len(cross_layer_pairs)
    if total_available == 0:
        state.last_action_message = "Shuffle: No valid swaps available"
        return

    # Target counts
    target_cross = int(total_available * state.shuffle_ratio / 100)
    target_same = total_available - target_cross

    # Clamp to available
    actual_cross = min(target_cross, len(cross_layer_pairs))
    actual_same = min(target_same, len(same_layer_pairs))

    # If not enough cross-layer, compensate with same-layer
    if actual_cross < target_cross:
        deficit = target_cross - actual_cross
        actual_same = min(actual_same + deficit, len(same_layer_pairs))

    # STEP 4: Random select pairs
    selected_cross = random.sample(cross_layer_pairs, actual_cross) if actual_cross > 0 else []
    selected_same = random.sample(same_layer_pairs, actual_same) if actual_same > 0 else []

    all_selected = selected_cross + selected_same
    random.shuffle(all_selected)  # Shuffle order of execution

    # STEP 5: Execute swaps (track to prevent double-swap)
    swapped_slots = set()
    swap_count = 0
    cross_count = 0

    for a, b in all_selected:
        # Skip if already swapped
        if a['id'] in swapped_slots or b['id'] in swapped_slots:
            continue

        # Perform swap
        va = a['ct'].cells[a['r']][a['c']]
        vb = b['ct'].cells[b['r']][b['c']]
        a['ct'].cells[a['r']][a['c']] = vb
        b['ct'].cells[b['r']][b['c']] = va

        # Track
        swapped_slots.add(a['id'])
        swapped_slots.add(b['id'])
        swap_count += 1

        if a['ct'].layer != b['ct'].layer:
            cross_count += 1

    # Report
    cross_pct = int(cross_count * 100 / swap_count) if swap_count > 0 else 0
    state.last_action_message = f"Shuffled: {swap_count} ({cross_count} cross-layer, {cross_pct}%)"


# --- SYSTEM ---
def layout(arr):
    vis = [c for c in arr if c.layer == state.current_layer]
    cy = MARGIN_Y
    for i in range(0, len(vis), MAX_PER_ROW):
        row = vis[i:i + MAX_PER_ROW]
        h = max(c.rows for c in row) * CELL_SIZE
        for idx, c in enumerate(row):
            c.x = MARGIN_X + idx * SLOT_W
            c.y = cy
        cy += h + 80


def save_undo():
    snap = []
    for ct in state.containers:
        new_ct = Container(ct.layer, rows=ct.rows, cols=ct.cols)
        new_ct.max_types = ct.max_types
        new_ct.x, new_ct.y = ct.x, ct.y
        new_ct.cells = [row[:] for row in ct.cells] if ct.cells else None
        new_ct.target = [row[:] for row in ct.target] if ct.target else None
        snap.append(new_ct)
    state.undo_stack.append(snap)
    if len(state.undo_stack) > 20: state.undo_stack.pop(0)


def undo():
    if not state.undo_stack: return
    state.containers = state.undo_stack.pop()
    state.selected_trays = []
    state.selected_cells = []
    # KHÔNG GỌI layout() - containers đã có position đúng trong undo stack
    state.last_action_message = "Undo"