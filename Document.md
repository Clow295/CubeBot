# CubeBot - Puzzle King Documentation

## Tổng Quan Dự Án

**CubeBot - Puzzle King** là một công cụ chuyên nghiệp để thiết kế và tạo level cho game puzzle kiểu Color Cube Match, với hệ thống rayline/conveyor hỗ trợ spawn containers theo đường dẫn.

**Yêu cầu hệ thống:** Python 3.12.xx

**Công nghệ chính:** Pygame, Python Standard Libraries

---

## Cấu Trúc Project

```
CubeBot/
├── .git/                   # Git repository
├── .idea/                  # IDE configuration
├── __pycache__/           # Python bytecode cache
├── save_level/            # Thư mục lưu level đã xuất
│   ├── Level_*.json       # File level Unity format
│   └── Level_*.json.meta  # Unity meta files
├── .gitignore             # Git ignore configuration
├── Document.md            # Documentation (file này)
├── README.md              # Project README
├── config.py              # File cấu hình chính
├── logic_core.py          # Core logic và thuật toán
├── logic_export.py        # Logic xuất file Unity
├── logic_rayline.py       # Logic rayline/conveyor system
├── main.py                # Entry point của ứng dụng
└── ui.py                  # UI rendering
```

---

## Các Module Chính

### 1. main.py - Entry Point & Game Loop
**Chức năng:**
- Khởi tạo Pygame window (1600x900)
- Game loop chính với event handling
- Xử lý input: mouse clicks, keyboard shortcuts, rayline drawing
- Điều phối giữa các module UI và Logic

**Keyboard Shortcuts:**
- `Space`: Spawn new trays (theo ray nếu có, hoặc random)
- `1-6`: Fill N blocks cùng màu vào selected trays
- `P`: Toggle paint mode
- `0-9`: Paint blocks (Alt + 0-9 để paint targets)
- `T`: Swap nội dung 2 trays đã chọn
- `S`: Shuffle level
- `U`: Undo
- `D`: Delete selected trays
- `E`: Export to Unity JSON
- `+/-`: Tăng/giảm Tray Color Variety
- `,/.`: Tăng/giảm Max Same Color
- `R`: Toggle Ray Editor modal

**Event Handling:**
- Mouse motion: Vẽ rayline khi đang trong chế độ drawing
- Mouse down/up: Select trays, paint cells, vẽ rayline
- Keyboard: Shortcuts và text input cho table

### 2. config.py - Configuration & Constants
**Chứa:**
- Constants: kích thước màn hình (WIDTH=1600, HEIGHT=900)
- Bảng màu: 10 màu chuẩn (Blue, Cyan, Green, Skin, Magenta, Orange, Purple, Red, White, Yellow)
- Class State: quản lý trạng thái toàn cục của ứng dụng
- UI layout positions và button rectangles
- Cấu hình spawn ratio table
- Rayline modal configuration
- Ray spawn tuning parameters

**Cấu hình mặc định:**
```python
WIDTH, HEIGHT = 1600, 900
PANEL_LEFT_W = 320
PANEL_RIGHT_W = 280
CELL_SIZE = 20
MAX_PER_ROW = 3
MAX_TRAY_PER_LAYER = 15

# State defaults
tray_color_variety = 4    # Số loại màu trong tray
max_same_color = 4        # Max số lượng cùng màu
shuffle_ratio = 50        # % shuffle cross-layer
symmetry_mode = False     # Spawn đối xứng
```

**Spawn Ratio Table mặc định:**
```python
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
```

**Rayline Configuration:**
```python
RAYLINE_GRID_SIZE = 16           # Grid 16x16
RAYLINE_CELL_SIZE = 40           # Mỗi ô 40px
RAY_GRID_CENTER = 7.5            # Center của grid
RAY_SPAWN_SPACING = 2.0          # Khoảng cách spawn (world units)
RAY_SPAWN_BUFFER = 10            # Buffer overlap check (pixels)
```

