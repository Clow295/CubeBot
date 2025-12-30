# RAYLINE/CONVEYOR SYSTEM - THIẾT KẾ CHI TIẾT

## 1. PHÂN TÍCH KIẾN TRÚC HIỆN TẠI

### Cấu trúc MVC hiện tại:
```
main.py        → Controller (event loop, keyboard/mouse handling)
ui.py          → View (rendering panels, stats, gameplay)
logic_core.py  → Model (spawn, fill, shuffle, layout logic)
logic_export.py → Service (Unity JSON export)
config.py      → State & Constants
```

### State Management:
- `State` class trong `config.py` chứa:
  - `containers` - danh sách trays
  - `undo_stack` - history cho undo
  - `selected_trays`, `selected_cells` - selections
  - `current_layer`, `layer_checkbox` - layer control
  - Các config params: `tray_color_variety`, `max_same_color`, etc.

### Layout System hiện tại:
- Function `layout()` trong `logic_core.py:522`
- Tự động tính toán vị trí trays theo grid 3 cột
- Công thức: `c.x = MARGIN_X + idx * SLOT_W`, `c.y = cy`

### Spawn System hiện tại:
- Function `spawn_new_trays()` trong `logic_core.py:359`
- Tạo Container mới với layer hiện tại
- Hỗ trợ Symmetry Mode (tạo cặp đối xứng)
- Sau spawn → gọi `layout()` để tính toán vị trí

---

## 2. DATA STRUCTURE DESIGN

### A. Rayline Data Structure

Thêm vào `State` class trong `config.py`:

```python
class State:
    # ... existing fields ...

    # RAYLINE DATA
    rayline_enabled = False          # Toggle rayline on/off
    rayline_points = []              # List of (grid_x, grid_y) tuples
    rayline_edit_mode = False        # True khi đang vẽ rayline
    rayline_temp_drawing = []        # Temporary path khi đang drag

    # RAYLINE GRID CONFIG
    rayline_grid_size = 10           # Grid 10x10
    rayline_cell_size = 40           # Mỗi ô 40px
    rayline_offset_x = 0             # Offset X của grid (tính sau)
    rayline_offset_y = 0             # Offset Y của grid
```

### B. Rayline Coordinate System

**Grid Space → World Space Conversion:**
```python
# Grid space: (0,0) đến (9,9) - tương đối
# World space: Unity coordinate (-5, -5) đến (5, 5)

def grid_to_world(grid_x, grid_y):
    """Convert grid coordinate to Unity world space"""
    # Map từ 0-9 → -5 đến +5
    world_x = (grid_x - 4.5) * 1.0  # Center tại 4.5
    world_y = (grid_y - 4.5) * 1.0
    return (world_x, world_y)

def world_to_grid(world_x, world_y):
    """Convert Unity world coordinate to grid"""
    grid_x = int(world_x + 4.5)
    grid_y = int(world_y + 4.5)
    return (grid_x, grid_y)
```

### C. Container Spawn Constraint Data

```python
class SpawnConstraint:
    """Constraint cho việc spawn container quanh rayline"""
    rayline_points_world = []  # Rayline trong world space
    min_distance = 2.0         # Khoảng cách tối thiểu từ rayline
    spawn_zone_padding = 1.0   # Padding cho spawn zone
```

---

## 3. UI DESIGN - RAYLINE EDITOR

### A. UI Layout Options

**Option 1: Modal Window (Recommended)**
- Hiển thị rayline editor như một overlay modal
- Kích hoạt bằng nút "Edit Rayline" trong right panel
- Background dim để focus vào editor
- Có nút Close để quay về gameplay view

**Option 2: Tab System**
- Thêm tabs: "Gameplay" và "Rayline"
- Switch giữa 2 modes
- Phức tạp hơn nhưng professional hơn

**Lựa chọn: Option 1 - Modal Window** (đơn giản, dễ implement)

### B. Modal Window Specification

**Kích thước & Vị trí:**
```python
RAYLINE_MODAL_W = 600
RAYLINE_MODAL_H = 700
RAYLINE_MODAL_X = (WIDTH - RAYLINE_MODAL_W) // 2
RAYLINE_MODAL_Y = (HEIGHT - RAYLINE_MODAL_H) // 2
```

