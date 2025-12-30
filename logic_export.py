import os, json, uuid, time, pygame
from config import *
from logic_core import state

# Tên folder lưu trữ
SAVE_FOLDER = "save_level"


def get_tray_rect(ct):
    return pygame.Rect(ct.x, ct.y, ct.cols * CELL_SIZE, ct.rows * CELL_SIZE)


def check_tray_overlap(rect1, rect2):
    return rect1.colliderect(rect2)


def generate_meta_file(full_path_filename):
    """
    Tạo file .meta tại đường dẫn cụ thể (trong folder save_level)
    """
    meta_filename = full_path_filename + ".meta"
    guid = uuid.uuid4().hex

    # Thử đọc GUID cũ nếu file meta đã tồn tại
    if os.path.exists(meta_filename):
        try:
            with open(meta_filename, "r") as f:
                for line in f:
                    if "guid:" in line:
                        guid = line.split(":")[1].strip()
                        break
        except:
            pass

    content = f"fileFormatVersion: 2\nguid: {guid}\ntimeCreated: {int(time.time())}\nlicenseType: Free\nTextScriptImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"

    try:
        with open(meta_filename, "w") as f:
            f.write(content)
    except Exception as e:
        print(f"Meta Error: {e}")


def export_to_unity_json(filename="Level_0.json"):
    # --- BƯỚC 1: KIỂM TRA VÀ TẠO FOLDER ---
    if not os.path.exists(SAVE_FOLDER):
        try:
            os.makedirs(SAVE_FOLDER)
        except OSError as e:
            print(f"Error creating directory: {e}")
            state.last_action_message = "Dir Error"
            return

    # Tạo đường dẫn đầy đủ: save_level/export_level.json
    full_path = os.path.join(SAVE_FOLDER, filename)

    # --- BƯỚC 2: SINH DỮ LIỆU (LOGIC CŨ) ---
    id_counter = [0]

    def gen_id():
        id_counter[0] += 1
        return id_counter[0]

    ex_slots, ex_colors, temp = [], [], []

    # --- NEW: Generate ConveyorSegments ---
    conveyor_segments = []
    if state.rayline_enabled and state.rayline_points:
        from logic_rayline import grid_to_world
        for gx, gy in state.rayline_points:
            wx, wy = grid_to_world(gx, gy)
            conveyor_segments.append({
                "Position": f"{int(wx)};{int(wy)}"
            })

    for ct in state.containers:
        tid = gen_id()
        ux = ((ct.x - WIDTH / 2) / 100.0) * 2
        uy = (-(ct.y - HEIGHT / 2) / 100.0) * 2
        uz = -(ct.layer - 1) * 1.0

        data = {
            "Size": f"{ct.cols};{ct.rows}",
            "Position": f"{ux:.3f};{uy:.3f};{int(uz)}",
            "CoveredIds": [],
            "SegmentIds": [],
            "Color": 0,
            "Mystery": False,
            "ID": tid
        }
        temp.append({"data": data, "ref": ct, "rect": get_tray_rect(ct)})

        for r in range(ct.rows):
            for c in range(ct.cols):
                sid = gen_id()
                col = ct.target[r][c] if ct.target[r][c] is not None else 0
                ex_slots.append({"CellBlockId": tid, "Color": col, "ID": sid})
                if ct.cells and ct.cells[r][c] is not None:
                    bid = gen_id()
                    ex_colors.append({"Color": ct.cells[r][c], "OwnerID": sid, "ID": bid})

    for a in temp:
        for b in temp:
            if a == b: continue
            if a["ref"].layer > b["ref"].layer and check_tray_overlap(a["rect"], b["rect"]):
                a["data"]["CoveredIds"].append(b["data"]["ID"])

    final = {
        "Version": 10,
        "MaxInstanceId": id_counter[0],
        "ZoneModifier": None,
        "ConveyorSpeed": 1.0,
        "AmountSlots": 16,
        "AmountArrows": 8,
        "ArrowsOffset": 0.5,
        "ReverseDirection": False,
        "ConveyorSegments": conveyor_segments,  # NEW: Rayline data
        "ConveyorSlots": [],
        "CellBlocks": [t["data"] for t in temp],
        "CellSlots": ex_slots,
        "BlockColors": ex_colors,
        "BlockMystery": [],
        "Reverser": None
    }

    # --- BƯỚC 3: GHI FILE VÀO FOLDER ---
    try:
        with open(full_path, "w") as f:
            json.dump(final, f, separators=(',', ':'))

        # Gọi hàm tạo meta với đường dẫn đầy đủ
        generate_meta_file(full_path)

        state.last_action_message = f"Saved to {SAVE_FOLDER}/"
        print(f"Exported successfully to: {full_path}")
    except Exception as e:
        print(e)
        state.last_action_message = "Export Failed"