**State Class:**
```python
class State:
    containers = []               # Danh sách trays
    undo_stack = []              # Undo history (20 levels)
    selected_trays = []          # Trays đang chọn
    selected_cells = []          # Cells đang chọn (paint mode)
    paint_mode = False           # Chế độ vẽ chi tiết
    current_layer = 1            # Layer hiện tại (1-5)
    layer_checkbox = [False] * 5 # Layer selection checkboxes

    # Rayline System
    layer_rays = {1:[], 2:[], 3:[], 4:[], 5:[]}  # Ray cho từng layer
    layer_ray_spawn_index = {1:0, 2:0, 3:0, 4:0, 5:0}  # Spawn index
    rayline_edit_mode = False    # Ray Editor modal state
    rayline_edit_layer = 1       # Layer đang edit ray
    rayline_temp_drawing = []    # Temporary drawing path
    rayline_is_drawing = False   # Mouse drag state
```

### 3. logic_core.py - Core Algorithms & Logic

**Container Class:**
Đại diện cho mỗi tray/khay puzzle
- Properties: rows, cols, cells, target, layer, position (x, y)
- Methods: draw_target(), draw_block()

**Các thuật toán chính:**

#### 1. `spawn_new_trays()`
Spawn tray mới theo rayline hoặc random
- Nếu layer có ray: spawn theo sequential trên ray
- Nếu không có ray: spawn random trong gameplay area
- Sử dụng weighted random selection từ spawn ratio table
- Hỗ trợ symmetry mode

#### 2. `generate_cluster_pattern()`
Tạo pattern màu sắc có clustering tự nhiên
- Sử dụng BFS để tìm vị trí đặt cluster màu
- Ưu tiên hình chữ nhật compact
- Cân bằng màu sắc giữa các trays

#### 3. `find_compact_cluster()`
Tìm vị trí đặt cluster màu theo hình chữ nhật compact
- Tìm kiếm vùng trống liên tục
- Tối ưu hóa tỷ lệ khung hình

#### 4. `sort_grid_data_optimized()`
Sắp xếp màu sắc theo tiling optimization
- Rectangle packing algorithm
- Giảm fragmentation

#### 5. `smart_optimize_orphans()`
Ghép đôi các màu lẻ giữa các khay
- Tìm cặp trays có màu lẻ giống nhau
- Swap để tạo nhóm đủ số lượng

#### 6. `fill_clustered_logic()`
Điền màu vào khay theo logic clustering
- Tính toán mismatch giữa target và block
- Fill theo clusters compact

#### 7. `shuffle_level()`
Xáo trộn level với tỷ lệ điều chỉnh được
- Cross-layer shuffle
- Preserve clustering pattern

#### 8. `fill_layers()`
Fill blocks cho selected layers (basic version)
- Tính demand dựa trên room available (global stats)
- Fill với clustering, tránh trùng màu target
- Có thể để trống ô nếu không tìm được slot phù hợp
- Sử dụng find_best_slot_for_clustering()

#### 9. `fill_layers_advance()` (NEW)
Fill blocks cho selected layers (advanced version với exact matching)
- **Phase 1**: Count exact demand per color trong layer
  - `layer_target_count = {color: count}` - đếm target colors
  - `layer_block_count = {color: count}` - đếm block colors hiện tại
  - `exact_demand = target - block` cho mỗi màu
- **Phase 2**: Fill với clustering (ideal)
  - Fill theo exact_demand, ưu tiên clustering
  - Tránh trùng màu với target position
  - Update exact_demand sau mỗi lần fill
- **Phase 3**: Find remaining empty slots và remaining demand
- **Phase 4**: Force fill exact demand
  - Build list màu cần fill (exact count)
  - Sort slots ưu tiên (prefer non-matching)
  - Fill chính xác từng màu vào slot thích hợp
  - Cho phép fill trùng target nếu cần (fallback)
- **Phase 5**: Verify color balance
  - Re-count blocks sau fill
  - Check: block_count == target_count cho mỗi màu
  - Message: `✓ exact match` hoặc `⚠ may need adjustment`
- **Đảm bảo**: Không có ô trống, số lượng màu chính xác 100%

#### 10. `find_best_color_for_slot()`
Helper function cho fill_layers_advance()
- Tìm màu tối ưu cho slot dựa trên strategy priority
- Respect constraints: max_same_color, max_types
- Balance color distribution

