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

### A) Đưa vào PLAXIS qua **Expert → Python** (khuyên dùng)

Đây chính là cách đưa tool vào menu Expert / Run Python để bấm là chạy ngay
trong phiên PLAXIS đang mở — **không cần điền PORT/PASSWORD**. Khi PLAXIS chạy
tool, nó tự truyền cổng và mật khẩu qua dòng lệnh, nên trong code
`new_server()` gọi không tham số sẽ tự kết nối đúng phiên PLAXIS đó.

Các bước:

1. Mở **PLAXIS Input**.
2. Menu **Expert → Python** (một số phiên bản là *Expert → Configure Python
   tools* hoặc nút *Tools* trong cửa sổ Python).
3. Chọn **Add / New tool** rồi trỏ tới file `plaxis_material_selector.py` này
   (hoặc dán nội dung file vào một tool mới, đặt tên ví dụ
   *"Material Set Selector"*).
4. Lưu lại. Từ giờ tool sẽ xuất hiện trong danh sách để **Run**.

Mỗi lần dùng:

- Muốn xem/chọn theo material set của **một nhóm đối tượng cụ thể**: chọn sẵn
  các đối tượng đó trong mô hình rồi Run tool.
- Muốn xem **toàn bộ** material set trong mô hình: không chọn gì, Run tool.

> Lưu ý: PLAXIS chạy tool bằng bản Python đi kèm của nó. Bản này thường có sẵn
> `plxscripting` và `tkinter`, nên bảng sẽ hiện dạng cửa sổ. Nếu bản Python đó
> không có `tkinter`, tool tự động in bảng ra console/log.

> **Cửa sổ console đen (python.exe):** trên Windows, khi PLAXIS chạy tool bằng
> `python.exe` sẽ có một cửa sổ console đen bật lên trước. Tool đã tự **ẩn**
> cửa sổ này (Windows API) ngay khi khởi động. Nếu muốn chắc chắn không nhấp
> nháy chút nào, có thể đăng ký tool trỏ tới bản `pythonw.exe` (chạy không
> console) thay cho `python.exe`, hoặc đổi đuôi file thành `.pyw`.

### B) Chạy như script bên ngoài PLAXIS

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

### C) Chạy trực tiếp trong cửa sổ Python của PLAXIS

Trong PLAXIS đã có sẵn biến `g_i`, chỉ cần:

```python
import plaxis_material_selector as pms
pms.run_from_plaxis(g_i)
```

## Ghi chú

- Khi bấm **Select objects**, mặc định tool chọn **hình học cấp cao nhất**
  của từng feature — Polygon (2D), SoilVolume/Volume (3D), Line, Surface…
  (leo hết chuỗi `.Parent`). Đây đúng là cách PLAXIS chọn khi bạn click tay,
  nên **Selection explorer hiện đầy đủ tham số chung** (tọa độ x/y/z, axis
  function…) để hiệu chỉnh hàng loạt. Có thể đổi chế độ ngay trên giao diện:
  - *Hình học (như chọn tay)* — mặc định, sửa được tham số chung;
  - *Hình học + feature* — chọn cả hai;
  - *Chỉ feature* — chỉ chọn Soil/Plate…
- Chiều ngược lại cũng được xử lý: nếu bạn chọn tay một Polygon/Volume (hình
  học) rồi chạy tool, tool sẽ tìm material qua feature con (Soil, Plate…)
  nằm trong hình học đó.
- Tool đọc material qua thuộc tính `.Material` của từng đối tượng, có fallback
  cho trường hợp material gán theo phase (staged construction).
- Trong bảng "toàn bộ material set", các material set đã khai báo nhưng chưa
  gán cho đối tượng nào sẽ hiển thị với số lượng đối tượng bằng `0`.
