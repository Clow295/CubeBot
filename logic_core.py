# # import random
# # import pygame
# # from config import *
# #
# #
# # # ============================================================
# # # STATS & UTILS
# # # ============================================================
# # def global_stats():
# #     tc, bc = {}, {}
# #     for ct in state.containers:
# #         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
# #         for r in range(ct.rows):
# #             for c in range(ct.cols):
# #                 t = ct.target[r][c]
# #                 if t is not None: tc[t] = tc.get(t, 0) + 1
# #                 b = ct.cells[r][c]
# #                 if b is not None: bc[b] = bc.get(b, 0) + 1
# #     return tc, bc
# #
# #
# # def get_current_spawn_config():
# #     config = {}
# #     for row in state.ratio_ui_rows:
# #         try:
# #             s_txt = row['size'].lower()
# #             w = int(row['weight'])
# #             l = int(row.get('limit', '4'))
# #             if 'x' in s_txt:
# #                 r, c = map(int, s_txt.split('x'))
# #                 if r > 0 and c > 0 and w > 0:
# #                     config[(r, c)] = {'weight': w, 'limit': l}
# #         except:
# #             continue
# #     if not config: return {(2, 2): {'weight': 100, 'limit': 2}}
# #     return config
# #
# #
# # # ============================================================
# # # CONTAINER CLASS
# # # ============================================================
# # class Container:
# #     def __init__(self, layer, rows=None, cols=None):
# #         if rows is None:
# #             # Spawn Random dựa trên Ratio Table
# #             cfg = get_current_spawn_config()
# #             k = random.choices(list(cfg.keys()), weights=[v['weight'] for v in cfg.values()])[0]
# #             self.rows, self.cols = k
# #             self.max_types = cfg[k]['limit']  # Lấy limit màu cho khay này
# #         else:
# #             # Spawn thủ công (Space bar khi chưa chọn gì hoặc logic khác)
# #             self.rows, self.cols = rows, cols
# #             self.max_types = 4  # Default fallback
# #
# #         self.cells = []
# #         self.target = generate_cluster_pattern(self.rows, self.cols, self.max_types)
# #         self.x, self.y, self.layer = 0, 0, layer
# #
# #     def draw_target(self, s):
# #         pygame.draw.rect(s, (255, 255, 255),
# #                          (self.x - 5, self.y - 5, self.cols * CELL_SIZE + 10, self.rows * CELL_SIZE + 10), 2)
# #         for r in range(self.rows):
# #             for c in range(self.cols):
# #                 col = self.target[r][c]
# #                 rgb = COLORS[col] if col is not None and 0 <= col < len(COLORS) else (50, 50, 50)
# #                 pygame.draw.rect(s, rgb, (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
# #                 pygame.draw.rect(s, (200, 200, 200),
# #                                  (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
# #
# #     def draw_block(self, s):
# #         if not self.cells: return
# #         ox = self.x + self.cols * CELL_SIZE + 20
# #         oy = self.y
# #         for r in range(self.rows):
# #             for c in range(self.cols):
# #                 col = self.cells[r][c]
# #                 if col is not None and 0 <= col < len(COLORS):
# #                     pygame.draw.rect(s, COLORS[col], (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
# #                     pygame.draw.rect(s, (0, 0, 0), (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
# #
# #
# # # ============================================================
# # # ALGORITHMS (PATTERN & FILL)
# # # ============================================================
# # def get_partitions_for_size(total, max_same):
# #     patterns = []
# #     if total == 4:
# #         patterns = [[2, 2], [4]]
# #     elif total == 6:
# #         patterns = [[3, 3], [2, 2, 2], [4, 2]]
# #     elif total == 8:
# #         patterns = [[4, 4], [4, 2, 2], [3, 3, 2], [2, 2, 2, 2]]
# #     elif total == 9:
# #         patterns = [[3, 3, 3], [5, 4]]
# #     elif total == 10:
# #         patterns = [[5, 5], [4, 4, 2], [3, 3, 2, 2]]
# #     else:
# #         p = [];
# #         rem = total
# #         while rem > 0: take = min(rem, max_same); p.append(take); rem -= take
# #         patterns = [p]
# #     valid = [p for p in patterns if all(x <= max_same for x in p)]
# #     return valid[0] if valid else []
# #
# #
# def find_bfs_slots(rows, cols, mask, count):
#     coords = [(r, c) for r in range(rows) for c in range(cols)]
#     random.shuffle(coords)
#     start = next((p for p in coords if p not in mask), None)
#     if not start: return []
#     cluster, q, visited = [], [start], {start}
#     while len(cluster) < count and q:
#         curr = q.pop(0);
#         cluster.append(curr);
#         r, c = curr
#         nbs = [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)];
#         random.shuffle(nbs)
#         for nr, nc in nbs:
#             if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in mask and (nr, nc) not in visited:
#                 if len(cluster) + len(q) < count: visited.add((nr, nc)); q.append((nr, nc))
#     return cluster
#
# #
# # def generate_cluster_pattern(rows, cols, max_types):
# #     total = rows * cols
# #     cells = [None] * total
# #
# #     limit = min(state.tray_color_variety, len(COLORS))
# #     pool = list(range(limit))
# #     limit_local = min(max_types, len(pool))
# #     if limit_local < 1: limit_local = 1
# #     allowed = random.sample(pool, limit_local)
# #
# #     pattern = get_partitions_for_size(total, state.max_same_color)
# #     tc, _ = global_stats()
# #     mask = set()
# #
# #     # Helper to choose color
# #     def choose(cnts, size, opts):
# #         sub = {k: cnts.get(k, 0) for k in opts}
# #         m = min(sub.values()) if sub else 0
# #         valid = [k for k, v in sub.items() if v <= m + 1]
# #         return random.choice(valid) if valid else random.choice(opts)
# #
# #     if isinstance(pattern, list):
# #         for size in pattern:
# #             col = choose(tc, size, allowed)
# #             tc[col] = tc.get(col, 0) + size
# #             slots = find_bfs_slots(rows, cols, mask, size)
# #             for r, c in slots: cells[r * cols + c] = col; mask.add((r, c))
# #
# #     for i in range(total):
# #         if cells[i] is None: cells[i] = random.choice(allowed)
# #     return [[cells[i * cols + j] for j in range(cols)] for i in range(rows)]
# #
# #
# # # --- MAIN FILL LOGIC (UPDATED FOR LOCAL LIMIT) ---
# # def find_best_slot_for_clustering(target_trays, color):
# #     """
# #     Tìm vị trí tốt nhất để điền 'color' vào.
# #     Ràng buộc:
# #     1. Max Same Color (Toàn cục).
# #     2. Max Variety Limit (Cục bộ từng khay).
# #     3. Mismatch (Màu Block != Màu Target).
# #     """
# #     candidates_adj = []
# #     candidates_free = []
# #
# #     for ct in target_trays:
# #         # Ensure data
# #         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
# #
# #         # 1. Phân tích các block hiện có trong khay này
# #         current_blocks = [x for row in ct.cells for x in row if x is not None]
# #
# #         # Check Global Constraint: Số lượng block cùng màu
# #         if current_blocks.count(color) >= state.max_same_color:
# #             continue
# #
# #             # Check Local Constraint: Số loại màu (Variety Limit của khay)
# #         unique_colors = set(current_blocks)
# #         # Nếu màu định điền là màu MỚI (chưa có trong khay) VÀ khay đã ĐỦ số loại màu -> Skip
# #         if color not in unique_colors and len(unique_colors) >= ct.max_types:
# #             continue
# #
# #         # 2. Duyệt từng ô trong khay
# #         for r in range(ct.rows):
# #             for c in range(ct.cols):
# #                 # Chỉ điền vào ô trống
# #                 if ct.cells[r][c] is None:
# #                     # Check Mismatch Rule: Màu điền vào KHÔNG ĐƯỢC trùng màu Target
# #                     if ct.target[r][c] == color:
# #                         continue
# #
# #                         # Check Adjacency (Rắn săn mồi - Gom nhóm)
# #                     has_adj = False
# #                     for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
# #                         nr, nc = r + dr, c + dc
# #                         if 0 <= nr < ct.rows and 0 <= nc < ct.cols and ct.cells[nr][nc] == color:
# #                             has_adj = True
# #                             break
# #
# #                     if has_adj:
# #                         candidates_adj.append((ct, r, c))
# #                     else:
# #                         candidates_free.append((ct, r, c))
# #
# #     # Ưu tiên ô có hàng xóm cùng màu
# #     if candidates_adj: return random.choice(candidates_adj)
# #     if candidates_free: return random.choice(candidates_free)
# #     return None
# #
# #
# # def fill_clustered_logic(trays, demand):
# #     filled = 0
# #     # Fill màu có nhu cầu cao trước để dễ gom nhóm
# #     for col, cnt in sorted(demand.items(), key=lambda x: x[1], reverse=True):
# #         for _ in range(cnt):
# #             slot = find_best_slot_for_clustering(trays, col)
# #             if slot:
# #                 slot[0].cells[slot[1]][slot[2]] = col
# #                 filled += 1
# #             else:
# #                 # Không còn chỗ nào hợp lệ cho màu này
# #                 break
# #     state.last_action_message = f"Filled: {filled}" if filled > 0 else "Fill Failed (Limits)"
# #
# #
# # def fill_n(n):
# #     if not state.selected_trays: return
# #     tc, bc = global_stats()
# #     limit = min(state.tray_color_variety, len(COLORS))
# #
# #     # Chỉ chọn màu còn thiếu so với target
# #     valid = [c for c in range(limit) if tc.get(c, 0) - bc.get(c, 0) >= n]
# #
# #     if valid:
# #         col_to_fill = random.choice(valid)
# #         fill_clustered_logic([state.selected_trays[0]], {col_to_fill: n})
# #
# #
# # def auto_fill_mismatch(trays):
# #     # Xác định tập màu cần thiết dựa trên Target của các khay được chọn
# #     pool = set()
# #     for ct in trays:
# #         for r in ct.target:
# #             for c in r: pool.add(c)
# #
# #     tc, bc = global_stats()
# #     limit = min(state.tray_color_variety, len(COLORS))
# #     demand = {}
# #
# #     for c in pool:
# #         if c < limit:
# #             need = tc.get(c, 0) - bc.get(c, 0)
# #             if need > 0: demand[c] = need
# #
# #     fill_clustered_logic(trays, demand)
# #
# #
# # def fill_layers():
# #     tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
# #     if not tls: tls = [state.current_layer]
# #     targets = [c for c in state.containers if c.layer in tls]
# #     if not targets: return
# #
# #     l_tc = {}
# #     for c in targets:
# #         for row in c.target:
# #             for val in row: l_tc[val] = l_tc.get(val, 0) + 1
# #
# #     tc, bc = global_stats()
# #     demand = {}
# #     limit = min(state.tray_color_variety, len(COLORS))
# #     for c, amt in l_tc.items():
# #         if c < limit:
# #             room = tc.get(c, 0) - bc.get(c, 0)
# #             if room > 0: demand[c] = min(amt, room)
# #     fill_clustered_logic(targets, demand)
# #
# #
# # def fill_same():
# #     tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
# #     targets = [c for c in state.containers if c.layer in tls] if tls else state.selected_trays
# #     if not targets: return
# #
# #     cnt = 0
# #     for ct in targets:
# #         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
# #
# #         # Kiểm tra màu hiện có
# #         types = set(x for row in ct.cells for x in row if x is not None)
# #
# #         for r in range(ct.rows):
# #             for c in range(ct.cols):
# #                 if ct.cells[r][c] is None:
# #                     t = ct.target[r][c]
# #
# #                     # Apply Limit Check for Fill Same too
# #                     if t in types or len(types) < ct.max_types:
# #                         ct.cells[r][c] = t
# #                         types.add(t)
# #                         cnt += 1
# #
# #     state.last_action_message = f"Filled Same: {cnt}"
# #
# #
# # def shuffle_level():
# #     targets = state.selected_trays if state.selected_trays else state.containers
# #     slots = []
# #     for ct in targets:
# #         if not ct.cells: continue
# #         for r in range(ct.rows):
# #             for c in range(ct.cols):
# #                 if ct.cells[r][c] is not None: slots.append({'ct': ct, 'r': r, 'c': c})
# #
# #     if len(slots) < 2: return
# #     random.shuffle(slots)
# #     cnt = 0
# #
# #     for a in slots:
# #         diff = random.randint(0, 100) < state.shuffle_ratio
# #         cands = []
# #         for b in slots:
# #             # Skip self
# #             if a['ct'] == b['ct'] and a['r'] == b['r'] and a['c'] == b['c']: continue
# #             # Check layer ratio
# #             if (a['ct'].layer != b['ct'].layer) != diff: continue
# #
# #             # Check Mismatch Rule
# #             val_a = a['ct'].cells[a['r']][a['c']]
# #             val_b = b['ct'].cells[b['r']][b['c']]
# #             tgt_a = a['ct'].target[a['r']][a['c']]
# #             tgt_b = b['ct'].target[b['r']][b['c']]
# #
# #             if val_a != tgt_b and val_b != tgt_a:
# #                 cands.append(b)
# #
# #         if cands:
# #             b = random.choice(cands)
# #             v1, v2 = a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']]
# #             a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']] = v2, v1
# #             cnt += 1
# #
# #     state.last_action_message = f"Shuffled: {cnt}"
# #
# #
# # # --- SYSTEM ---
# # def layout(arr):
# #     vis = [c for c in arr if c.layer == state.current_layer]
# #     cy = MARGIN_Y
# #     for i in range(0, len(vis), MAX_PER_ROW):
# #         row = vis[i:i + MAX_PER_ROW]
# #         h = max(c.rows for c in row) * CELL_SIZE
# #         for idx, c in enumerate(row):
# #             c.x = MARGIN_X + idx * SLOT_W
# #             c.y = cy
# #         cy += h + 80
# #
# # def save_undo():
# #     snap = []
# #     for ct in state.containers:
# #         new_ct = Container(ct.layer, rows=ct.rows, cols=ct.cols)
# #         new_ct.max_types = ct.max_types
# #         new_ct.x, new_ct.y = ct.x, ct.y
# #         new_ct.cells = [row[:] for row in ct.cells] if ct.cells else None
# #         new_ct.target = [row[:] for row in ct.target] if ct.target else None
# #         snap.append(new_ct)
# #     state.undo_stack.append(snap)
# #     if len(state.undo_stack) > 20: state.undo_stack.pop(0)
# #
# # def undo():
# #     if not state.undo_stack: return
# #     state.containers = state.undo_stack.pop()
# #     state.selected_trays = []
# #     state.selected_cells = []
# #     layout(state.containers)
# #     state.last_action_message = "Undo"
#
#
# import random
# import pygame
# from config import *
#
#
# # ============================================================
# # STATS & UTILS
# # ============================================================
# def global_stats():
#     tc, bc = {}, {}
#     for ct in state.containers:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 t = ct.target[r][c]
#                 if t is not None: tc[t] = tc.get(t, 0) + 1
#                 b = ct.cells[r][c]
#                 if b is not None: bc[b] = bc.get(b, 0) + 1
#     return tc, bc
#
#
# def get_current_spawn_config():
#     config = {}
#     for row in state.ratio_ui_rows:
#         try:
#             s_txt = row['size'].lower()
#             w = int(row['weight'])
#             l = int(row.get('limit', '4'))
#             if 'x' in s_txt:
#                 r, c = map(int, s_txt.split('x'))
#                 if r > 0 and c > 0 and w > 0:
#                     config[(r, c)] = {'weight': w, 'limit': l}
#         except:
#             continue
#     if not config: return {(2, 2): {'weight': 100, 'limit': 2}}
#     return config
#
#
# # ============================================================
# # CONTAINER CLASS
# # ============================================================
# class Container:
#     def __init__(self, layer, rows=None, cols=None):
#         if rows is None:
#             cfg = get_current_spawn_config()
#             k = random.choices(list(cfg.keys()), weights=[v['weight'] for v in cfg.values()])[0]
#             self.rows, self.cols = k
#             self.max_types = cfg[k]['limit']
#         else:
#             self.rows, self.cols = rows, cols
#             self.max_types = 4
#
#         self.cells = []
#         self.target = generate_cluster_pattern(self.rows, self.cols, self.max_types)
#         self.x, self.y, self.layer = 0, 0, layer
#
#     def draw_target(self, s):
#         pygame.draw.rect(s, (255, 255, 255),
#                          (self.x - 5, self.y - 5, self.cols * CELL_SIZE + 10, self.rows * CELL_SIZE + 10), 2)
#         for r in range(self.rows):
#             for c in range(self.cols):
#                 col = self.target[r][c]
#                 rgb = COLORS[col] if col is not None and 0 <= col < len(COLORS) else (50, 50, 50)
#                 pygame.draw.rect(s, rgb, (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
#                 pygame.draw.rect(s, (200, 200, 200),
#                                  (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
#
#     def draw_block(self, s):
#         if not self.cells: return
#         ox = self.x + self.cols * CELL_SIZE + 20
#         oy = self.y
#         for r in range(self.rows):
#             for c in range(self.cols):
#                 col = self.cells[r][c]
#                 if col is not None and 0 <= col < len(COLORS):
#                     pygame.draw.rect(s, COLORS[col], (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
#                     pygame.draw.rect(s, (0, 0, 0), (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
#
#
# # ============================================================
# # ALGORITHMS (PATTERN & FILL) - NEW LOGIC
# # ============================================================
# def get_partitions_for_size(total, max_same):
#     # Logic chia cụm: Ưu tiên cụm to để dễ xếp đẹp
#     patterns = []
#     if total == 4:
#         patterns = [[2, 2], [4]]
#     elif total == 6:
#         patterns = [[3, 3], [4, 2], [2, 2, 2]]
#     elif total == 8:
#         patterns = [[4, 4], [5, 3], [6, 2], [4, 2, 2]]
#     elif total == 9:
#         patterns = [[5, 4], [3, 3, 3], [6, 3]]
#     elif total == 10:
#         patterns = [[5, 5], [6, 4], [4, 4, 2], [8, 2]]
#     else:
#         p = [];
#         rem = total
#         while rem > 0: take = min(rem, max_same); p.append(take); rem -= take
#         patterns = [p]
#     valid = [p for p in patterns if all(x <= max_same for x in p)]
#     if not valid:
#         # Fallback
#         p = [];
#         rem = total
#         while rem > 0: take = min(rem, max_same); p.append(take); rem -= take
#         valid = [p]
#
#     # Sort pattern: Số lớn trước (để xử lý cụm to trước), số nhỏ sau (xử lý màu lẻ sau)
#     chosen = random.choice(valid)
#     chosen.sort(reverse=True)
#     return chosen
#
#
# def find_compact_cluster(rows, cols, mask, count):
#     """
#     Tìm vị trí cho cụm màu sao cho 'Compact' nhất (vuông vức nhất).
#     Nếu là cụm nhỏ (1-2 ô), ưu tiên đẩy về góc.
#     """
#     all_cells = [(r, c) for r in range(rows) for c in range(cols)]
#
#     # Xác định chiến thuật dựa trên kích thước cụm
#     is_small_cluster = (count <= 2)
#
#     # Nếu là cụm nhỏ, ưu tiên tìm ở các góc trước
#     # Thứ tự ưu tiên góc: Dưới-Phải -> Trên-Trái -> ...
#     corners = [(rows - 1, cols - 1), (0, 0), (0, cols - 1), (rows - 1, 0)]
#
#     search_order = []
#     if is_small_cluster:
#         # Tìm góc trống
#         for c in corners:
#             if c not in mask: search_order.append(c)
#         # Sau đó mới đến các ô khác
#         others = [p for p in all_cells if p not in mask and p not in corners]
#         # Sort others để ưu tiên các ô biên (gần lề)
#         others.sort(key=lambda p: -min(p[0], p[1], rows - 1 - p[0], cols - 1 - p[1]))  # Đẩy ra biên
#         search_order.extend(others)
#     else:
#         # Cụm to: Quét từ trên xuống, trái sang (để lấp đầy tuần tự)
#         search_order = [p for p in all_cells if p not in mask]
#
#     best_cluster = []
#     best_score = -1  # Điểm compactness càng cao càng tốt
#
#     # Thử bắt đầu loang từ mỗi vị trí khả dĩ
#     # Để tối ưu perf, chỉ thử N vị trí đầu tiên tìm thấy
#     trials = 0
#     max_trials = 10 if is_small_cluster else 20
#
#     for start_node in search_order:
#         if start_node in mask: continue
#
#         # BFS để tìm cụm
#         cluster = []
#         queue = [start_node]
#         visited_local = {start_node}
#
#         while len(cluster) < count and queue:
#             # Cải tiến BFS: Chọn node tiếp theo sao cho nó gần start_node nhất (giữ cụm đặc)
#             # Sort queue by distance to start_node
#             queue.sort(key=lambda p: abs(p[0] - start_node[0]) + abs(p[1] - start_node[1]))
#
#             curr = queue.pop(0)
#             cluster.append(curr)
#
#             r, c = curr
#             # Hàng xóm
#             nbs = [(r + 1, c), (r, c + 1), (r - 1, c), (r, c - 1)]
#             # Ưu tiên hàng xóm theo hướng điền tự nhiên (Phải, Dưới)
#
#             for nr, nc in nbs:
#                 if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in mask and (nr, nc) not in visited_local:
#                     if len(cluster) + len(queue) < count:
#                         visited_local.add((nr, nc))
#                         queue.append((nr, nc))
#
#         if len(cluster) == count:
#             # Đánh giá cụm này
#             # Tiêu chí 1: Số cạnh chung (càng nhiều cạnh chung càng đặc)
#             adjacency_score = 0
#             for i in range(len(cluster)):
#                 for j in range(i + 1, len(cluster)):
#                     r1, c1 = cluster[i]
#                     r2, c2 = cluster[j]
#                     if abs(r1 - r2) + abs(c1 - c2) == 1: adjacency_score += 1
#
#             # Tiêu chí 2: Phạt nếu nằm giữa (cho cụm nhỏ)
#             position_score = 0
#             if is_small_cluster:
#                 # Càng gần góc càng tốt
#                 dist_corner = min(abs(r - cr) + abs(c - cc) for r, c in cluster for cr, cc in corners)
#                 position_score = -dist_corner  # Gần góc -> dist nhỏ -> score âm ít (tốt)
#
#             total_score = adjacency_score * 10 + position_score
#
#             if total_score > best_score:
#                 best_score = total_score
#                 best_cluster = cluster
#
#             trials += 1
#             if trials >= max_trials: break  # Tìm tạm đủ rồi
#
#     return best_cluster
#
#
# def generate_cluster_pattern(rows, cols, max_types):
#     total = rows * cols
#     cells = [None] * total
#
#     limit = min(state.tray_color_variety, len(COLORS))
#     pool = list(range(limit))
#     limit_local = min(max_types, len(pool))
#     if limit_local < 1: limit_local = 1
#     allowed = random.sample(pool, limit_local)
#
#     pattern = get_partitions_for_size(total, state.max_same_color)
#     tc, _ = global_stats()
#     mask = set()
#
#     # Helper to choose color
#     def choose(cnts, size, opts):
#         sub = {k: cnts.get(k, 0) for k in opts}
#         m = min(sub.values()) if sub else 0
#         valid = [k for k, v in sub.items() if v <= m + 1]
#         return random.choice(valid) if valid else random.choice(opts)
#
#     if isinstance(pattern, list):
#         # Pattern đã được sort giảm dần (cụm to xử lý trước, cụm nhỏ xử lý sau)
#         for size in pattern:
#             col = choose(tc, size, allowed)
#             tc[col] = tc.get(col, 0) + size
#
#             # Dùng thuật toán Compact/Corner Push
#             slots = find_compact_cluster(rows, cols, mask, size)
#
#             # Fallback nếu thuật toán xịn fail (hiếm gặp) -> Dùng BFS thường
#             if not slots:
#                 slots = find_bfs_slots(rows, cols, mask, size)
#
#             for r, c in slots:
#                 cells[r * cols + c] = col
#                 mask.add((r, c))
#
#     for i in range(total):
#         if cells[i] is None: cells[i] = random.choice(allowed)
#     return [[cells[i * cols + j] for j in range(cols)] for i in range(rows)]
#
#
# # --- MAIN FILL LOGIC (UPDATED FOR LOCAL LIMIT) ---
# def find_best_slot_for_clustering(target_trays, color):
#     candidates_adj = []
#     candidates_free = []
#
#     for ct in target_trays:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#
#         current_blocks = [x for row in ct.cells for x in row if x is not None]
#
#         if current_blocks.count(color) >= state.max_same_color: continue
#         unique_colors = set(current_blocks)
#         if color not in unique_colors and len(unique_colors) >= ct.max_types: continue
#
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is None:
#                     if ct.target[r][c] == color: continue
#
#                     # Check Adjacency
#                     has_adj = False
#                     for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
#                         nr, nc = r + dr, c + dc
#                         if 0 <= nr < ct.rows and 0 <= nc < ct.cols and ct.cells[nr][nc] == color:
#                             has_adj = True;
#                             break
#
#                     if has_adj:
#                         candidates_adj.append((ct, r, c))
#                     else:
#                         candidates_free.append((ct, r, c))
#
#     if candidates_adj: return random.choice(candidates_adj)
#     if candidates_free: return random.choice(candidates_free)
#     return None
#
#
# def fill_clustered_logic(trays, demand):
#     filled = 0
#     for col, cnt in sorted(demand.items(), key=lambda x: x[1], reverse=True):
#         for _ in range(cnt):
#             slot = find_best_slot_for_clustering(trays, col)
#             if slot:
#                 slot[0].cells[slot[1]][slot[2]] = col
#                 filled += 1
#             else:
#                 break
#     state.last_action_message = f"Filled: {filled}" if filled > 0 else "Fill Failed (Limits)"
#
#
# def fill_n(n):
#     if not state.selected_trays: return
#     tc, bc = global_stats()
#     limit = min(state.tray_color_variety, len(COLORS))
#     valid = [c for c in range(limit) if tc.get(c, 0) - bc.get(c, 0) >= n]
#     if valid:
#         col_to_fill = random.choice(valid)
#         fill_clustered_logic([state.selected_trays[0]], {col_to_fill: n})
#
#
# def auto_fill_mismatch(trays):
#     pool = set()
#     for ct in trays:
#         for r in ct.target:
#             for c in r: pool.add(c)
#     tc, bc = global_stats()
#     limit = min(state.tray_color_variety, len(COLORS))
#     demand = {}
#     for c in pool:
#         if c < limit:
#             need = tc.get(c, 0) - bc.get(c, 0)
#             if need > 0: demand[c] = need
#     fill_clustered_logic(trays, demand)
#
#
# def fill_layers():
#     tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
#     if not tls: tls = [state.current_layer]
#     targets = [c for c in state.containers if c.layer in tls]
#     if not targets: return
#     l_tc = {}
#     for c in targets:
#         for row in c.target:
#             for val in row: l_tc[val] = l_tc.get(val, 0) + 1
#     tc, bc = global_stats()
#     demand = {}
#     limit = min(state.tray_color_variety, len(COLORS))
#     for c, amt in l_tc.items():
#         if c < limit:
#             room = tc.get(c, 0) - bc.get(c, 0)
#             if room > 0: demand[c] = min(amt, room)
#     fill_clustered_logic(targets, demand)
#
#
# def fill_same():
#     tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
#     targets = [c for c in state.containers if c.layer in tls] if tls else state.selected_trays
#     if not targets: return
#     cnt = 0
#     for ct in targets:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         types = set(x for row in ct.cells for x in row if x is not None)
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is None:
#                     t = ct.target[r][c]
#                     if t in types or len(types) < ct.max_types:
#                         ct.cells[r][c] = t;
#                         types.add(t);
#                         cnt += 1
#     state.last_action_message = f"Filled Same: {cnt}"
#
#
# def shuffle_level():
#     targets = state.selected_trays if state.selected_trays else state.containers
#     slots = []
#     for ct in targets:
#         if not ct.cells: continue
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is not None: slots.append({'ct': ct, 'r': r, 'c': c})
#     if len(slots) < 2: return
#     random.shuffle(slots)
#     cnt = 0
#     for a in slots:
#         diff = random.randint(0, 100) < state.shuffle_ratio
#         cands = []
#         for b in slots:
#             if a['ct'] == b['ct'] and a['r'] == b['r'] and a['c'] == b['c']: continue
#             if (a['ct'].layer != b['ct'].layer) != diff: continue
#             val_a = a['ct'].cells[a['r']][a['c']]
#             val_b = b['ct'].cells[b['r']][b['c']]
#             tgt_a = a['ct'].target[a['r']][a['c']]
#             tgt_b = b['ct'].target[b['r']][b['c']]
#             if val_a != tgt_b and val_b != tgt_a: cands.append(b)
#         if cands:
#             b = random.choice(cands)
#             v1, v2 = a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']]
#             a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']] = v2, v1
#             cnt += 1
#     state.last_action_message = f"Shuffled: {cnt}"
#
#
# # --- SYSTEM (RESTORED) ---
# def layout(arr):
#     vis = [c for c in arr if c.layer == state.current_layer]
#     cy = MARGIN_Y
#     for i in range(0, len(vis), MAX_PER_ROW):
#         row = vis[i:i + MAX_PER_ROW]
#         h = max(c.rows for c in row) * CELL_SIZE
#         for idx, c in enumerate(row):
#             c.x = MARGIN_X + idx * SLOT_W
#             c.y = cy
#         cy += h + 80
#
#
# def save_undo():
#     snap = []
#     for ct in state.containers:
#         new_ct = Container(ct.layer, rows=ct.rows, cols=ct.cols)
#         new_ct.max_types = ct.max_types
#         new_ct.x, new_ct.y = ct.x, ct.y
#         new_ct.cells = [row[:] for row in ct.cells] if ct.cells else None
#         new_ct.target = [row[:] for row in ct.target] if ct.target else None
#         snap.append(new_ct)
#     state.undo_stack.append(snap)
#     if len(state.undo_stack) > 20: state.undo_stack.pop(0)
#
#
# def undo():
#     if not state.undo_stack: return
#     state.containers = state.undo_stack.pop()
#     state.selected_trays = []
#     state.selected_cells = []
#     layout(state.containers)
#     state.last_action_message = "Undo"