**Helper Functions:**
- `global_stats()`: Thống kê target/block colors toàn level
- `layout()`: Tính toán layout position cho các trays
- `save_undo()`/`undo()`: Undo/redo system (20 levels)
- `fill_n()`: Fill N blocks cùng màu vào selected trays
- `fill_same()`: Reset cells to match targets exactly
- `fix_color()`: Fix color issues in containers

### 4. logic_rayline.py - Rayline/Conveyor System

**Module mới** để xử lý toàn bộ logic rayline và spawn positioning.

**Chức năng chính:**

#### Coordinate Conversion
- `grid_to_world(gx, gy)`: Grid → Unity world coordinates
- `world_to_grid(wx, wy)`: World → Grid coordinates
- `world_to_screen_x/y()`: World → Pygame screen coordinates
- `screen_to_world_x/y()`: Screen → World coordinates
- `mouse_to_grid(mx, my)`: Mouse position → Grid cell

**Coordinate Systems:**
- **Grid**: 16x16 grid, (0,0) top-left, Y+ down
- **World**: Unity space, center at (0,0), range [-8, 8], Y+ up
- **Screen**: Pygame space, (0,0) top-left, Y+ down

#### Distance Calculation
- `calculate_min_distance_to_rayline()`: Khoảng cách từ point đến rayline
- Dùng để validate spawn positions (old method)

#### Spawn Zone Calculation (Old Method)
- `calculate_spawn_zones()`: Chia rayline thành zones
- Spawn xung quanh các zones (không dùng nữa)

#### Sequential Spawn on Ray (New Method)
- `calculate_sequential_spawn_position()`: Tính vị trí spawn tuần tự trên ray
  - Chia ray thành segments
  - Tính cumulative lengths
  - Interpolate vị trí spawn với spacing đều
  - Validate position (overlap, boundaries)
  - Return (screen_x, screen_y, world_x, world_y, next_index)

#### Validation Functions
- `is_valid_spawn_on_ray()`: Kiểm tra vị trí spawn ON ray
  - Không check distance from ray (vì spawn đúng trên ray)
  - Check overlap với containers khác (cùng layer)
  - Check boundaries (gameplay area)
- `check_rect_overlap()`: Kiểm tra 2 rectangles overlap

**Ray Spawn Logic:**
1. User vẽ ray trên grid 16x16 bằng Ray Editor
2. Ray được lưu theo layer (mỗi layer có ray riêng)
3. Khi spawn: tính vị trí tuần tự trên ray với spacing đều
4. Spawn index tăng dần, wrap around khi hết ray
5. Nếu vị trí bị chặn (overlap): thử vị trí tiếp theo

### 5. ui.py - User Interface Rendering

**Các hàm vẽ chính:**
- `draw_panels()`: Vẽ left/right panels
- `draw_stats()`: Hiển thị thống kê màu sắc (current/target)
- `draw_table()`: Vẽ bảng spawn ratio configuration
- `draw_right_panel()`: Layer controls, buttons, settings
- `draw_instruction()`: Keyboard shortcuts guide
- `draw_gameplay()`: Vẽ các trays với target và block colors
- `draw_rayline_modal()`: Vẽ Ray Editor modal

**Ray Editor Modal:**
- Grid 16x16 (640x640 pixels)
- Layer selector buttons (1-5)
- Drawing canvas với mouse drag
- Save/Clear/Close buttons
- Real-time preview của ray path
- Chỉ cho phép horizontal/vertical movement (không diagonal)

**Layout:**
- Left Panel (320px): Spawn ratio table, statistics
- Center Area: Gameplay (trays visualization + rayline preview)
- Right Panel (280px): Layer controls, action buttons, settings

### 6. logic_export.py - Unity Export System

**Chức năng:**
- `export_to_unity_json()`: Xuất level sang Unity JSON format
- `generate_meta_file()`: Tạo Unity .meta file với GUID
- Coordinate conversion: Pygame → Unity world space
- Layer depth calculation (Z-axis)
- Overlap detection và CoveredIds relationships

**Coordinate Conversion:**
- Pygame: (0,0) top-left, Y down
- Unity: Center screen = (0,0), Y up, Z = layer depth
- Formula:
  ```python
  ux = (x - WIDTH/2) / 100.0
  uy = -(y - HEIGHT/2) / 100.0
  uz = -(layer - 1)
  ```

