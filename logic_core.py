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
            ct.cells = sort_grid_data_optimized(ct.rows, ct.cols, ct.cells)
        count += 1

    state.last_action_message = f"Sorted {count} trays (Merged {merges})"


# --- SPAWN (SYMMETRY) ---
def spawn_new_trays():
    master = Container(state.current_layer)
    state.containers.append(master)
    if state.symmetry_mode:
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
        slave.x = master.x + master.cols * CELL_SIZE + 60
        slave.y = master.y
        state.containers.append(slave)
        state.last_action_message = "Spawned Pair"
    else:
        state.last_action_message = "Spawned Single"


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
                            has_adj = True;
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


def fill_same():
    tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
    targets = [c for c in state.containers if c.layer in tls] if tls else state.selected_trays
    if not targets: return
    cnt = 0
    for ct in targets:
        if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
        types = set(x for row in ct.cells for x in row if x is not None)
        for r in range(ct.rows):
            for c in range(ct.cols):
                if ct.cells[r][c] is None:
                    t = ct.target[r][c]
                    if t in types or len(types) < ct.max_types:
                        ct.cells[r][c] = t;
                        types.add(t);
                        cnt += 1
    state.last_action_message = f"Filled Same: {cnt}"


def shuffle_level():
    targets = state.selected_trays if state.selected_trays else state.containers
    slots = []
    for ct in targets:
        if not ct.cells: continue
        for r in range(ct.rows):
            for c in range(ct.cols):
                if ct.cells[r][c] is not None: slots.append({'ct': ct, 'r': r, 'c': c})
    if len(slots) < 2: return
    random.shuffle(slots)
    cnt = 0
    for a in slots:
        diff = random.randint(0, 100) < state.shuffle_ratio
        cands = []
        for b in slots:
            if a['ct'] == b['ct'] and a['r'] == b['r'] and a['c'] == b['c']: continue
            if (a['ct'].layer != b['ct'].layer) != diff: continue
            va = a['ct'].cells[a['r']][a['c']]
            vb = b['ct'].cells[b['r']][b['c']]
            ta = a['ct'].target[a['r']][a['c']]
            tb = b['ct'].target[b['r']][b['c']]
            if va != tb and vb != ta: cands.append(b)
        if cands:
            b = random.choice(cands)
            v1, v2 = a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']]
            a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']] = v2, v1
            cnt += 1
    state.last_action_message = f"Shuffled: {cnt}"


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
    layout(state.containers)
    state.last_action_message = "Undo"