**Layout:**
```
┌─────────────────────────────────────┐
│         RAYLINE EDITOR              │
├─────────────────────────────────────┤
│  [Grid 10x10 - 400x400px]           │
│                                     │
│  • Rayline points hiển thị         │
│  • Drag để vẽ path                 │
│  • Visual feedback                 │
│                                     │
├─────────────────────────────────────┤
│  [Save] [Clear] [Close]             │
│  Status: N points                   │
└─────────────────────────────────────┘
```

**Grid Rendering:**
- Grid 10x10 cells
- Mỗi cell 40x40 px → total 400x400px
- Background: dark gray
- Grid lines: light gray
- Rayline path: bright color (cyan/yellow)
- Hover cell: highlight

### C. Drawing Interaction

**Mouse Events:**

1. **Mouse Down** (trong grid area):
   - Bắt đầu vẽ path
   - Lưu điểm đầu tiên vào `rayline_temp_drawing`
   - Set flag `is_drawing = True`

2. **Mouse Motion** (khi `is_drawing = True`):
   - Tính cell hiện tại từ mouse position
   - Nếu cell khác cell cuối trong `rayline_temp_drawing`:
     - Thêm vào `rayline_temp_drawing`
   - Chỉ cho phép di chuyển horizontal hoặc vertical (không diagonal)

3. **Mouse Up**:
   - Kết thúc vẽ
   - Copy `rayline_temp_drawing` → `state.rayline_points`
   - Clear `rayline_temp_drawing`
   - Set `is_drawing = False`

**Keyboard Shortcuts:**
- `R`: Toggle rayline edit mode
- `Esc`: Close modal
- `Ctrl+Z`: Undo last point

### D. Control Buttons

**Save Button:**
- Lưu `rayline_temp_drawing` vào `state.rayline_points`
- Set `state.rayline_enabled = True`
- Tính toán lại spawn zones
- Close modal

**Clear Button:**
- Clear `state.rayline_points`
- Clear `rayline_temp_drawing`
- Set `state.rayline_enabled = False`

**Close Button:**
- Close modal
- Nếu chưa save, hỏi confirm

---

## 4. SPAWN ALGORITHM AROUND RAYLINE

### A. Spawn Strategy Overview

**Khi rayline enabled:**
1. Tính toán spawn zones dọc theo rayline
2. Random chọn zone
3. Tìm vị trí hợp lệ trong zone (không overlap, cách rayline >= 2 units)
4. Spawn container tại vị trí đó

**Khi rayline disabled:**
- Giữ nguyên 100% logic spawn cũ
- Không thay đổi gì

### B. Spawn Zone Calculation

```python
def calculate_spawn_zones(rayline_points, num_zones=8):
    """
    Chia rayline thành các zones để spawn container

    Args:
        rayline_points: List[(grid_x, grid_y)]
        num_zones: Số zones chia

    Returns:
        List[SpawnZone] - mỗi zone chứa center point và radius
    """
    zones = []
    if len(rayline_points) < 2:
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
            'radius': 3.0,  # Spawn trong bán kính 3 units
            'used': False
        })

    return zones
```

### C. Valid Position Check

```python
def is_valid_spawn_position(x, y, container_width, container_height, rayline_points):
    """
    Kiểm tra vị trí spawn có hợp lệ không

    Constraints:
    1. Cách rayline ít nhất 2 units
    2. Không overlap với containers khác
    3. Nằm trong boundaries
    """
    # Check 1: Distance from rayline
    min_dist = calculate_min_distance_to_rayline(x, y, rayline_points)
    if min_dist < 2.0:
        return False

    # Check 2: Overlap với containers khác
    new_rect = create_rect(x, y, container_width, container_height)
    for ct in state.containers:
        if ct.layer != state.current_layer:
            continue
        ct_rect = create_rect(ct.world_x, ct.world_y, ct.cols, ct.rows)
        if check_overlap(new_rect, ct_rect):
            return False

    # Check 3: Boundaries
    if x < -10 or x > 10 or y < -10 or y > 10:
        return False

    return True

def calculate_min_distance_to_rayline(x, y, rayline_points):
    """Tính khoảng cách ngắn nhất từ (x,y) đến rayline"""
    min_dist = float('inf')

    for gx, gy in rayline_points:
        wx, wy = grid_to_world(gx, gy)
        dist = math.sqrt((x - wx)**2 + (y - wy)**2)
        min_dist = min(min_dist, dist)

    return min_dist
```