---

## Luồng Hoạt Động Hệ Thống

```
START
  ↓
Pygame Init
  ↓
Main Loop
  ├─→ Draw Panels & UI
  │   ├── Left Panel: Ratio table, stats
  │   ├── Center: Gameplay + rayline preview
  │   ├── Right Panel: Layer controls, buttons
  │   └── Ray Editor Modal (if active)
  │
  ├─→ Event Handling
  │   ├── Mouse Motion
  │   │   └── Rayline drawing (if in edit mode)
  │   │
  │   ├── Mouse Clicks
  │   │   ├── Ray Modal: Layer selector, buttons, grid drawing
  │   │   ├── Left Panel: Edit spawn ratio table
  │   │   ├── Center: Select/paint trays & cells
  │   │   └── Right Panel: Layer switch, buttons
  │   │
  │   └── Keyboard Input
  │       ├── Space: Spawn trays (on ray if exists)
  │       ├── 1-6: Fill N blocks
  │       ├── P: Paint mode
  │       ├── R: Ray Editor
  │       └── Other shortcuts...
  │
  └─→ Update State → Redraw → Loop (60 FPS)
```

### Workflow Chi Tiết

#### 1. Setup Ray (Optional)
- Nhấn `R` → mở Ray Editor modal
- Chọn layer (1-5) để edit
- Drag trên grid để vẽ ray path
- Nhấn "Save" để lưu ray cho layer đó
- Mỗi layer có thể có ray riêng hoặc không có

#### 2. Spawn Trays
**Nếu layer có ray:**
- Nhấn `Space` → spawn tại vị trí tiếp theo trên ray
- Tự động spacing đều theo RAY_SPAWN_SPACING
- Spawn index tăng dần, wrap around khi hết chỗ

**Nếu layer không có ray:**
- Spawn random trong gameplay area (như cũ)

**Symmetry Mode:**
- Tạo cặp tray đối xứng màu
- Tự động generate cluster pattern thông minh

#### 3. Fill Blocks
- Chọn trays + nhấn số `1-6` → fill N blocks cùng màu
- Clustering logic: ưu tiên đặt cạnh nhau
- Tự động cân bằng màu sắc

#### 4. Paint Mode
- Nhấn `P` → chế độ vẽ chi tiết từng cell
- Số `0-9`: vẽ block color
- `Alt + 0-9`: vẽ target color
- `Shift + Click`: multi-select cells

#### 5. Sort & Optimize
- Button "Sort Blocks"
- Merge orphan colors giữa các trays
- Compact layout cho mỗi tray

#### 6. Export
- Nhấn `E` → xuất ra `save_level/Level_X.json`
- Tự động tạo .meta file cho Unity
- Format chuẩn Unity JSON

---

## Các Tính Năng Chính

### A. Rayline/Conveyor System (NEW)
**Ray Editor:**
- Modal UI với grid 16x16
- Vẽ ray bằng mouse drag (horizontal/vertical only)
- Multi-layer support: mỗi layer có ray riêng
- Save/Clear/Close controls

**Sequential Spawn on Ray:**
- Spawn containers tuần tự trên ray path
- Spacing đều nhau (configurable)
- Tự động wrap around khi hết chỗ
- Smart overlap detection
- Fallback: spawn vị trí tiếp theo nếu bị chặn

**Coordinate System:**
- Grid 16x16 ↔ Unity world [-8, 8]
- Automatic coordinate conversion
- Y-axis inversion handling

**Tuning Parameters:**
- `RAY_SPAWN_SPACING`: Khoảng cách spawn (default: 2.0 world units)
- `RAY_SPAWN_BUFFER`: Buffer overlap check (default: 10 pixels)

### B. Spawn System (Symmetry Support)
- Configurable spawn ratio table (size, weight, limit)
- Kích thước tray: 2x2, 2x3, 3x2, 3x3, 2x4, 4x2, 2x5, 5x2, etc.
- Symmetry Mode: tạo cặp tray với color mapping đối xứng
- Weight-based random spawning
- Smart spawn: ưu tiên ray nếu có, fallback random