###########ver1###########

# import random
# import pygame
# from config import *
#
#
# # ============================================================
# # STATS & UTILS
# # ============================================================
# def global_stats():
#     tc, bc = {}, {}
#     for ct in state.containers:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 t = ct.target[r][c]
#                 if t is not None: tc[t] = tc.get(t, 0) + 1
#                 b = ct.cells[r][c]
#                 if b is not None: bc[b] = bc.get(b, 0) + 1
#     return tc, bc
#
#
# def get_current_spawn_config():
#     config = {}
#     for row in state.ratio_ui_rows:
#         try:
#             s_txt = row['size'].lower()
#             w = int(row['weight'])
#             l = int(row.get('limit', '4'))
#             if 'x' in s_txt:
#                 r, c = map(int, s_txt.split('x'))
#                 if r > 0 and c > 0 and w > 0:
#                     config[(r, c)] = {'weight': w, 'limit': l}
#         except:
#             continue
#     if not config: return {(2, 2): {'weight': 100, 'limit': 2}}
#     return config
#
#
# # ============================================================
# # CONTAINER CLASS
# # ============================================================
# class Container:
#     def __init__(self, layer, rows=None, cols=None, manual_target=None):
#         # manual_target: Dùng cho spawn đối xứng (copy pattern)
#         if rows is None:
#             cfg = get_current_spawn_config()
#             k = random.choices(list(cfg.keys()), weights=[v['weight'] for v in cfg.values()])[0]
#             self.rows, self.cols = k
#             self.max_types = cfg[k]['limit']
#         else:
#             self.rows, self.cols = rows, cols
#             self.max_types = 4
#
#         self.cells = []  # Block colors (Cube)
#
#         if manual_target:
#             self.target = manual_target
#         else:
#             self.target = generate_cluster_pattern(self.rows, self.cols, self.max_types)
#
#         self.x, self.y, self.layer = 0, 0, layer
#
#     def draw_target(self, s):
#         pygame.draw.rect(s, (255, 255, 255),
#                          (self.x - 5, self.y - 5, self.cols * CELL_SIZE + 10, self.rows * CELL_SIZE + 10), 2)
#         for r in range(self.rows):
#             for c in range(self.cols):
#                 col = self.target[r][c]
#                 rgb = COLORS[col] if col is not None and 0 <= col < len(COLORS) else (50, 50, 50)
#                 pygame.draw.rect(s, rgb, (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
#                 pygame.draw.rect(s, (200, 200, 200),
#                                  (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
#
#     def draw_block(self, s):
#         if not self.cells: return
#         ox = self.x + self.cols * CELL_SIZE + 20
#         oy = self.y
#         for r in range(self.rows):
#             for c in range(self.cols):
#                 col = self.cells[r][c]
#                 if col is not None and 0 <= col < len(COLORS):
#                     pygame.draw.rect(s, COLORS[col], (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
#                     pygame.draw.rect(s, (0, 0, 0), (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
#
#
# # ============================================================
# # ALGORITHMS: DIRECTIONAL GENERATION & SORT
# # ============================================================
#
# def get_directional_slots(rows, cols):
#     """
#     Trả về danh sách tọa độ (r,c) được sắp xếp theo chiều 'ngắn' nhất.
#     - Nếu Rows < Cols (vd 2x3): Quét dọc (Hàng dọc trước).
#     - Nếu Rows >= Cols (vd 3x2): Quét ngang (Hàng ngang trước).
#     """
#     slots = []
#     if rows < cols:
#         # Fill theo cột (Column-major order) -> Tạo sọc dọc
#         for c in range(cols):
#             for r in range(rows):
#                 slots.append((r, c))
#     else:
#         # Fill theo hàng (Row-major order) -> Tạo sọc ngang
#         for r in range(rows):
#             for c in range(cols):
#                 slots.append((r, c))
#     return slots
#
#
# def get_partitions_for_size(total, max_same):
#     # Logic chia cụm
#     patterns = []
#     if total == 4:
#         patterns = [[2, 2], [4]]
#     elif total == 6:
#         patterns = [[3, 3], [4, 2], [2, 2, 2]]
#     elif total == 8:
#         patterns = [[4, 4], [5, 3], [6, 2], [4, 2, 2]]
#     elif total == 9:
#         patterns = [[5, 4], [3, 3, 3], [6, 3]]
#     elif total == 10:
#         patterns = [[5, 5], [6, 4], [4, 4, 2], [8, 2]]
#     else:
#         p = [];
#         rem = total
#         while rem > 0: take = min(rem, max_same); p.append(take); rem -= take
#         patterns = [p]
#
#     valid = [p for p in patterns if all(x <= max_same for x in p)]
#     if not valid:
#         p = [];
#         rem = total
#         while rem > 0: take = min(rem, max_same); p.append(take); rem -= take
#         valid = [p]
#
#     chosen = random.choice(valid)
#     chosen.sort(reverse=True)
#     return chosen
#
#
# def generate_cluster_pattern(rows, cols, max_types):
#     total = rows * cols
#     cells = [None] * total
#
#     # 1. Setup Colors
#     limit = min(state.tray_color_variety, len(COLORS))
#     pool = list(range(limit))
#     limit_local = min(max_types, len(pool))
#     if limit_local < 1: limit_local = 1
#     allowed = random.sample(pool, limit_local)
#
#     pattern = get_partitions_for_size(total, state.max_same_color)
#     tc, _ = global_stats()
#
#     # Helper choose
#     def choose(cnts, size, opts):
#         sub = {k: cnts.get(k, 0) for k in opts}
#         m = min(sub.values()) if sub else 0
#         valid = [k for k, v in sub.items() if v <= m + 1]
#         return random.choice(valid) if valid else random.choice(opts)
#
#     # 2. Get Sorted Slots (New Logic)
#     # Lấy danh sách vị trí đã sắp xếp theo chiều ưu tiên
#     sorted_slots = get_directional_slots(rows, cols)
#
#     current_slot_idx = 0
#
#     # 3. Fill Sequentially
#     if isinstance(pattern, list):
#         for size in pattern:
#             col = choose(tc, size, allowed)
#             tc[col] = tc.get(col, 0) + size
#
#             # Điền màu này vào N vị trí tiếp theo trong danh sách đã sort
#             for _ in range(size):
#                 if current_slot_idx < total:
#                     r, c = sorted_slots[current_slot_idx]
#                     cells[r * cols + c] = col
#                     current_slot_idx += 1
#
#     # Fallback
#     for i in range(total):
#         if cells[i] is None: cells[i] = random.choice(allowed)
#
#     return [[cells[i * cols + j] for j in range(cols)] for i in range(rows)]
#
#
# # --- SORT LOGIC ---
# def sort_selected_trays(trays_to_sort):
#     # Nếu danh sách trống, kiểm tra checkbox layer
#     if not trays_to_sort:
#         target_layers = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
#         if target_layers:
#             trays_to_sort = [ct for ct in state.containers if ct.layer in target_layers]
#         else:
#             # Nếu không check layer nào -> Sort ALL
#             trays_to_sort = state.containers
#
#     if not trays_to_sort:
#         state.last_action_message = "Nothing to sort"
#         return
#
#     count = 0
#     for ct in trays_to_sort:
#         if not ct.cells: continue
#
#         # 1. Collect existing blocks
#         blocks = []
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is not None:
#                     blocks.append(ct.cells[r][c])
#
#         if not blocks: continue
#
#         # 2. Sort blocks by frequency
#         freq = {x: blocks.count(x) for x in set(blocks)}
#         blocks.sort(key=lambda x: (-freq[x], x))
#
#         # 3. Refill using Directional Logic
#         sorted_slots = get_directional_slots(ct.rows, ct.cols)
#
#         # Clear old cells
#         ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#
#         # Place sorted blocks
#         for i, val in enumerate(blocks):
#             if i < len(sorted_slots):
#                 r, c = sorted_slots[i]
#                 ct.cells[r][c] = val
#
#         count += 1
#     state.last_action_message = f"Sorted {count} trays"
#
#
# # --- SYMMETRY SPAWN LOGIC ---
# def spawn_new_trays():
#     # 1. Create Tray 1 (Master)
#     master = Container(state.current_layer)
#     state.containers.append(master)
#
#     # 2. Check Symmetry Mode
#     if state.symmetry_mode:
#         # Clone properties
#         slave_rows, slave_cols = master.rows, master.cols
#
#         # Create Inverted Pattern for Slave
#         # Logic: Find unique colors in Master pattern, map them to other colors
#         unique_colors = sorted(list(set(x for row in master.target for x in row if x is not None)))
#
#         # Rotate Mapping: C1 -> C2, C2 -> C3, ... Cn -> C1
#         color_map = {}
#         if unique_colors:
#             for i in range(len(unique_colors)):
#                 src = unique_colors[i]
#                 dst = unique_colors[(i + 1) % len(unique_colors)]
#                 color_map[src] = dst
#
#         slave_target = [[None] * slave_cols for _ in range(slave_rows)]
#         for r in range(slave_rows):
#             for c in range(slave_cols):
#                 orig = master.target[r][c]
#                 slave_target[r][c] = color_map.get(orig, orig)
#
#         # Create Slave Tray
#         slave = Container(state.current_layer, rows=slave_rows, cols=slave_cols, manual_target=slave_target)
#         state.containers.append(slave)
#         state.last_action_message = "Spawned Symmetric Pair"
#     else:
#         state.last_action_message = "Spawned Single Tray"
#
#
# # --- MAIN FILL LOGIC (UNCHANGED) ---
# def find_best_slot_for_clustering(target_trays, color):
#     candidates_adj, candidates_free = [], []
#     for ct in target_trays:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         current_blocks = [x for row in ct.cells for x in row if x is not None]
#         if current_blocks.count(color) >= state.max_same_color: continue
#         unique_colors = set(current_blocks)
#         if color not in unique_colors and len(unique_colors) >= ct.max_types: continue
#
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is None:
#                     if ct.target[r][c] == color: continue
#                     has_adj = False
#                     for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
#                         nr, nc = r + dr, c + dc
#                         if 0 <= nr < ct.rows and 0 <= nc < ct.cols and ct.cells[nr][nc] == color:
#                             has_adj = True;
#                             break
#                     if has_adj:
#                         candidates_adj.append((ct, r, c))
#                     else:
#                         candidates_free.append((ct, r, c))
#     if candidates_adj: return random.choice(candidates_adj)
#     if candidates_free: return random.choice(candidates_free)
#     return None
#
#
# def fill_clustered_logic(trays, demand):
#     filled = 0
#     for col, cnt in sorted(demand.items(), key=lambda x: x[1], reverse=True):
#         for _ in range(cnt):
#             slot = find_best_slot_for_clustering(trays, col)
#             if slot:
#                 slot[0].cells[slot[1]][slot[2]] = col
#                 filled += 1
#             else:
#                 break
#     state.last_action_message = f"Filled: {filled}" if filled > 0 else "Fill Failed (Limits)"
#
#
# def fill_n(n):
#     if not state.selected_trays: return
#     tc, bc = global_stats()
#     limit = min(state.tray_color_variety, len(COLORS))
#     valid = [c for c in range(limit) if tc.get(c, 0) - bc.get(c, 0) >= n]
#     if valid:
#         col_to_fill = random.choice(valid)
#         fill_clustered_logic([state.selected_trays[0]], {col_to_fill: n})
#
#
# def auto_fill_mismatch(trays):
#     pool = set()
#     for ct in trays:
#         for r in ct.target:
#             for c in r: pool.add(c)
#     tc, bc = global_stats()
#     limit = min(state.tray_color_variety, len(COLORS))
#     demand = {}
#     for c in pool:
#         if c < limit:
#             need = tc.get(c, 0) - bc.get(c, 0)
#             if need > 0: demand[c] = need
#     fill_clustered_logic(trays, demand)
#
#
# def fill_layers():
#     tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
#     if not tls: tls = [state.current_layer]
#     targets = [c for c in state.containers if c.layer in tls]
#     if not targets: return
#     l_tc = {}
#     for c in targets:
#         for row in c.target:
#             for val in row: l_tc[val] = l_tc.get(val, 0) + 1
#     tc, bc = global_stats()
#     demand = {}
#     limit = min(state.tray_color_variety, len(COLORS))
#     for c, amt in l_tc.items():
#         if c < limit:
#             room = tc.get(c, 0) - bc.get(c, 0)
#             if room > 0: demand[c] = min(amt, room)
#     fill_clustered_logic(targets, demand)
#
#
# def fill_same():
#     tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
#     targets = [c for c in state.containers if c.layer in tls] if tls else state.selected_trays
#     if not targets: return
#     cnt = 0
#     for ct in targets:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         types = set(x for row in ct.cells for x in row if x is not None)
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is None:
#                     t = ct.target[r][c]
#                     if t in types or len(types) < ct.max_types:
#                         ct.cells[r][c] = t;
#                         types.add(t);
#                         cnt += 1
#     state.last_action_message = f"Filled Same: {cnt}"
#
#
# def shuffle_level():
#     targets = state.selected_trays if state.selected_trays else state.containers
#     slots = []
#     for ct in targets:
#         if not ct.cells: continue
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is not None: slots.append({'ct': ct, 'r': r, 'c': c})
#     if len(slots) < 2: return
#     random.shuffle(slots)
#     cnt = 0
#     for a in slots:
#         diff = random.randint(0, 100) < state.shuffle_ratio
#         cands = []
#         for b in slots:
#             if a['ct'] == b['ct'] and a['r'] == b['r'] and a['c'] == b['c']: continue
#             if (a['ct'].layer != b['ct'].layer) != diff: continue
#             val_a = a['ct'].cells[a['r']][a['c']]
#             val_b = b['ct'].cells[b['r']][b['c']]
#             tgt_a = a['ct'].target[a['r']][a['c']]
#             tgt_b = b['ct'].target[b['r']][b['c']]
#             if val_a != tgt_b and val_b != tgt_a: cands.append(b)
#         if cands:
#             b = random.choice(cands)
#             v1, v2 = a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']]
#             a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']] = v2, v1
#             cnt += 1
#     state.last_action_message = f"Shuffled: {cnt}"
#
#
# # --- SYSTEM RESTORED ---
# def layout(arr):
#     vis = [c for c in arr if c.layer == state.current_layer]
#     cy = MARGIN_Y
#     for i in range(0, len(vis), MAX_PER_ROW):
#         row = vis[i:i + MAX_PER_ROW]
#         h = max(c.rows for c in row) * CELL_SIZE
#         for idx, c in enumerate(row):
#             c.x = MARGIN_X + idx * SLOT_W
#             c.y = cy
#         cy += h + 80
#
#
# def save_undo():
#     snap = []
#     for ct in state.containers:
#         new_ct = Container(ct.layer, rows=ct.rows, cols=ct.cols)
#         new_ct.max_types = ct.max_types
#         new_ct.x, new_ct.y = ct.x, ct.y
#         new_ct.cells = [row[:] for row in ct.cells] if ct.cells else None
#         new_ct.target = [row[:] for row in ct.target] if ct.target else None
#         snap.append(new_ct)
#     state.undo_stack.append(snap)
#     if len(state.undo_stack) > 20: state.undo_stack.pop(0)
#
#
# def undo():
#     if not state.undo_stack: return
#     state.containers = state.undo_stack.pop()
#     state.selected_trays = []
#     state.selected_cells = []
#     layout(state.containers)
#     state.last_action_message = "Undo"