### D. Modified Spawn Function

```python
def spawn_new_trays_with_rayline():
    """
    Modified spawn function với rayline support
    """
    if not state.rayline_enabled or not state.rayline_points:
        # Fallback to original spawn logic
        spawn_new_trays_original()
        return

    # Calculate spawn zones
    zones = calculate_spawn_zones(state.rayline_points)

    # Random chọn zone chưa dùng
    available_zones = [z for z in zones if not z['used']]
    if not available_zones:
        # Reset all zones
        for z in zones:
            z['used'] = False
        available_zones = zones

    zone = random.choice(available_zones)

    # Tạo container
    master = Container(state.current_layer)

    # Tìm vị trí hợp lệ quanh zone center
    max_attempts = 50
    found = False

    for _ in range(max_attempts):
        # Random offset từ center
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(2.5, zone['radius'])

        world_x = zone['center'][0] + radius * math.cos(angle)
        world_y = zone['center'][1] + radius * math.sin(angle)

        if is_valid_spawn_position(world_x, world_y, master.cols, master.rows, state.rayline_points):
            # Convert world → screen position
            master.world_x = world_x
            master.world_y = world_y
            master.x = world_to_screen_x(world_x)
            master.y = world_to_screen_y(world_y)

            found = True
            zone['used'] = True
            break

    if not found:
        # Fallback: spawn theo logic cũ
        spawn_new_trays_original()
        return

    state.containers.append(master)

    # Symmetry mode (nếu bật)
    if state.symmetry_mode:
        spawn_symmetry_pair(master, zone)

    state.last_action_message = "Spawned around Rayline"
```

### E. Coordinate Conversion Helpers

```python
def world_to_screen_x(world_x):
    """Convert Unity world X to Pygame screen X"""
    # Inverse of export formula: ux = ((ct.x - WIDTH/2) / 100.0) * 2
    # → ct.x = (ux / 2) * 100.0 + WIDTH/2
    return (world_x / 2) * 100.0 + WIDTH / 2

def world_to_screen_y(world_y):
    """Convert Unity world Y to Pygame screen Y"""
    # Inverse of: uy = (-(ct.y - HEIGHT/2) / 100.0) * 2
    # → ct.y = -uy / 2 * 100.0 + HEIGHT/2
    return (-world_y / 2) * 100.0 + HEIGHT / 2
```

---

## 5. EXPORT LOGIC UPDATE

### A. ConveyorSegments Export

Trong `logic_export.py`, update function `export_to_unity_json()`:

```python
def export_to_unity_json(filename="Level_0.json"):
    # ... existing code ...

    # NEW: Export ConveyorSegments
    conveyor_segments = []
    if state.rayline_enabled and state.rayline_points:
        for gx, gy in state.rayline_points:
            wx, wy = grid_to_world(gx, gy)
            conveyor_segments.append({
                "Position": f"{wx:.0f};{wy:.0f}"
            })

    final = {
        "Version": 10,
        "MaxInstanceId": id_counter[0],
        # ... other fields ...
        "ConveyorSegments": conveyor_segments,  # ← NEW
        "ConveyorSlots": [],
        "CellBlocks": [t["data"] for t in temp],
        "CellSlots": ex_slots,
        "BlockColors": ex_colors,
        # ...
    }

    # ... rest of export code ...
```

### B. Export Format Example

```json
{
  "Version": 10,
  "ConveyorSegments": [
    {"Position": "-3;0"},
    {"Position": "-2;0"},
    {"Position": "-1;0"},
    {"Position": "0;0"},
    {"Position": "1;0"},
    {"Position": "2;0"}
  ],
  "CellBlocks": [...],
  "CellSlots": [...],
  "BlockColors": [...]
}
```