### C. Multi-Layer System
- 5 layers độc lập (z-depth)
- Layer checkbox: áp dụng actions cho nhiều layers
- Mỗi layer có ray riêng biệt
- Overlap detection: trays ở layer cao che trays ở layer thấp
- Visual feedback cho layer selection

### D. Smart Color Generation
- **Cluster Pattern**: màu được nhóm thành các khối compact
- **Partition Algorithm**: chia số ô thành groups hợp lý (tránh lẻ 1 ô)
- **Global Balancing**: cân bằng màu sắc giữa các trays
- **Orphan Optimization**: ghép các màu lẻ (<2 blocks) giữa trays

### E. Fill Mechanisms
- **Fill Same (Green button)**: Điền target color vào empty cells
- **Fill N (1-6)**: Điền N blocks cùng màu vào tray đã chọn
- **Auto Fill (Cluster)**: Tự động điền theo mismatch với clustering
- **Fill Layers**: Điền cho selected layers với clustering, có thể để trống ô nếu không tìm được slot phù hợp
- **Fill Layer Advance (NEW)**: Phiên bản nâng cấp của Fill Layers
  - Đảm bảo 100% số lượng block mỗi màu = số lượng target mỗi màu
  - Không để trống ô nào (bắt buộc fill hết)
  - Ưu tiên clustering và tránh trùng màu với target position
  - Smart fallback: cho phép fill trùng target nếu cần để đảm bảo exact match
  - Message: `✓ exact match` khi thành công
- **Fill All**: Điền toàn bộ level
- **Fix Color**: Sửa color issues

### F. Manipulation Tools
- **Sort Blocks**: Sắp xếp lại màu theo compact tiling
- **Shuffle**: Xáo trộn blocks (có ratio điều chỉnh 0-100%)
- **Swap (T)**: Hoán đổi nội dung 2 trays
- **Delete (D)**: Xóa selected trays
- **Undo (U)**: 20-level undo stack
- **Multi-select**: Shift + Click để chọn nhiều trays/cells

### G. Paint Mode
- Chỉnh sửa từng cell cụ thể
- Shift + Click: multi-select cells
- Vẽ target hoặc block color (Alt modifier)
- Visual feedback cho selected cells

### H. Configuration Parameters
- **Tray Color Variety (+/-)**: 1-10 colors (số loại màu trong tray)
- **Max Same Color (,/.)**: 1-10 (số lượng tối đa cùng màu)
- **Shuffle Ratio**: 0-100% (tỷ lệ shuffle cross-layer)
- **Symmetry Mode**: Toggle spawn đối xứng

### I. Statistics & Visualization
- Real-time color statistics (current vs target)
- Visual color distribution bars
- Spawn ratio table với editable weights
- Layer-wise tray counting

---

## Unity Export Format

### JSON Structure
```json
{
  "Version": 10,
  "MaxInstanceId": <max_id>,
  "CellBlocks": [         // Các khay/trays
    {
      "ID": <id>,
      "Size": "cols;rows",
      "Position": "x;y;z",  // Unity world coordinates
      "CoveredIds": [...],  // IDs của trays bị che bởi tray này
      "Color": 0,
      "Mystery": false
    }
  ],
  "CellSlots": [          // Các ô target
    {
      "ID": <id>,
      "CellBlockId": <parent_tray_id>,
      "Color": <target_color>
    }
  ],
  "BlockColors": [        // Các block đã điền
    {
      "ID": <id>,
      "OwnerID": <cell_slot_id>,
      "Color": <block_color>
    }
  ],
  "ConveyorSegments": [], // Empty (không dùng conveyor)
  "ConveyorSlots": []
}
```

### Ví Dụ Export
File được lưu tại: `save_level/Level_X.json` (X = số level tự động tăng)

**CoveredIds Logic:**
- Tray A che Tray B nếu:
  - A ở layer cao hơn B
  - Bounding box của A overlap với B
- CoveredIds của A chứa ID của B

---

## Thuật Toán & Data Structures

### Algorithms Sử Dụng
1. **BFS (Breadth-First Search)**: Find compact clusters
2. **Greedy Partitioning**: Color distribution
3. **Tiling Optimization**: Rectangle packing
4. **Graph Matching**: Orphan color pairing
5. **Weighted Random Selection**: Spawn system
6. **Linear Interpolation**: Sequential spawn on ray
7. **Cumulative Distance**: Ray path segmentation

