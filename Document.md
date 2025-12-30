# CubeBot - Puzzle King Documentation

## Tổng Quan Dự Án

**CubeBot - Puzzle King** là một công cụ chuyên nghiệp để thiết kế và tạo level cho game puzzle kiểu Color Cube Match.

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
│   ├── Level_0.json       # File level Unity format
│   └── Level_0.json.meta  # Unity meta file
├── .gitignore             # Git ignore configuration
├── README.md              # Documentation
├── config.py              # File cấu hình chính
├── logic_core.py          # Core logic và thuật toán
├── logic_export.py        # Logic xuất file Unity
├── main.py                # Entry point của ứng dụng
└── ui.py                  # UI rendering
```

---

## Các Module Chính

### 1. main.py - Entry Point & Game Loop
**Chức năng:**
- Khởi tạo Pygame window (1600x900)
- Game loop chính với event handling
- Xử lý input: mouse clicks, keyboard shortcuts
- Điều phối giữa các module UI và Logic

**Keyboard Shortcuts:**
- `Space`: Spawn new trays
- `1-6`: Fill N blocks cùng màu
- `P`: Toggle paint mode
- `0-9`: Paint blocks (Alt + 0-9 để paint targets)
- `T`: Swap nội dung 2 trays
- `S`: Shuffle level
- `U`: Undo
- `D`: Delete selected trays
- `E`: Export to Unity JSON
- `+/-`: Tăng/giảm Tray Color Variety
- `,/.`: Tăng/giảm Max Same Color

### 2. config.py - Configuration & Constants
**Chứa:**
- Constants: kích thước màn hình (WIDTH=1600, HEIGHT=900)
- Bảng màu: 10 màu chuẩn (Blue, Cyan, Green, Skin, Magenta, Orange, Purple, Red, White, Yellow)
- Class State: quản lý trạng thái toàn cục của ứng dụng
- UI layout positions và button rectangles
- Cấu hình spawn ratio table

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

### 3. logic_core.py - Core Algorithms & Logic

**Container Class:**
Đại diện cho mỗi tray/khay puzzle
- Properties: rows, cols, cells, target, layer, position
- Methods: draw_target(), draw_block()

**Các thuật toán chính:**

#### 1. `generate_cluster_pattern()`
Tạo pattern màu sắc có clustering tự nhiên
- Sử dụng BFS để tìm vị trí đặt cluster màu
- Ưu tiên hình chữ nhật compact
- Cân bằng màu sắc giữa các trays

#### 2. `find_compact_cluster()`
Tìm vị trí đặt cluster màu theo hình chữ nhật compact
- Tìm kiếm vùng trống liên tục
- Tối ưu hóa tỷ lệ khung hình

#### 3. `sort_grid_data_optimized()`
Sắp xếp màu sắc theo tiling optimization
- Rectangle packing algorithm
- Giảm fragmentation

#### 4. `smart_optimize_orphans()`
Ghép đôi các màu lẻ giữa các khay
- Tìm cặp trays có màu lẻ giống nhau
- Swap để tạo nhóm đủ số lượng

#### 5. `fill_clustered_logic()`
Điền màu vào khay theo logic clustering
- Tính toán mismatch giữa target và block
- Fill theo clusters compact

#### 6. `shuffle_level()`
Xáo trộn level với tỷ lệ điều chỉnh được
- Cross-layer shuffle
- Preserve clustering pattern

**Helper Functions:**
- `global_stats()`: Thống kê target/block colors toàn level
- `layout()`: Tính toán layout position cho các trays
- `save_undo()`/`undo()`: Undo/redo system (20 levels)

### 4. ui.py - User Interface Rendering

**Các hàm vẽ chính:**
- `draw_panels()`: Vẽ left/right panels
- `draw_stats()`: Hiển thị thống kê màu sắc (current/target)
- `draw_table()`: Vẽ bảng spawn ratio configuration
- `draw_right_panel()`: Layer controls, buttons, settings
- `draw_instruction()`: Keyboard shortcuts guide
- `draw_gameplay()`: Vẽ các trays với target và block colors

**Layout:**
- Left Panel (320px): Spawn ratio table, statistics
- Center Area: Gameplay (trays visualization)
- Right Panel (280px): Layer controls, action buttons, settings

### 5. logic_export.py - Unity Export System

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
  ├─→ Event Handling
  │   ├── Mouse Clicks
  │   │   ├── LEFT PANEL: Edit spawn ratio table
  │   │   ├── CENTER: Select/paint trays & cells
  │   │   └── RIGHT PANEL: Layer switch, buttons
  │   │
  │   └── Keyboard Input (shortcuts)
  │
  └─→ Update State → Redraw → Loop
```

