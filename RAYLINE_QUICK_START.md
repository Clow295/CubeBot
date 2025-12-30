# RAYLINE/CONVEYOR SYSTEM - QUICK START GUIDE

## 🚀 What is Rayline?

**Rayline** (hay Conveyor) là một tính năng mới cho phép bạn:
- Vẽ một đường path (rayline) trên grid 10x10
- Spawn containers tự động phân bố xung quanh rayline
- Export rayline sang Unity dưới dạng ConveyorSegments

## 🎮 How to Use

### 1. Mở Rayline Editor
```
Nhấn phím R
```
→ Một modal window sẽ hiện lên với grid 10x10

### 2. Vẽ Rayline Path
```
1. Click vào ô đầu tiên
2. Giữ chuột và kéo (chỉ được di chuyển ngang hoặc dọc)
3. Thả chuột để kết thúc
```
→ Path của bạn sẽ hiện màu cyan

### 3. Save Rayline
```
Click nút "Save"
```
→ Status hiển thị "Rayline ENABLED"

### 4. Spawn Containers Around Rayline
```
Đóng modal (nút "Close" hoặc nhấn R lại)
Nhấn Space để spawn containers
```
→ Containers sẽ spawn xung quanh rayline, cách rayline ít nhất 2 units

### 5. Export to Unity
```
Nhấn E để export
```
→ File `save_level/Level_0.json` sẽ chứa ConveyorSegments

## 🎨 Rayline Editor Controls

| Action | How to |
|--------|--------|
| Vẽ path | Click & drag trên grid |
| Save rayline | Click "Save" button |
| Xóa rayline | Click "Clear" button |
| Đóng editor | Click "Close" hoặc nhấn R |

## 🔧 Advanced Usage

### Clear Rayline
```
1. Nhấn R để mở editor
2. Click "Clear"
3. Click "Save"
→ Rayline bị xóa và disabled
```

### Spawn với Symmetry Mode + Rayline
```
1. Bật Symmetry Mode (nút "Spawn Symmetry")
2. Spawn với rayline enabled
→ Cả master và slave đều spawn quanh rayline
```

## 📄 Export Format

Khi rayline enabled, JSON export sẽ có:

```json
{
  "ConveyorSegments": [
    {"Position": "-3;0"},
    {"Position": "-2;0"},
    {"Position": "-1;0"},
    {"Position": "0;0"}
  ],
  ...
}
```

Khi rayline disabled, ConveyorSegments sẽ là array rỗng `[]`.

## ❓ FAQs

**Q: Rayline có bắt buộc không?**
A: Không! Hoàn toàn optional. Khi không có rayline, spawn theo logic cũ.

**Q: Tôi có thể vẽ diagonal không?**
A: Không, chỉ horizontal hoặc vertical. Vẽ theo steps.

**Q: Spawn không hoạt động với rayline?**
A: Tool sẽ tự động fallback về spawn logic cũ nếu không tìm được vị trí hợp lệ.

**Q: Rayline có bị ảnh hưởng bởi Undo không?**
A: Không. Rayline là global setup, không nằm trong undo stack.

**Q: Làm sao biết rayline đang enabled?**
A: Xem instruction panel bên phải - "R:Rayline Editor" sẽ màu cyan khi enabled.

## 🐛 Troubleshooting

**Problem:** Containers không spawn quanh rayline
- **Solution:** Check rayline có được save chưa (status hiện "ENABLED")

**Problem:** Modal không mở
- **Solution:** Đảm bảo không đang ở Paint Mode (nhấn P để thoát)

**Problem:** Không export được ConveyorSegments
- **Solution:** Rayline phải được save trước khi export

## 📚 More Info

- Chi tiết thiết kế: `RAYLINE_DESIGN.md`
- Implementation summary: `RAYLINE_IMPLEMENTATION_SUMMARY.md`
- Source code: `logic_rayline.py`

---

**Happy Rayline Drawing!** 🎨✨