### Data Structures
- **State Class**: Singleton pattern cho global state
- **Container Class**: OOP representation của trays
- **Grid Matrix**: 2D list cho cells
- **Undo Stack**: List-based history (LIFO, max 20 levels)
- **Ray Path**: List of (grid_x, grid_y) tuples
- **Spawn Index Dict**: {layer_id: spawn_index}

---

## Dependencies

### Core Dependencies
- **pygame**: Game framework cho rendering và event handling
- **json**: Xuất/nhập level data
- **os**: File system operations
- **uuid**: Generate GUID cho Unity meta files
- **time**: Timestamp cho meta files
- **random**: Random generation algorithms
- **math**: Geometric calculations (distance, interpolation)

### Python Version
- Python 3.12.xx (required)
- No external dependencies ngoài pygame!

---

## Hướng Dẫn Sử Dụng

### Khởi động
```bash
python main.py
```

### Workflow Cơ Bản

#### Workflow với Rayline (Recommended)
1. **Setup Ray Path**:
   - Nhấn `R` để mở Ray Editor
   - Chọn layer muốn edit (1-5)
   - Drag trên grid để vẽ đường ray
   - Nhấn "Save" để lưu ray

2. **Spawn Trays on Ray**:
   - Switch về layer đã có ray
   - Nhấn `Space` nhiều lần
   - Containers sẽ spawn tuần tự dọc theo ray

3. **Fill Colors**:
   - Chọn trays (click)
   - Nhấn 1-6 để fill blocks
   - Hoặc dùng "Auto Fill" button

4. **Optimize**: Nhấn "Sort Blocks" để tối ưu

5. **Fine-tune**:
   - Nhấn `P` vào paint mode
   - Vẽ chi tiết từng cell

6. **Export**: Nhấn `E` để xuất Unity JSON

#### Workflow không dùng Rayline (Classic)
1. **Setup Spawn Table**: Chỉnh sửa left panel (size, weight, limit)
2. **Spawn Trays**: Nhấn `Space` nhiều lần để tạo trays random
3. **Fill Colors**: Chọn trays + nhấn 1-6 hoặc Auto Fill
4. **Optimize**: Sort Blocks
5. **Fine-tune**: Paint mode
6. **Export**: Nhấn `E`

### Tips & Tricks
- **Rayline Workflow**: Vẽ ray trước khi spawn để có layout đẹp và có tổ chức
- **Ray Spacing**: Điều chỉnh `RAY_SPAWN_SPACING` trong config.py nếu cần
- **Multi-layer Rays**: Vẽ ray khác nhau cho từng layer để tạo depth
- Sử dụng Symmetry Mode để tạo level cân đối
- Adjust Tray Color Variety để điều chỉnh độ khó
- Shuffle Ratio thấp (10-30%) cho shuffle nhẹ
- Sort Blocks trước khi export để tối ưu
- Dùng Undo (U) khi thử nghiệm
- Ray Editor: chỉ di chuyển horizontal/vertical, không diagonal

---

## Tính Năng Nổi Bật

### 1. Rayline/Conveyor System (NEW!)
- **Modal Editor**: UI trực quan để vẽ ray path
- **Sequential Spawn**: Container spawn tuần tự, spacing đều
- **Multi-layer Support**: Mỗi layer có ray độc lập
- **Smart Validation**: Automatic overlap detection
- **Coordinate Conversion**: Seamless grid ↔ world ↔ screen

### 2. Smart Clustering Algorithm
- Tự động nhóm màu thành clusters compact
- Giảm fragmentation
- Tối ưu cho gameplay (dễ visualize)

### 3. Orphan Optimization
- Tự động detect màu lẻ (<2 blocks)
- Smart pairing giữa các trays
- Giảm waste, tăng solvability

### 4. Multi-Layer Support
- Độc lập 5 layers
- Overlap detection
- Visual depth feedback
- Per-layer ray paths

### 5. Symmetry Mode
- Tạo cặp tray với color mapping
- Tăng tính thẩm mỹ
- Cân bằng difficulty

### 6. Undo/Redo System
- 20-level deep history
- Fast state restoration
- No data loss

