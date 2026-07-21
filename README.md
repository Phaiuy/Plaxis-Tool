# Plaxis-Tool — Material Set Selector (2D / 3D)

Công cụ chọn đối tượng theo **Material set (Identification)** cho PLAXIS Input,
dùng chung cho cả **PLAXIS 2D** và **PLAXIS 3D** thông qua Remote Scripting
(`plxscripting`).

## Chức năng

1. **Đang chọn sẵn đối tượng** khi chạy tool → hiện bảng các *Material set
   (Identification)* của riêng những đối tượng đang chọn (kèm số lượng đối
   tượng theo từng material set).
2. **Không chọn đối tượng nào** khi chạy tool → hiện bảng **toàn bộ** Material
   set (Identification) đang có trong mô hình.
3. Chọn một hoặc nhiều dòng material set trong bảng rồi bấm **Select objects**
   → tool sẽ chọn (highlight) toàn bộ đối tượng trong mô hình có material set
   tương ứng. Đây chính là mục đích *select đối tượng theo material set*.

Các loại đối tượng được quét: soil volumes, plates, beams, geogrids, embedded
beams / rows, anchors (node-to-node, fixed-end), interfaces.

## Yêu cầu

- PLAXIS 2D hoặc 3D có Remote Scripting server.
- Python 3 + gói `plxscripting`:

  ```bash
  pip install -r requirements.txt
  ```

## Chuẩn bị trong PLAXIS

1. Mở **PLAXIS Input**.
2. Menu **Expert → Configure remote scripting server**.
3. Bật server, ghi lại **Port** và **Password**.

## Cách chạy

### A) Chạy như script bên ngoài PLAXIS

Mở `plaxis_material_selector.py`, sửa phần cấu hình đầu file cho khớp:

```python
HOST = "localhost"
PORT = 10000      # đúng Port của remote scripting server
PASSWORD = ""     # đúng Password của remote scripting server
```

Rồi chạy:

```bash
python plaxis_material_selector.py
```

Một cửa sổ bảng (tkinter) sẽ hiện lên. Nếu môi trường không có tkinter, bảng
sẽ được in ra console.

### B) Chạy trực tiếp trong cửa sổ Python của PLAXIS

Trong PLAXIS đã có sẵn biến `g_i`, chỉ cần:

```python
import plaxis_material_selector as pms
pms.run_from_plaxis(g_i)
```

## Ghi chú

- Tool đọc material qua thuộc tính `.Material` của từng đối tượng, có fallback
  cho trường hợp material gán theo phase (staged construction).
- Trong bảng "toàn bộ material set", các material set đã khai báo nhưng chưa
  gán cho đối tượng nào sẽ hiển thị với số lượng đối tượng bằng `0`.