### Workflow Chi Tiết

#### 1. Spawn Trays
- Nhấn `Space` → tạo tray mới theo ratio config
- Nếu Symmetry Mode ON: tạo cặp tray đối xứng màu
- Tự động generate cluster pattern thông minh

#### 2. Fill Blocks
- Chọn trays + nhấn số `1-6` → fill N blocks cùng màu
- Clustering logic: ưu tiên đặt cạnh nhau
- Tự động cân bằng màu sắc

#### 3. Paint Mode
- Nhấn `P` → chế độ vẽ chi tiết từng cell
- Số `0-9`: vẽ block color
- `Alt + 0-9`: vẽ target color
- `Shift + Click`: multi-select cells

#### 4. Sort & Optimize
- Button "Sort Blocks"
- Merge orphan colors giữa các trays
- Compact layout cho mỗi tray

#### 5. Export
- Nhấn `E` → xuất ra `save_level/Level_0.json`
- Tự động tạo .meta file cho Unity
- Format chuẩn Unity JSON

---

## Các Tính Năng Chính

### A. Spawn System (Symmetry Support)
- Configurable spawn ratio table (size, weight, limit)
- Kích thước tray: 2x2, 2x3, 3x2, 3x3, 2x4, 4x2, 2x5, 5x2, etc.
- Symmetry Mode: tạo cặp tray với color mapping đối xứng
- Weight-based random spawning

### B. Multi-Layer System
- 5 layers độc lập (z-depth)
- Layer checkbox: áp dụng actions cho nhiều layers
- Overlap detection: trays ở layer cao che trays ở layer thấp
- Visual feedback cho layer selection

### C. Smart Color Generation
- **Cluster Pattern**: màu được nhóm thành các khối compact
- **Partition Algorithm**: chia số ô thành groups hợp lý (tránh lẻ 1 ô)
- **Global Balancing**: cân bằng màu sắc giữa các trays
- **Orphan Optimization**: ghép các màu lẻ (<2 blocks) giữa trays

### D. Fill Mechanisms
- **Fill Same (Green button)**: Điền target color vào empty cells
- **Fill N (1-6)**: Điền N blocks cùng màu vào tray đã chọn
- **Auto Fill (Cluster)**: Tự động điền theo mismatch với clustering
- **Fill Layers**: Điền cho selected layers
- **Fill All**: Điền toàn bộ level

### E. Manipulation Tools
- **Sort Blocks**: Sắp xếp lại màu theo compact tiling
- **Shuffle**: Xáo trộn blocks (có ratio điều chỉnh 0-100%)
- **Swap (T)**: Hoán đổi nội dung 2 trays
- **Delete (D)**: Xóa selected trays
- **Undo (U)**: 20-level undo stack
- **Multi-select**: Shift + Click để chọn nhiều trays/cells

### F. Paint Mode
- Chỉnh sửa từng cell cụ thể
- Shift + Click: multi-select cells
- Vẽ target hoặc block color (Alt modifier)
- Visual feedback cho selected cells