### 7. Unity Integration
- Seamless export
- Coordinate conversion
- Auto GUID generation

---

## Kiến Trúc Code

### Design Patterns
- **Singleton**: State class (global config)
- **MVC-like**: Separation of logic/UI/export
- **Event-driven**: Pygame event loop
- **Immutable State**: Undo system sử dụng deep copy
- **Module Separation**: Ray logic tách riêng module

### Code Organization
```
main.py          → Controller (event handling, game loop)
ui.py            → View (rendering, ray editor modal)
logic_core.py    → Model (business logic, algorithms)
logic_rayline.py → Service (ray system, coordinate conversion)
logic_export.py  → Service (export utility)
config.py        → Config (constants, state, UI layout)
```

### Best Practices
- Pure functions trong algorithms
- Minimal global state
- Clear separation of concerns
- Docstrings cho các hàm phức tạp
- Coordinate conversion centralized trong logic_rayline

---

## Ray System Technical Details

### Grid to World Conversion
```
Grid 16x16:
  - Index: 0 to 15
  - Center: 7.5
  - (0,0) = top-left
  - Y+ down

World [-8, 8]:
  - Center: (0, 0)
  - Range: -8 to +8
  - Y+ up (inverted)

Formula:
  world_x = (grid_x - 7.5) * 1.0
  world_y = (7.5 - grid_y) * 1.0  // Y inverted
```

### Sequential Spawn Algorithm
```
1. Convert ray points to world coords
2. Calculate cumulative segment lengths
3. For each spawn:
   a. target_distance = spawn_index * spacing
   b. Find segment containing target_distance
   c. Interpolate position on segment
   d. Validate position (overlap, boundaries)
   e. Return position or try next index
4. Wrap around when reaching end of ray
```

### Validation Rules (On Ray)
```
KHÔNG CHECK:
  - Distance from rayline (spawn ON ray)

CHECK:
  - Overlap với containers khác (same layer)
    - Buffer: RAY_SPAWN_BUFFER pixels
  - Boundaries (gameplay area)
    - x: MARGIN_X to PANEL_RIGHT_X
    - y: MARGIN_Y to HEIGHT-50
```

---

## Fill Layer Advance Technical Details

### Algorithm Overview
Fill Layer Advance sử dụng thuật toán 5-phase để đảm bảo exact color matching:

### Phase 1: Count Exact Demand
```python
# Đếm target colors trong layer
layer_target_count = {}
for container in selected_layers:
    for cell in container.target:
        layer_target_count[color] += 1

# Đếm block colors hiện tại
layer_block_count = {}
for container in selected_layers:
    for cell in container.cells:
        if cell is not None:
            layer_block_count[color] += 1

# Tính exact demand
exact_demand = {}
for color, target_count in layer_target_count.items():
    current_count = layer_block_count.get(color, 0)
    need = target_count - current_count
    if need > 0:
        exact_demand[color] = need
```

### Phase 2: Fill with Clustering (Ideal)
```python
# Fill theo exact_demand, ưu tiên clustering
for color, count in sorted(exact_demand.items()):
    for _ in range(count):
        slot = find_best_slot_for_clustering(containers, color)
        if slot and slot.target_color != color:
            fill(slot, color)
            exact_demand[color] -= 1
```

**Clustering Priority:**
1. Slots có adjacent cùng màu (clustering)
2. Slots không có adjacent
3. Skip nếu target_color == color (tránh trùng)

### Phase 3: Find Remaining
```python
# Tìm ô trống còn lại
empty_slots = []
for container in containers:
    for cell in container:
        if cell is None:
            empty_slots.append(cell)

# Lọc exact_demand còn lại
exact_demand = {color: count for color, count in exact_demand.items() if count > 0}
```