---

## 6. FILES CẦN CHỈNH SỬA / TẠO MỚI

### A. Chỉnh sửa Files Hiện Tại

#### 1. `config.py`
**Thêm:**
- Rayline state variables (rayline_enabled, rayline_points, etc.)
- Rayline modal constants (RAYLINE_MODAL_W, etc.)
- Grid conversion constants

#### 2. `main.py`
**Thêm:**
- Rayline modal event handling
- Keyboard shortcut `R` để mở rayline editor
- Mouse events trong rayline grid
- Conditional rendering của modal

#### 3. `ui.py`
**Thêm:**
- Function `draw_rayline_modal(screen)`
- Function `draw_rayline_grid(screen)`
- Function `draw_rayline_path(screen, points)`
- Function `draw_rayline_controls(screen)`

#### 4. `logic_core.py`
**Thêm:**
- Function `calculate_spawn_zones(rayline_points)`
- Function `is_valid_spawn_position(x, y, w, h, rayline_points)`
- Function `calculate_min_distance_to_rayline(x, y, rayline_points)`
- Function `world_to_screen_x(world_x)`, `world_to_screen_y(world_y)`
- Function `grid_to_world(gx, gy)`, `world_to_grid(wx, wy)`
- Modify `spawn_new_trays()` để check rayline_enabled

#### 5. `logic_export.py`
**Thêm:**
- ConveyorSegments export logic
- Grid to world conversion cho export

### B. File Mới (Optional)

#### `logic_rayline.py` (Recommended)
**Chứa:**
- Tất cả rayline-related logic
- Spawn zone calculation
- Distance checking
- Coordinate conversion
- Giữ code organized và modular

**Lý do tách riêng:**
- Tránh làm phình `logic_core.py` (đã 553 lines)
- Dễ maintain và test
- Clear separation of concerns

---

## 7. IMPLEMENTATION PLAN

### Phase 1: Data Structure & State (30 min)
1. ✅ Update `config.py` - thêm rayline state
2. ✅ Create `logic_rayline.py` - helper functions
3. ✅ Add coordinate conversion functions

### Phase 2: UI - Rayline Editor (1 hour)
1. ✅ Draw rayline modal window (`ui.py`)
2. ✅ Draw 10x10 grid
3. ✅ Implement mouse drawing interaction
4. ✅ Add control buttons (Save, Clear, Close)
5. ✅ Visual feedback (hover, path preview)

### Phase 3: Spawn Logic Integration (1 hour)
1. ✅ Implement spawn zone calculation
2. ✅ Implement valid position check
3. ✅ Modify `spawn_new_trays()` với rayline support
4. ✅ Test spawn distribution
5. ✅ Handle edge cases (no valid position)

### Phase 4: Export Logic (30 min)
1. ✅ Update `export_to_unity_json()`
2. ✅ Add ConveyorSegments generation
3. ✅ Test export format

### Phase 5: Testing & Polish (30 min)
1. ✅ Test full workflow: draw → spawn → export
2. ✅ Test edge cases (empty rayline, etc.)
3. ✅ Test undo/redo compatibility
4. ✅ Add keyboard shortcuts
5. ✅ Add status messages

**Total Estimated Time: 3-4 hours**

---

## 8. RÀNG BUỘC & COMPATIBILITY

### A. Backward Compatibility
✅ **Không phá vỡ logic cũ:**
- Khi `rayline_enabled = False` → 100% logic spawn cũ
- Khi `rayline_points = []` → fallback to original
- Không thay đổi existing Container class
- Không ảnh hưởng export format cũ (ConveyorSegments empty list)

### B. Undo System Compatibility
✅ **Rayline state trong undo:**
- Option 1: Rayline state không vào undo (recommended - vì rayline là global setup, không phải level state)
- Option 2: Include rayline trong undo snapshot (phức tạp hơn)

**Lựa chọn: Option 1**

### C. Layer System Compatibility
✅ **Rayline và layers:**
- Rayline là global (không phụ thuộc layer)
- Spawn logic chỉ spawn vào `current_layer`
- Multi-layer spawn vẫn hoạt động bình thường