###########ver2###########


# import random
# import pygame
# from config import *
#
#
# # ============================================================
# # STATS & UTILS
# # ============================================================
# def global_stats():
#     tc, bc = {}, {}
#     for ct in state.containers:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 t = ct.target[r][c]
#                 if t is not None: tc[t] = tc.get(t, 0) + 1
#                 b = ct.cells[r][c]
#                 if b is not None: bc[b] = bc.get(b, 0) + 1
#     return tc, bc
#
#
# def get_current_spawn_config():
#     config = {}
#     for row in state.ratio_ui_rows:
#         try:
#             s_txt = row['size'].lower()
#             w = int(row['weight'])
#             l = int(row.get('limit', '4'))
#             if 'x' in s_txt:
#                 r, c = map(int, s_txt.split('x'))
#                 if r > 0 and c > 0 and w > 0:
#                     config[(r, c)] = {'weight': w, 'limit': l}
#         except:
#             continue
#     if not config: return {(2, 2): {'weight': 100, 'limit': 2}}
#     return config
#
#
# # ============================================================
# # CONTAINER CLASS
# # ============================================================
# class Container:
#     def __init__(self, layer, rows=None, cols=None, manual_target=None):
#         if rows is None:
#             cfg = get_current_spawn_config()
#             k = random.choices(list(cfg.keys()), weights=[v['weight'] for v in cfg.values()])[0]
#             self.rows, self.cols = k
#             self.max_types = cfg[k]['limit']
#         else:
#             self.rows, self.cols = rows, cols
#             self.max_types = 4
#
#         self.cells = []
#
#         if manual_target:
#             self.target = manual_target
#         else:
#             self.target = generate_cluster_pattern(self.rows, self.cols, self.max_types)
#
#         self.x, self.y, self.layer = 0, 0, layer
#
#     def draw_target(self, s):
#         pygame.draw.rect(s, (255, 255, 255),
#                          (self.x - 5, self.y - 5, self.cols * CELL_SIZE + 10, self.rows * CELL_SIZE + 10), 2)
#         for r in range(self.rows):
#             for c in range(self.cols):
#                 col = self.target[r][c]
#                 rgb = COLORS[col] if col is not None and 0 <= col < len(COLORS) else (50, 50, 50)
#                 pygame.draw.rect(s, rgb, (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
#                 pygame.draw.rect(s, (200, 200, 200),
#                                  (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
#
#     def draw_block(self, s):
#         if not self.cells: return
#         ox = self.x + self.cols * CELL_SIZE + 20
#         oy = self.y
#         for r in range(self.rows):
#             for c in range(self.cols):
#                 col = self.cells[r][c]
#                 if col is not None and 0 <= col < len(COLORS):
#                     pygame.draw.rect(s, COLORS[col], (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
#                     pygame.draw.rect(s, (0, 0, 0), (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
#
#
# # ============================================================
# # ALGORITHMS: DIRECTIONAL GENERATION & SORT
# # ============================================================
#
# def get_directional_slots(rows, cols):
#     """
#     Trả về danh sách tọa độ (r,c) ưu tiên điền theo chiều ngắn nhất.
#     """
#     slots = []
#     if rows < cols:
#         # Fill theo cột (Dọc) -> Tạo sọc dọc
#         for c in range(cols):
#             for r in range(rows):
#                 slots.append((r, c))
#     else:
#         # Fill theo hàng (Ngang) -> Tạo sọc ngang
#         for r in range(rows):
#             for c in range(cols):
#                 slots.append((r, c))
#     return slots
#
#
# def get_partitions_for_size(total, max_same):
#     patterns = []
#     if total == 4:
#         patterns = [[2, 2], [4]]
#     elif total == 6:
#         patterns = [[3, 3], [4, 2], [2, 2, 2]]
#     elif total == 8:
#         patterns = [[4, 4], [6, 2], [4, 2, 2], [2, 2, 2, 2]]
#     elif total == 9:
#         patterns = [[3, 3, 3], [5, 4]]
#     elif total == 10:
#         patterns = [[5, 5], [6, 4], [4, 4, 2], [2, 2, 2, 2, 2]]
#     elif total == 12:
#         patterns = [[6, 6], [4, 4, 4], [4, 4, 2, 2]]
#     else:
#         if total % 2 == 0:
#             p = [];
#             rem = total
#             while rem > 0: take = min(rem, max_same); p.append(take); rem -= take
#             patterns = [p]
#         else:
#             p = [];
#             rem = total
#             while rem > 0: take = min(rem, max_same); p.append(take); rem -= take
#             patterns = [p]
#
#     valid = [p for p in patterns if all(x <= max_same for x in p)]
#     if not valid: valid = [[1] * total]
#
#     chosen = random.choice(valid)
#     chosen.sort(reverse=True)
#     return chosen
#
#
# def find_compact_cluster(rows, cols, mask, count):
#     all_cells = [(r, c) for r in range(rows) for c in range(cols)]
#     is_small_cluster = (count <= 2)
#     corners = [(rows - 1, cols - 1), (0, 0), (0, cols - 1), (rows - 1, 0)]
#
#     search_order = []
#     if is_small_cluster:
#         for c in corners:
#             if c not in mask: search_order.append(c)
#         others = [p for p in all_cells if p not in mask and p not in corners]
#         others.sort(key=lambda p: -min(p[0], p[1], rows - 1 - p[0], cols - 1 - p[1]))
#         search_order.extend(others)
#     else:
#         search_order = [p for p in all_cells if p not in mask]
#
#     best_cluster = []
#     best_score = -999
#     trials = 0
#     max_trials = 10 if is_small_cluster else 20
#
#     for start_node in search_order:
#         if start_node in mask: continue
#         cluster = [];
#         queue = [start_node];
#         visited_local = {start_node}
#
#         while len(cluster) < count and queue:
#             queue.sort(key=lambda p: abs(p[0] - start_node[0]) + abs(p[1] - start_node[1]))
#             curr = queue.pop(0);
#             cluster.append(curr);
#             r, c = curr
#             nbs = [(r + 1, c), (r, c + 1), (r - 1, c), (r, c - 1)]
#             for nr, nc in nbs:
#                 if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in mask and (nr, nc) not in visited_local:
#                     if len(cluster) + len(queue) < count:
#                         visited_local.add((nr, nc));
#                         queue.append((nr, nc))
#
#         if len(cluster) == count:
#             adjacency_score = 0
#             for i in range(len(cluster)):
#                 for j in range(i + 1, len(cluster)):
#                     if abs(cluster[i][0] - cluster[j][0]) + abs(cluster[i][1] - cluster[j][1]) == 1:
#                         adjacency_score += 1
#             position_score = -min(
#                 abs(r - cr) + abs(c - cc) for r, c in cluster for cr, cc in corners) if is_small_cluster else 0
#             total_score = adjacency_score * 10 + position_score
#
#             if total_score > best_score:
#                 best_score = total_score;
#                 best_cluster = cluster
#             trials += 1
#             if trials >= max_trials: break
#
#     # Fallback
#     if not best_cluster:
#         fallback = []
#         for p in search_order:
#             if p not in mask:
#                 fallback.append(p)
#                 if len(fallback) == count: return fallback
#         return fallback
#
#     return best_cluster
#
#
# def generate_cluster_pattern(rows, cols, max_types):
#     total = rows * cols
#     cells = [None] * total
#     limit = min(state.tray_color_variety, len(COLORS))
#     pool = list(range(limit))
#     safe_limit = max(1, total // 2)
#     limit_local = min(max_types, len(pool), safe_limit)
#     allowed = random.sample(pool, limit_local)
#
#     pattern = get_partitions_for_size(total, state.max_same_color)
#     tc, _ = global_stats()
#     mask = set()
#
#     def choose(cnts, size, opts):
#         sub = {k: cnts.get(k, 0) for k in opts}
#         m = min(sub.values()) if sub else 0
#         valid = [k for k, v in sub.items() if v <= m + 1]
#         return random.choice(valid) if valid else random.choice(opts)
#
#     if isinstance(pattern, list):
#         for size in pattern:
#             col = choose(tc, size, allowed)
#             tc[col] = tc.get(col, 0) + size
#             slots = find_compact_cluster(rows, cols, mask, size)
#             for r, c in slots: cells[r * cols + c] = col; mask.add((r, c))
#
#     for i in range(total):
#         if cells[i] is None: cells[i] = random.choice(allowed)
#     return [[cells[i * cols + j] for j in range(cols)] for i in range(rows)]
#
#
# # ============================================================
# # ALGORITHMS: SORTING (CROSS-TRAY OPTIMIZATION)
# # ============================================================
# def sort_grid_data(rows, cols, data_source):
#     items = [x for row in data_source for x in row if x is not None]
#     if not items: return data_source
#     counts = {x: items.count(x) for x in set(items)}
#     unique_items = sorted(list(set(items)), key=lambda x: -counts[x])
#     new_grid = [[None] * cols for _ in range(rows)]
#     mask = set()
#
#     for val in unique_items:
#         count = counts[val]
#         slots = find_compact_cluster(rows, cols, mask, count)
#         for r, c in slots: new_grid[r][c] = val; mask.add((r, c))
#
#     # Simple filling for leftover
#     remain = []
#     for r in range(rows):
#         for c in range(cols):
#             if new_grid[r][c] is None: remain.append((r, c))
#     # This shouldn't happen often if Compact algo works, but just in case
#     return new_grid
#
#
# def optimize_orphans(trays):
#     """
#     Tìm và ghép cặp các màu lẻ (số lượng < 2) giữa các khay.
#     """
#     # 1. Quét tìm các màu lẻ (orphans)
#     orphans = []  # List of {'tray': ct, 'color': col, 'count': n}
#
#     for ct in trays:
#         if not ct.cells: continue
#         flat = [x for row in ct.cells for x in row if x is not None]
#         counts = {x: flat.count(x) for x in set(flat)}
#
#         for col, n in counts.items():
#             if n < 2:  # Màu lẻ (ít hơn 2 khối)
#                 orphans.append({'tray': ct, 'color': col, 'count': n})
#
#     # 2. Tìm cặp matching (2 khay khác nhau có cùng màu lẻ)
#     # Gom theo màu
#     by_color = {}
#     for item in orphans:
#         c = item['color']
#         if c not in by_color: by_color[c] = []
#         by_color[c].append(item['tray'])
#
#     swapped = 0
#
#     # 3. Thực hiện tráo đổi (Swap) để gom về 1 khay
#     for col, tray_list in by_color.items():
#         while len(tray_list) >= 2:
#             t1 = tray_list.pop(0)
#             t2 = tray_list.pop(0)
#
#             # Cần chuyển block 'col' từ t2 sang t1 (hoặc ngược lại)
#             # Để làm được, t1 cần đẩy 1 block khác màu sang t2
#
#             # Tìm block cần chuyển ở t2
#             src_pos = None
#             for r in range(t2.rows):
#                 for c in range(t2.cols):
#                     if t2.cells[r][c] == col: src_pos = (r, c); break
#
#             # Tìm block để nhận ở t1 (block nào đó không phải màu col, và số lượng dư dả)
#             dst_pos = None
#             # Ưu tiên đổi block mà t1 đang có dư, hoặc block lẻ khác
#             for r in range(t1.rows):
#                 for c in range(t1.cols):
#                     v = t1.cells[r][c]
#                     if v is not None and v != col:
#                         dst_pos = (r, c)
#                         break  # Lấy tạm cái đầu tiên tìm được
#
#             if src_pos and dst_pos:
#                 # Swap
#                 val_src = t2.cells[src_pos[0]][src_pos[1]]  # == col
#                 val_dst = t1.cells[dst_pos[0]][dst_pos[1]]  # != col
#
#                 t2.cells[src_pos[0]][src_pos[1]] = val_dst
#                 t1.cells[dst_pos[0]][dst_pos[1]] = val_src
#                 swapped += 1
#
#     return swapped
#
#
# def sort_selected_trays(trays_to_sort):
#     if not trays_to_sort:
#         target_layers = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
#         if target_layers:
#             trays_to_sort = [ct for ct in state.containers if ct.layer in target_layers]
#         else:
#             trays_to_sort = state.containers
#
#     if not trays_to_sort:
#         state.last_action_message = "Nothing to sort"
#         return
#
#     # BƯỚC 1: Global Optimize (Gom màu lẻ giữa các khay)
#     # Chạy vài lần để tối ưu
#     opt_count = 0
#     for _ in range(3):
#         opt_count += optimize_orphans(trays_to_sort)
#
#     # BƯỚC 2: Local Sort (Sắp xếp gọn gàng từng khay)
#     count = 0
#     for ct in trays_to_sort:
#         # Sort Target
#         ct.target = sort_grid_data(ct.rows, ct.cols, ct.target)
#
#         # Sort Block
#         has_block = False
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         for row in ct.cells:
#             if any(x is not None for x in row): has_block = True
#
#         if has_block:
#             ct.cells = sort_grid_data(ct.rows, ct.cols, ct.cells)
#         count += 1
#
#     state.last_action_message = f"Sorted {count} trays (Merged {opt_count} orphans)"
#
#
# # --- SYMMETRY SPAWN LOGIC ---
# def spawn_new_trays():
#     master = Container(state.current_layer)
#     state.containers.append(master)
#
#     if state.symmetry_mode:
#         slave_rows, slave_cols = master.rows, master.cols
#         unique = sorted(list(set(x for row in master.target for x in row if x is not None)))
#         color_map = {}
#         if unique:
#             for i in range(len(unique)):
#                 src = unique[i]
#                 dst = unique[(i + 1) % len(unique)]
#                 color_map[src] = dst
#
#         slave_target = [[None] * slave_cols for _ in range(slave_rows)]
#         for r in range(slave_rows):
#             for c in range(slave_cols):
#                 orig = master.target[r][c]
#                 slave_target[r][c] = color_map.get(orig, orig)
#
#         slave = Container(state.current_layer, rows=slave_rows, cols=slave_cols, manual_target=slave_target)
#         slave.x = master.x + master.cols * CELL_SIZE + 60
#         slave.y = master.y
#         state.containers.append(slave)
#         state.last_action_message = "Spawned Symmetric Pair"
#     else:
#         state.last_action_message = "Spawned Single Tray"
#
#
# # --- FILL LOGIC (UNCHANGED) ---
# def find_best_slot_for_clustering(target_trays, color):
#     candidates_adj, candidates_free = [], []
#     for ct in target_trays:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         current_blocks = [x for row in ct.cells for x in row if x is not None]
#         if current_blocks.count(color) >= state.max_same_color: continue
#         unique_colors = set(current_blocks)
#         if color not in unique_colors and len(unique_colors) >= ct.max_types: continue
#
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is None:
#                     if ct.target[r][c] == color: continue
#                     has_adj = False
#                     for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
#                         nr, nc = r + dr, c + dc
#                         if 0 <= nr < ct.rows and 0 <= nc < ct.cols and ct.cells[nr][nc] == color:
#                             has_adj = True;
#                             break
#                     if has_adj:
#                         candidates_adj.append((ct, r, c))
#                     else:
#                         candidates_free.append((ct, r, c))
#     if candidates_adj: return random.choice(candidates_adj)
#     if candidates_free: return random.choice(candidates_free)
#     return None
#
#
# def fill_clustered_logic(trays, demand):
#     filled = 0
#     for col, cnt in sorted(demand.items(), key=lambda x: x[1], reverse=True):
#         for _ in range(cnt):
#             slot = find_best_slot_for_clustering(trays, col)
#             if slot:
#                 slot[0].cells[slot[1]][slot[2]] = col
#                 filled += 1
#             else:
#                 break
#     state.last_action_message = f"Filled: {filled}" if filled > 0 else "Fill Failed (Limits)"
#
#
# def fill_n(n):
#     if not state.selected_trays: return
#     tc, bc = global_stats()
#     limit = min(state.tray_color_variety, len(COLORS))
#     valid = [c for c in range(limit) if tc.get(c, 0) - bc.get(c, 0) >= n]
#     if valid:
#         col_to_fill = random.choice(valid)
#         fill_clustered_logic([state.selected_trays[0]], {col_to_fill: n})
#
#
# def auto_fill_mismatch(trays):
#     pool = set()
#     for ct in trays:
#         for r in ct.target:
#             for c in r: pool.add(c)
#     tc, bc = global_stats()
#     limit = min(state.tray_color_variety, len(COLORS))
#     demand = {}
#     for c in pool:
#         if c < limit:
#             need = tc.get(c, 0) - bc.get(c, 0)
#             if need > 0: demand[c] = need
#     fill_clustered_logic(trays, demand)
#
#
# def fill_layers():
#     tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
#     if not tls: tls = [state.current_layer]
#     targets = [c for c in state.containers if c.layer in tls]
#     if not targets: return
#     l_tc = {}
#     for c in targets:
#         for row in c.target:
#             for val in row: l_tc[val] = l_tc.get(val, 0) + 1
#     tc, bc = global_stats()
#     demand = {}
#     limit = min(state.tray_color_variety, len(COLORS))
#     for c, amt in l_tc.items():
#         if c < limit:
#             room = tc.get(c, 0) - bc.get(c, 0)
#             if room > 0: demand[c] = min(amt, room)
#     fill_clustered_logic(targets, demand)
#
#
# def fill_same():
#     tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
#     targets = [c for c in state.containers if c.layer in tls] if tls else state.selected_trays
#     if not targets: return
#     cnt = 0
#     for ct in targets:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         types = set(x for row in ct.cells for x in row if x is not None)
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is None:
#                     t = ct.target[r][c]
#                     if t in types or len(types) < ct.max_types:
#                         ct.cells[r][c] = t;
#                         types.add(t);
#                         cnt += 1
#     state.last_action_message = f"Filled Same: {cnt}"
#
#
# def shuffle_level():
#     targets = state.selected_trays if state.selected_trays else state.containers
#     slots = []
#     for ct in targets:
#         if not ct.cells: continue
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is not None: slots.append({'ct': ct, 'r': r, 'c': c})
#     if len(slots) < 2: return
#     random.shuffle(slots)
#     cnt = 0
#     for a in slots:
#         diff = random.randint(0, 100) < state.shuffle_ratio
#         cands = []
#         for b in slots:
#             if a['ct'] == b['ct'] and a['r'] == b['r'] and a['c'] == b['c']: continue
#             if (a['ct'].layer != b['ct'].layer) != diff: continue
#             val_a = a['ct'].cells[a['r']][a['c']]
#             val_b = b['ct'].cells[b['r']][b['c']]
#             tgt_a = a['ct'].target[a['r']][a['c']]
#             tgt_b = b['ct'].target[b['r']][b['c']]
#             if val_a != tgt_b and val_b != tgt_a: cands.append(b)
#         if cands:
#             b = random.choice(cands)
#             v1, v2 = a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']]
#             a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']] = v2, v1
#             cnt += 1
#     state.last_action_message = f"Shuffled: {cnt}"
#
#
# # --- SYSTEM ---
# def layout(arr):
#     vis = [c for c in arr if c.layer == state.current_layer]
#     cy = MARGIN_Y
#     for i in range(0, len(vis), MAX_PER_ROW):
#         row = vis[i:i + MAX_PER_ROW]
#         h = max(c.rows for c in row) * CELL_SIZE
#         for idx, c in enumerate(row):
#             c.x = MARGIN_X + idx * SLOT_W
#             c.y = cy
#         cy += h + 80
#
#
# def save_undo():
#     snap = []
#     for ct in state.containers:
#         new_ct = Container(ct.layer, rows=ct.rows, cols=ct.cols)
#         new_ct.max_types = ct.max_types
#         new_ct.x, new_ct.y = ct.x, ct.y
#         new_ct.cells = [row[:] for row in ct.cells] if ct.cells else None
#         new_ct.target = [row[:] for row in ct.target] if ct.target else None
#         snap.append(new_ct)
#     state.undo_stack.append(snap)
#     if len(state.undo_stack) > 20: state.undo_stack.pop(0)
#
#
# def undo():
#     if not state.undo_stack: return
#     state.containers = state.undo_stack.pop()
#     state.selected_trays = []
#     state.selected_cells = []
#     layout(state.containers)
#     state.last_action_message = "Undo"
#