### G. Configuration Parameters
- **Tray Color Variety (+/-)**: 1-10 colors (số loại màu trong tray)
- **Max Same Color (,/.)**: 1-10 (số lượng tối đa cùng màu)
- **Shuffle Ratio**: 0-100% (tỷ lệ shuffle cross-layer)
- **Symmetry Mode**: Toggle spawn đối xứng

### H. Statistics & Visualization
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
File được lưu tại: `save_level/Level_0.json`

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

### Data Structures
- **State Class**: Singleton pattern cho global state
- **Container Class**: OOP representation của trays
- **Grid Matrix**: 2D list cho cells
- **Undo Stack**: List-based history (LIFO)

---

## Dependencies

### Core Dependencies
- **pygame**: Game framework cho rendering và event handling
- **json**: Xuất/nhập level data
- **os**: File system operations
- **uuid**: Generate GUID cho Unity meta files
- **time**: Timestamp cho meta files
- **random**: Random generation algorithms

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
1. **Setup Spawn Table**: Chỉnh sửa left panel (size, weight, limit)
2. **Spawn Trays**: Nhấn Space nhiều lần để tạo trays
3. **Fill Colors**:
   - Chọn trays (click)
   - Nhấn 1-6 để fill blocks
   - Hoặc dùng "Auto Fill" button
4. **Optimize**: Nhấn "Sort Blocks" để tối ưu
5. **Fine-tune**:
   - Nhấn P vào paint mode
   - Vẽ chi tiết từng cell
6. **Export**: Nhấn E để xuất Unity JSON

### Tips & Tricks
- Sử dụng Symmetry Mode để tạo level cân đối
- Adjust Tray Color Variety để điều chỉnh độ khó
- Shuffle Ratio thấp (10-30%) cho shuffle nhẹ
- Sort Blocks trước khi export để tối ưu
- Dùng Undo (U) khi thử nghiệm

---

## Tính Năng Nổi Bật

### 1. Smart Clustering Algorithm
- Tự động nhóm màu thành clusters compact
- Giảm fragmentation
- Tối ưu cho gameplay (dễ visualize)

### 2. Orphan Optimization
- Tự động detect màu lẻ (<2 blocks)
- Smart pairing giữa các trays
- Giảm waste, tăng solvability

### 3. Multi-Layer Support
- Độc lập 5 layers
- Overlap detection
- Visual depth feedback

### 4. Symmetry Mode
- Tạo cặp tray với color mapping
- Tăng tính thẩm mỹ
- Cân bằng difficulty

### 5. Undo/Redo System
- 20-level deep history
- Fast state restoration
- No data loss

### 6. Unity Integration
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

### Code Organization
```
main.py        → Controller (event handling, game loop)
ui.py          → View (rendering)
logic_core.py  → Model (business logic, algorithms)
logic_export.py → Service (export utility)
config.py      → Config (constants, state)
```

### Best Practices
- Pure functions trong algorithms
- Minimal global state
- Clear separation of concerns
- Docstrings cho các hàm phức tạp

---

## Kết Luận

**CubeBot - Puzzle King** là một level editor chuyên nghiệp với:

✅ Giao diện trực quan với Pygame
✅ Thuật toán thông minh: clustering, balancing, optimization
✅ Export seamless sang Unity
✅ Hỗ trợ multi-layer, symmetry, undo/redo
✅ Configurable spawning system
✅ Paint mode cho fine-tuning chi tiết

Đây là công cụ production-ready để thiết kế puzzle levels một cách hiệu quả và khoa học.

---

## Files Quan Trọng

- `main.py:1` - Entry point
- `logic_core.py:1` - Core algorithms (553 lines)
- `config.py:1` - Configuration
- `logic_export.py:1` - Unity export
- `save_level/Level_0.json` - Example exported level

---

**Phiên bản tài liệu:** 1.0
**Ngày cập nhật:** 2025-12-30
**Người tạo:** CubeBot Development Team