### D. Symmetry Mode Compatibility
✅ **Rayline + Symmetry:**
- Khi symmetry mode ON:
  - Spawn master quanh rayline
  - Spawn slave ở vị trí symmetric (có thể xa rayline)
- Chỉ master cần thỏa rayline constraint

---

## 9. EDGE CASES & ERROR HANDLING

### A. Empty Rayline
- **Case**: User không vẽ rayline
- **Handling**: Fallback to original spawn logic

### B. Rayline quá ngắn (< 2 points)
- **Case**: Rayline chỉ có 1-2 điểm
- **Handling**: Treat as single spawn zone với radius lớn

### C. Không tìm thấy vị trí hợp lệ
- **Case**: Sau 50 attempts vẫn không spawn được
- **Handling**:
  - Fallback to original spawn logic
  - Show warning message: "Cannot spawn near rayline, using default"

### D. Container quá lớn
- **Case**: Container 5x5 không fit quanh rayline
- **Handling**: Tăng search radius, hoặc fallback

### E. Rayline ở góc screen
- **Case**: Rayline vẽ ở biên, không đủ space spawn
- **Handling**: Spawn ở phía có space, ignore rayline constraint nếu cần

---

## 10. TESTING CHECKLIST

### Functional Tests
- [ ] Vẽ rayline mới → save → spawn → verify positions
- [ ] Clear rayline → spawn → verify dùng logic cũ
- [ ] Export với rayline → verify ConveyorSegments format
- [ ] Export không có rayline → verify ConveyorSegments = []
- [ ] Undo/redo không ảnh hưởng rayline
- [ ] Symmetry mode + rayline → verify cặp spawn đúng
- [ ] Multi-layer + rayline → verify spawn đúng layer

### Edge Case Tests
- [ ] Rayline 1 điểm
- [ ] Rayline 100 điểm
- [ ] Rayline diagonal
- [ ] Rayline ở góc màn hình
- [ ] Spawn khi đã có nhiều containers
- [ ] Spawn container lớn (5x5)

### UI Tests
- [ ] Modal mở/đóng smooth
- [ ] Drawing responsive (không lag)
- [ ] Hover feedback rõ ràng
- [ ] Button clicks hoạt động
- [ ] Keyboard shortcuts work

---

## 11. FUTURE ENHANCEMENTS (Out of Scope)

### A. Multiple Raylines
- Hỗ trợ nhiều rayline paths
- Mỗi rayline có ID riêng

### B. Rayline Properties
- Customize rayline width
- Customize min_distance per rayline
- Rayline color options

### C. Advanced Spawn
- Directional spawn (chỉ spawn bên trái/phải rayline)
- Density control (spawn nhiều ở đầu/cuối rayline)
- Priority zones (spawn nhiều ở zones cụ thể)

### D. Visual Enhancements
- Animate rayline drawing
- Show spawn zones visualization
- Show distance indicators

---

## 12. SUMMARY

### Core Concept
- **Rayline**: Đường path do user vẽ, định nghĩa "conveyor belt"
- **Spawn Constraint**: Containers spawn quanh rayline (distance >= 2)
- **Export**: Rayline → ConveyorSegments trong Unity JSON

### Key Design Decisions
1. **Modal UI** cho rayline editor (không phức tạp hóa main UI)
2. **Separate file** `logic_rayline.py` (modularity)
3. **Fallback strategy** (rayline optional, không break existing)
4. **Grid 10x10** mapping to Unity world space (-5 to +5)
5. **Zone-based spawn** (distribute evenly along rayline)

### Implementation Priority
1. **Phase 1-2**: UI first (để test drawing interaction)
2. **Phase 3**: Spawn logic (core feature)
3. **Phase 4**: Export (last step)

### Success Criteria
✅ User có thể vẽ rayline dễ dàng
✅ Containers spawn hợp lý quanh rayline
✅ Export format đúng Unity spec
✅ Không break existing features
✅ Code clean, maintainable

---

**Document Status:** READY FOR IMPLEMENTATION
**Author:** AI Design Assistant
**Date:** 2025-12-30
**Version:** 1.0