########ver3########

# import random
# import pygame
# from config import *
#
#
# # ============================================================
# # STATS & UTILS
# # ============================================================
# def global_stats():
#     tc, bc = {}, {}
#     for ct in state.containers:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 t = ct.target[r][c]
#                 if t is not None: tc[t] = tc.get(t, 0) + 1
#                 b = ct.cells[r][c]
#                 if b is not None: bc[b] = bc.get(b, 0) + 1
#     return tc, bc
#
#
# def get_current_spawn_config():
#     config = {}
#     for row in state.ratio_ui_rows:
#         try:
#             s_txt = row['size'].lower()
#             w = int(row['weight'])
#             l = int(row.get('limit', '4'))
#             if 'x' in s_txt:
#                 r, c = map(int, s_txt.split('x'))
#                 if r > 0 and c > 0 and w > 0:
#                     config[(r, c)] = {'weight': w, 'limit': l}
#         except:
#             continue
#     if not config: return {(2, 2): {'weight': 100, 'limit': 2}}
#     return config
#
#
# # ============================================================
# # CONTAINER CLASS
# # ============================================================
# class Container:
#     def __init__(self, layer, rows=None, cols=None, manual_target=None):
#         if rows is None:
#             cfg = get_current_spawn_config()
#             k = random.choices(list(cfg.keys()), weights=[v['weight'] for v in cfg.values()])[0]
#             self.rows, self.cols = k
#             self.max_types = cfg[k]['limit']
#         else:
#             self.rows, self.cols = rows, cols
#             self.max_types = 4
#
#         self.cells = []
#
#         if manual_target:
#             self.target = manual_target
#         else:
#             self.target = generate_cluster_pattern(self.rows, self.cols, self.max_types)
#
#         self.x, self.y, self.layer = 0, 0, layer
#
#     def draw_target(self, s):
#         pygame.draw.rect(s, (255, 255, 255),
#                          (self.x - 5, self.y - 5, self.cols * CELL_SIZE + 10, self.rows * CELL_SIZE + 10), 2)
#         for r in range(self.rows):
#             for c in range(self.cols):
#                 col = self.target[r][c]
#                 rgb = COLORS[col] if col is not None and 0 <= col < len(COLORS) else (50, 50, 50)
#                 pygame.draw.rect(s, rgb, (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
#                 pygame.draw.rect(s, (200, 200, 200),
#                                  (self.x + c * CELL_SIZE, self.y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
#
#     def draw_block(self, s):
#         if not self.cells: return
#         ox = self.x + self.cols * CELL_SIZE + 20
#         oy = self.y
#         for r in range(self.rows):
#             for c in range(self.cols):
#                 col = self.cells[r][c]
#                 if col is not None and 0 <= col < len(COLORS):
#                     pygame.draw.rect(s, COLORS[col], (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
#                     pygame.draw.rect(s, (0, 0, 0), (ox + c * CELL_SIZE, oy + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
#
#
# # ============================================================
# # ALGORITHMS: PATTERN GENERATION
# # ============================================================
#
# def get_partitions_for_size(total, max_same):
#     patterns = []
#     if total == 4:
#         patterns = [[2, 2], [4]]
#     elif total == 6:
#         patterns = [[3, 3], [4, 2], [2, 2, 2]]
#     elif total == 8:
#         patterns = [[4, 4], [6, 2], [4, 2, 2], [2, 2, 2, 2]]
#     elif total == 9:
#         patterns = [[3, 3, 3], [5, 4]]
#     elif total == 10:
#         patterns = [[5, 5], [6, 4], [4, 4, 2], [2, 2, 2, 2, 2]]
#     elif total == 12:
#         patterns = [[6, 6], [4, 4, 4], [4, 4, 2, 2]]
#     else:
#         if total % 2 == 0:
#             p = [];
#             rem = total
#             while rem > 0: take = min(rem, max_same); p.append(take); rem -= take
#             patterns = [p]
#         else:
#             p = [];
#             rem = total
#             while rem > 0: take = min(rem, max_same); p.append(take); rem -= take
#             patterns = [p]
#
#     valid = [p for p in patterns if all(x <= max_same for x in p)]
#     if not valid: valid = [[1] * total]
#     chosen = random.choice(valid)
#     chosen.sort(reverse=True)
#     return chosen
#
#
# def find_compact_cluster(rows, cols, mask, count):
#     all_cells = [(r, c) for r in range(rows) for c in range(cols)]
#     is_small_cluster = (count <= 2)
#     corners = [(0, 0), (rows - 1, 0), (0, cols - 1), (rows - 1, cols - 1)]
#     anchor = random.choice(corners)
#     search_order = sorted(all_cells, key=lambda p: abs(p[0] - anchor[0]) + abs(p[1] - anchor[1]))
#
#     start_node = None
#     for p in search_order:
#         if p not in mask:
#             start_node = p;
#             break
#     if not start_node: return []
#
#     cluster = [];
#     queue = [start_node];
#     visited_local = {start_node}
#     while len(cluster) < count and queue:
#         queue.sort(key=lambda p: abs(p[0] - anchor[0]) + abs(p[1] - anchor[1]))
#         curr = queue.pop(0);
#         cluster.append(curr);
#         r, c = curr
#         nbs = [(r + 1, c), (r, c + 1), (r - 1, c), (r, c - 1)]
#         for nr, nc in nbs:
#             if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in mask and (nr, nc) not in visited_local:
#                 if len(cluster) + len(queue) < count:
#                     visited_local.add((nr, nc));
#                     queue.append((nr, nc))
#
#     if len(cluster) == count: return cluster
#     fallback = []
#     for p in search_order:
#         if p not in mask:
#             fallback.append(p)
#             if len(fallback) == count: return fallback
#     return fallback
#
#
# def generate_cluster_pattern(rows, cols, max_types):
#     total = rows * cols
#     cells = [None] * total
#     limit = min(state.tray_color_variety, len(COLORS))
#     pool = list(range(limit))
#     safe_limit = max(1, total // 2)
#     limit_local = min(max_types, len(pool), safe_limit)
#     allowed = random.sample(pool, limit_local)
#
#     pattern = get_partitions_for_size(total, state.max_same_color)
#     tc, _ = global_stats()
#     mask = set()
#
#     def choose(cnts, size, opts):
#         sub = {k: cnts.get(k, 0) for k in opts}
#         m = min(sub.values()) if sub else 0
#         valid = [k for k, v in sub.items() if v <= m + 1]
#         return random.choice(valid) if valid else random.choice(opts)
#
#     if isinstance(pattern, list):
#         for size in pattern:
#             col = choose(tc, size, allowed)
#             tc[col] = tc.get(col, 0) + size
#             slots = find_compact_cluster(rows, cols, mask, size)
#             for r, c in slots: cells[r * cols + c] = col; mask.add((r, c))
#
#     for i in range(total):
#         if cells[i] is None: cells[i] = random.choice(allowed)
#     return [[cells[i * cols + j] for j in range(cols)] for i in range(rows)]
#
#
# # ============================================================
# # ALGORITHMS: SORTING (RECTANGULAR PACKING & ORPHAN MERGE)
# # ============================================================
#
# def get_directional_slots(rows, cols):
#     slots = []
#     if rows < cols:
#         for c in range(cols):
#             for r in range(rows): slots.append((r, c))
#     else:
#         for r in range(rows):
#             for c in range(cols): slots.append((r, c))
#     return slots
#
#
# def find_rectangular_fit(rows, cols, mask, count):
#     """
#     Tìm vị trí để đặt một khối hình chữ nhật hoàn hảo kích thước = count.
#     Ví dụ count = 4 -> tìm 2x2, 1x4, 4x1.
#     Ưu tiên 2x2 hơn 1x4.
#     """
#     possible_shapes = []
#     # Tìm các ước số của count để ra kích thước hcn (r_size * c_size = count)
#     for r_size in range(1, count + 1):
#         if count % r_size == 0:
#             c_size = count // r_size
#             # Ưu tiên hình vuông hoặc gần vuông (hiệu số r-c nhỏ)
#             possible_shapes.append((r_size, c_size))
#
#     # Sort shapes: Ưu tiên hình vuông nhất (abs(r-c) nhỏ nhất)
#     possible_shapes.sort(key=lambda s: abs(s[0] - s[1]))
#
#     # Quét lưới để tìm chỗ trống phù hợp
#     for r_s, c_s in possible_shapes:
#         # Nếu hình dạng lớn hơn khay thì bỏ qua
#         if r_s > rows or c_s > cols: continue
#
#         # Quét kiểu sliding window
#         # Ưu tiên điền từ góc (0,0) hoặc (0, cols-1)...
#         # Để đơn giản, quét từ trái sang phải, trên xuống dưới, chỗ nào khớp thì lấy
#         for r in range(rows - r_s + 1):
#             for c in range(cols - c_s + 1):
#                 # Kiểm tra vùng này có trống không
#                 is_free = True
#                 slots = []
#                 for ir in range(r, r + r_s):
#                     for ic in range(c, c + c_s):
#                         if (ir, ic) in mask:
#                             is_free = False
#                             break
#                         slots.append((ir, ic))
#                     if not is_free: break
#
#                 if is_free:
#                     return slots  # Tìm thấy chỗ đặt đẹp!
#
#     return None  # Không tìm thấy chỗ hình chữ nhật
#
#
# def sort_grid_data(rows, cols, data_source):
#     items = [x for row in data_source for x in row if x is not None]
#     if not items: return data_source
#
#     counts = {x: items.count(x) for x in set(items)}
#     unique_items = sorted(list(set(items)), key=lambda x: -counts[x])  # Sort màu nhiều lên trước
#
#     new_grid = [[None] * cols for _ in range(rows)]
#     mask = set()
#
#     # Chiến thuật: Cố gắng xếp thành hình chữ nhật trước (Rectangular Packing)
#     # Nếu không được thì mới xếp theo dòng (Directional Flow)
#
#     leftover_items = []
#
#     for val in unique_items:
#         count = counts[val]
#
#         # 1. Thử xếp hình chữ nhật
#         slots = find_rectangular_fit(rows, cols, mask, count)
#
#         if slots:
#             for r, c in slots:
#                 new_grid[r][c] = val
#                 mask.add((r, c))
#         else:
#             # Nếu không xếp được hình đẹp, đẩy vào danh sách chờ để lấp chỗ trống sau
#             leftover_items.extend([val] * count)
#
#     # 2. Xử lý phần dư bằng Directional Fill (lấp vào các khe hở)
#     if leftover_items:
#         sorted_slots = get_directional_slots(rows, cols)
#         idx = 0
#         for r, c in sorted_slots:
#             if (r, c) not in mask:
#                 if idx < len(leftover_items):
#                     new_grid[r][c] = leftover_items[idx]
#                     idx += 1
#                 else:
#                     break
#
#     return new_grid
#
#
# def aggressive_orphan_merge(trays):
#     """
#     Tìm các màu lẻ (số lượng = 1) trên toàn bộ danh sách khay và ghép chúng lại.
#     Tráo đổi: Đưa Orphan từ Khay B về Khay A. Đẩy 1 block dư (nhiều nhất) từ A sang B.
#     """
#     # 1. Map: Color -> List of Trays containing exactly 1 block of that color
#     orphan_map = {}
#
#     # Helper để đếm và lấy vị trí
#     def get_info(ct):
#         if not ct.cells: return {}, {}
#         flat = [x for row in ct.cells for x in row if x is not None]
#         counts = {x: flat.count(x) for x in set(flat)}
#         positions = {}  # Color -> (r, c) (lấy vị trí đầu tiên tìm thấy)
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 val = ct.cells[r][c]
#                 if val is not None:
#                     if val not in positions: positions[val] = (r, c)
#         return counts, positions
#
#     for ct in trays:
#         counts, _ = get_info(ct)
#         for col, n in counts.items():
#             if n == 1:
#                 if col not in orphan_map: orphan_map[col] = []
#                 orphan_map[col].append(ct)
#
#     swaps_made = 0
#
#     # 2. Matchmaking
#     for col, tray_list in orphan_map.items():
#         # Cần ít nhất 2 khay có cùng màu lẻ để ghép
#         while len(tray_list) >= 2:
#             t_dest = tray_list.pop(0)  # Khay sẽ nhận màu lẻ (thành đôi)
#             t_src = tray_list.pop(0)  # Khay sẽ mất màu lẻ
#
#             # Lấy vị trí màu lẻ ở source
#             _, src_pos_map = get_info(t_src)
#             src_pos = src_pos_map[col]  # (r, c) của màu lẻ tại source
#
#             # Tìm block để đẩy từ Dest -> Source (để chỗ cho màu lẻ bay về)
#             # Ưu tiên đẩy màu mà t_dest đang có nhiều nhất (để bớt dư)
#             dest_counts, dest_pos_map = get_info(t_dest)
#
#             # Sort màu ở dest theo số lượng giảm dần, bỏ qua màu 'col' (vì nó đang lẻ 1, ko đẩy đi)
#             candidates = sorted([c for c in dest_counts if c != col], key=lambda x: -dest_counts[x])
#
#             if not candidates:
#                 # Dest chỉ có mỗi màu lẻ đó? Không swap được.
#                 continue
#
#             swap_col = candidates[0]
#             # Tìm một vị trí của swap_col tại dest
#             # (Phải quét lại grid để tìm vị trí cụ thể, vì pos_map chỉ lưu 1 vị trí)
#             swap_pos = None
#             for r in range(t_dest.rows):
#                 for c in range(t_dest.cols):
#                     if t_dest.cells[r][c] == swap_col:
#                         swap_pos = (r, c);
#                         break
#                 if swap_pos: break
#
#             if src_pos and swap_pos:
#                 # THỰC HIỆN SWAP
#                 # Orphan (col) bay từ Src -> Dest
#                 # Swap_Block (swap_col) bay từ Dest -> Src
#
#                 t_dest.cells[swap_pos[0]][swap_pos[1]] = col
#                 t_src.cells[src_pos[0]][src_pos[1]] = swap_col
#
#                 swaps_made += 1
#
#     return swaps_made
#
#
# def sort_selected_trays(trays_to_sort):
#     if not trays_to_sort:
#         target_layers = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
#         if target_layers:
#             trays_to_sort = [ct for ct in state.containers if ct.layer in target_layers]
#         else:
#             trays_to_sort = state.containers
#
#     if not trays_to_sort:
#         state.last_action_message = "Nothing to sort"
#         return
#
#     # BƯỚC 1: Global Optimize (Gom màu lẻ giữa các khay)
#     orphan_merges = 0
#     # Chạy vài vòng để tối ưu hóa dây chuyền
#     for _ in range(5):
#         m = aggressive_orphan_merge(trays_to_sort)
#         if m == 0: break
#         orphan_merges += m
#
#     # BƯỚC 2: Local Sort (Sắp xếp gọn gàng từng khay bằng Rectangular Packing)
#     count = 0
#     for ct in trays_to_sort:
#         ct.target = sort_grid_data(ct.rows, ct.cols, ct.target)
#
#         has_block = False
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         for row in ct.cells:
#             if any(x is not None for x in row): has_block = True
#
#         if has_block:
#             ct.cells = sort_grid_data(ct.rows, ct.cols, ct.cells)
#
#         count += 1
#
#     state.last_action_message = f"Sorted {count} trays (Merged {orphan_merges} orphans)"
#
#
# # --- SYMMETRY SPAWN LOGIC ---
# def spawn_new_trays():
#     master = Container(state.current_layer)
#     state.containers.append(master)
#
#     if state.symmetry_mode:
#         slave_rows, slave_cols = master.rows, master.cols
#         unique = sorted(list(set(x for row in master.target for x in row if x is not None)))
#         color_map = {}
#         if unique:
#             for i in range(len(unique)):
#                 src = unique[i]
#                 dst = unique[(i + 1) % len(unique)]
#                 color_map[src] = dst
#
#         slave_target = [[None] * slave_cols for _ in range(slave_rows)]
#         for r in range(slave_rows):
#             for c in range(slave_cols):
#                 orig = master.target[r][c]
#                 slave_target[r][c] = color_map.get(orig, orig)
#
#         slave = Container(state.current_layer, rows=slave_rows, cols=slave_cols, manual_target=slave_target)
#         slave.x = master.x + master.cols * CELL_SIZE + 60
#         slave.y = master.y
#         state.containers.append(slave)
#         state.last_action_message = "Spawned Symmetric Pair"
#     else:
#         state.last_action_message = "Spawned Single Tray"
#
#
# # --- FILL LOGIC (UNCHANGED) ---
# def find_best_slot_for_clustering(target_trays, color):
#     candidates_adj, candidates_free = [], []
#     for ct in target_trays:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         current_blocks = [x for row in ct.cells for x in row if x is not None]
#         if current_blocks.count(color) >= state.max_same_color: continue
#         unique_colors = set(current_blocks)
#         if color not in unique_colors and len(unique_colors) >= ct.max_types: continue
#
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is None:
#                     if ct.target[r][c] == color: continue
#                     has_adj = False
#                     for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
#                         nr, nc = r + dr, c + dc
#                         if 0 <= nr < ct.rows and 0 <= nc < ct.cols and ct.cells[nr][nc] == color:
#                             has_adj = True;
#                             break
#                     if has_adj:
#                         candidates_adj.append((ct, r, c))
#                     else:
#                         candidates_free.append((ct, r, c))
#     if candidates_adj: return random.choice(candidates_adj)
#     if candidates_free: return random.choice(candidates_free)
#     return None
#
#
# def fill_clustered_logic(trays, demand):
#     filled = 0
#     for col, cnt in sorted(demand.items(), key=lambda x: x[1], reverse=True):
#         for _ in range(cnt):
#             slot = find_best_slot_for_clustering(trays, col)
#             if slot:
#                 slot[0].cells[slot[1]][slot[2]] = col
#                 filled += 1
#             else:
#                 break
#     state.last_action_message = f"Filled: {filled}" if filled > 0 else "Fill Failed (Limits)"
#
#
# def fill_n(n):
#     if not state.selected_trays: return
#     tc, bc = global_stats()
#     limit = min(state.tray_color_variety, len(COLORS))
#     valid = [c for c in range(limit) if tc.get(c, 0) - bc.get(c, 0) >= n]
#     if valid:
#         col_to_fill = random.choice(valid)
#         fill_clustered_logic([state.selected_trays[0]], {col_to_fill: n})
#
#
# def auto_fill_mismatch(trays):
#     pool = set()
#     for ct in trays:
#         for r in ct.target:
#             for c in r: pool.add(c)
#     tc, bc = global_stats()
#     limit = min(state.tray_color_variety, len(COLORS))
#     demand = {}
#     for c in pool:
#         if c < limit:
#             need = tc.get(c, 0) - bc.get(c, 0)
#             if need > 0: demand[c] = need
#     fill_clustered_logic(trays, demand)
#
#
# def fill_layers():
#     tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
#     if not tls: tls = [state.current_layer]
#     targets = [c for c in state.containers if c.layer in tls]
#     if not targets: return
#     l_tc = {}
#     for c in targets:
#         for row in c.target:
#             for val in row: l_tc[val] = l_tc.get(val, 0) + 1
#     tc, bc = global_stats()
#     demand = {}
#     limit = min(state.tray_color_variety, len(COLORS))
#     for c, amt in l_tc.items():
#         if c < limit:
#             room = tc.get(c, 0) - bc.get(c, 0)
#             if room > 0: demand[c] = min(amt, room)
#     fill_clustered_logic(targets, demand)
#
#
# def fill_same():
#     tls = [i + 1 for i, c in enumerate(state.layer_checkbox) if c]
#     targets = [c for c in state.containers if c.layer in tls] if tls else state.selected_trays
#     if not targets: return
#     cnt = 0
#     for ct in targets:
#         if not ct.cells: ct.cells = [[None] * ct.cols for _ in range(ct.rows)]
#         types = set(x for row in ct.cells for x in row if x is not None)
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is None:
#                     t = ct.target[r][c]
#                     if t in types or len(types) < ct.max_types:
#                         ct.cells[r][c] = t;
#                         types.add(t);
#                         cnt += 1
#     state.last_action_message = f"Filled Same: {cnt}"
#
#
# def shuffle_level():
#     targets = state.selected_trays if state.selected_trays else state.containers
#     slots = []
#     for ct in targets:
#         if not ct.cells: continue
#         for r in range(ct.rows):
#             for c in range(ct.cols):
#                 if ct.cells[r][c] is not None: slots.append({'ct': ct, 'r': r, 'c': c})
#     if len(slots) < 2: return
#     random.shuffle(slots)
#     cnt = 0
#     for a in slots:
#         diff = random.randint(0, 100) < state.shuffle_ratio
#         cands = []
#         for b in slots:
#             if a['ct'] == b['ct'] and a['r'] == b['r'] and a['c'] == b['c']: continue
#             if (a['ct'].layer != b['ct'].layer) != diff: continue
#             va = a['ct'].cells[a['r']][a['c']]
#             vb = b['ct'].cells[b['r']][b['c']]
#             ta = a['ct'].target[a['r']][a['c']]
#             tb = b['ct'].target[b['r']][b['c']]
#             if va != tb and vb != ta: cands.append(b)
#         if cands:
#             b = random.choice(cands)
#             v1, v2 = a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']]
#             a['ct'].cells[a['r']][a['c']], b['ct'].cells[b['r']][b['c']] = v2, v1
#             cnt += 1
#     state.last_action_message = f"Shuffled: {cnt}"
#
#
# # --- SYSTEM ---
# def layout(arr):
#     vis = [c for c in arr if c.layer == state.current_layer]
#     cy = MARGIN_Y
#     for i in range(0, len(vis), MAX_PER_ROW):
#         row = vis[i:i + MAX_PER_ROW]
#         h = max(c.rows for c in row) * CELL_SIZE
#         for idx, c in enumerate(row):
#             c.x = MARGIN_X + idx * SLOT_W
#             c.y = cy
#         cy += h + 80
#
#
# def save_undo():
#     snap = []
#     for ct in state.containers:
#         new_ct = Container(ct.layer, rows=ct.rows, cols=ct.cols)
#         new_ct.max_types = ct.max_types
#         new_ct.x, new_ct.y = ct.x, ct.y
#         new_ct.cells = [row[:] for row in ct.cells] if ct.cells else None
#         new_ct.target = [row[:] for row in ct.target] if ct.target else None
#         snap.append(new_ct)
#     state.undo_stack.append(snap)
#     if len(state.undo_stack) > 20: state.undo_stack.pop(0)
#
#
# def undo():
#     if not state.undo_stack: return
#     state.containers = state.undo_stack.pop()
#     state.selected_trays = []
#     state.selected_cells = []
#     layout(state.containers)
#     state.last_action_message = "Undo"


##########ver4############

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