### Phase 4: Force Fill Exact Demand
```python
# Build list màu cần fill (exact count)
colors_to_fill = []
for color, count in exact_demand.items():
    colors_to_fill.extend([color] * count)

# Sort slots by priority
empty_slots_sorted = []
for slot in empty_slots:
    # Priority 0: slots có thể fill không trùng target
    # Priority 1: slots khác
    priority = 0 if slot.can_fill_without_match(colors_to_fill) else 1
    empty_slots_sorted.append((priority, slot))

empty_slots_sorted.sort()

# Fill từng màu vào slot thích hợp
for color in colors_to_fill:
    # Try find slot where color != target (ideal)
    best_slot = find_slot_not_matching(empty_slots_sorted, color)

    # Fallback: use any slot (allow matching)
    if not best_slot:
        best_slot = empty_slots_sorted[0]

    fill(best_slot, color)
    remove_from_list(empty_slots_sorted, best_slot)
```

### Phase 5: Verify Balance
```python
# Re-count blocks sau fill
final_block_count = {}
for container in containers:
    for cell in container.cells:
        if cell is not None:
            final_block_count[color] += 1

# Check balance
is_balanced = True
for color, target_count in layer_target_count.items():
    block_count = final_block_count.get(color, 0)
    if target_count != block_count:
        is_balanced = False
        break

# Message
if is_balanced:
    "Fill Advance: X filled (✓ exact match)"
else:
    "Fill Advance: X filled (⚠ may need adjustment)"
```

### Guarantees
```
✓ Số lượng block mỗi màu = Số lượng target mỗi màu (100%)
✓ Không có ô trống (fill hết)
✓ Ưu tiên clustering (adjacent colors)
✓ Ưu tiên tránh trùng target position
✓ Fallback: cho phép trùng target nếu cần để đảm bảo exact match
```

### Example
```
BEFORE:
Target: Blue=15, Red=20, Green=10
Blocks: Blue=12, Red=18, Green=8
Empty slots: 7

AFTER Fill Layer Advance:
Blocks: Blue=15, Red=20, Green=10
Empty slots: 0
✓ exact match
```

---

## Kết Luận

**CubeBot - Puzzle King** là một level editor chuyên nghiệp với:

✅ Giao diện trực quan với Pygame
✅ Hệ thống Rayline/Conveyor hoàn chỉnh
✅ Sequential spawn với spacing tự động
✅ Multi-layer ray system độc lập
✅ Fill Layer Advance với exact color matching (NEW v2.1)
✅ Thuật toán thông minh: clustering, balancing, optimization
✅ Export seamless sang Unity
✅ Hỗ trợ symmetry, undo/redo
✅ Configurable spawning system
✅ Paint mode cho fine-tuning chi tiết

Đây là công cụ production-ready để thiết kế puzzle levels một cách hiệu quả, khoa học và có tổ chức.

---

## Files Quan Trọng

- `main.py:1` - Entry point, game loop
- `logic_core.py:1` - Core algorithms
- `logic_rayline.py:1` - Ray system (NEW)
- `logic_export.py:1` - Unity export
- `config.py:1` - Configuration, state management
- `ui.py:1` - UI rendering, ray editor modal
- `save_level/Level_*.json` - Exported levels

---

## Changelog

### Version 2.1 (2026-01-06)
- **NEW**: Fill Layer Advance - phiên bản nâng cấp của Fill Layers
  - Đảm bảo 100% số lượng block mỗi màu = số lượng target mỗi màu
  - Không để trống ô nào (bắt buộc fill hết)
  - 5-phase algorithm với exact color matching
  - Smart fallback strategies
  - Verification và balance checking
- **NEW**: find_best_color_for_slot() helper function
- **NEW**: UI button "Fill Layer Advance" (màu cam)
- **FIXED**: Vấn đề màu thừa/thiếu khi fill layers
- **IMPROVED**: Fill mechanisms documentation

### Version 2.0 (2026-01-06)
- **NEW**: Rayline/Conveyor System với Ray Editor modal
- **NEW**: Sequential spawn on ray path
- **NEW**: Multi-layer ray support (mỗi layer có ray riêng)
- **NEW**: logic_rayline.py module
- **IMPROVED**: Spawn system với ray fallback
- **IMPROVED**: Coordinate conversion system
- **IMPROVED**: UI layout với Ray Editor

### Version 1.0 (2025-12-30)
- Initial release
- Basic spawn, fill, sort, export
- Multi-layer support
- Symmetry mode
- Paint mode

---

**Phiên bản tài liệu:** 2.1
**Ngày cập nhật:** 2026-01-06
**Người tạo:** CubeBot Development Team
