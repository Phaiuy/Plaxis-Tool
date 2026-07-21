# PLAXIS Isolate Tool

Bộ công cụ Python cho **PLAXIS 2D và PLAXIS 3D** thêm lệnh **Isolate** — *chỉ
hiện đối tượng đang chọn, ẩn toàn bộ phần còn lại* — giống lệnh **Isolate** trong
các phần mềm model khác (SketchUp, Rhino, Revit, Navisworks…), kèm lệnh
**Unisolate** để khôi phục lại như cũ.

Chạy được ở **hai chế độ**:

- **Nhúng trong PLAXIS** qua menu **Expert → Python / Run Python Tool** (dùng biến
  `g_i` mà PLAXIS cấp sẵn).
- **Chạy ngoài (standalone)** qua **Remote Scripting Server** của PLAXIS.

Cùng một mã nguồn dùng chung cho **cả 2D lẫn 3D**.

---

## 1. Nội dung

| File | Chức năng |
|------|-----------|
| `plx_isolate.py`   | **Isolate** – chỉ hiện đối tượng đang chọn, ẩn phần còn lại |
| `plx_unisolate.py` | **Unisolate** – khôi phục hiện/ẩn về đúng trạng thái trước khi Isolate |
| `plx_show_all.py`  | **Show All** – hiện lại tất cả đối tượng (reset hiển thị) |
| `plx_inspect.py`   | **Inspect** – chẩn đoán: in toàn bộ thuộc tính của đối tượng để tìm đúng tên thuộc tính hiện/ẩn |
| `plaxis_isolate/config.py` | Cấu hình (host/port/password, tên thuộc tính hiện/ẩn, danh sách collection) |
| `plaxis_isolate/core.py`   | Toàn bộ logic |
| `tests/test_core.py`       | Bộ kiểm thử bằng PLAXIS giả lập (không cần PLAXIS thật) |

---

## 2. Cài đặt vào menu Expert của PLAXIS

### Bước 1 — Chép thư mục
Chép cả thư mục `Plaxis-Tool` vào máy, ví dụ:

```
C:\PlaxisTools\Plaxis-Tool\
```

### Bước 2 — Bật Remote Scripting Server (chỉ cần khi chạy standalone)
Trong PLAXIS Input: **Expert → Configure remote scripting server…**
→ chọn Port (ví dụ `10000`), đặt Password (nếu muốn) rồi **Start**.
Ghi lại **Port** và **Password** để điền vào `plaxis_isolate/config.py`.

> Nếu chỉ chạy tool **từ trong menu Expert của PLAXIS** thì **không bắt buộc**
> bước này — PLAXIS đã cấp sẵn `g_i`.

### Bước 3 — Đăng ký lệnh vào menu Expert
Trong PLAXIS Input mở **Expert → Python** (hoặc **Configure Python tools…**,
tên có thể khác nhau tùy phiên bản CONNECT/2023/2024) rồi **thêm 3 tool** trỏ tới:

- `...\Plaxis-Tool\plx_isolate.py`   → đặt tên **Isolate**
- `...\Plaxis-Tool\plx_unisolate.py` → đặt tên **Unisolate**
- `...\Plaxis-Tool\plx_show_all.py`  → đặt tên **Show All**

Sau khi thêm, các lệnh sẽ hiện trong menu **Expert** và có thể gán phím tắt.

> Cả 3 script tự thêm thư mục của mình vào `sys.path`, nên PLAXIS gọi từ thư
> mục làm việc nào cũng chạy được.

---

## 2b. Kết quả in ra ở đâu? (QUAN TRỌNG)

Khi PLAXIS chạy một Python tool, **`print()` KHÔNG hiện trong command line /
session history** — command line chỉ hiển thị lệnh PLAXIS, còn stdout của Python
thường bị ẩn. Đó là lý do bạn "không thấy gì".

Vì vậy tool **ghi kết quả ra file** ở nơi dễ tìm (thử lần lượt):

1. `<Desktop>\PLAXIS_isolate_log.txt` (Isolate/Unisolate/Show All)
2. `<Desktop>\PLAXIS_inspect_output.txt` (Inspect)
3. Nếu không ghi được Desktop → thư mục Home → thư mục Temp.

Sau khi chạy tool, hãy **mở file `.txt` trên Desktop** để xem kết quả.

---

## 3. Cách sử dụng

1. **Chọn** một hoặc nhiều đối tượng trên vùng vẽ (hoặc trong Model explorer).
2. Chạy **Expert → Isolate** → chỉ đối tượng đang chọn còn hiện, phần còn lại bị ẩn.
3. Chạy **Expert → Unisolate** để khôi phục về đúng trạng thái trước đó.
   (Hoặc **Show All** để hiện lại tất cả.)

Trạng thái hiện/ẩn trước khi Isolate được lưu ra file tạm (theo từng project),
nên Unisolate khôi phục **chính xác** — kể cả những đối tượng vốn đã bị ẩn từ trước.

---

## 4. Chạy standalone (ngoài PLAXIS)

Cần Python có `plxscripting` (đi kèm bản cài PLAXIS). Sau khi bật Remote Scripting
Server và điền `config.py`:

```bash
python plx_isolate.py
python plx_unisolate.py
python plx_show_all.py
```

Dùng trong script của bạn:

```python
from plaxis_isolate import core
core.isolate()     # tự tìm g_i (nhúng) hoặc tự kết nối (standalone)
core.unisolate()
core.show_all()
```

---

## 5. Cấu hình (`plaxis_isolate/config.py`)

- `HOST`, `INPUT_PORTS`, `PASSWORD`, `CONNECT_TIMEOUT` — thông số kết nối Remote
  Scripting Server (chỉ dùng khi chạy standalone). `INPUT_PORTS` là danh sách,
  tool sẽ thử lần lượt (tiện khi mở đồng thời 2D và 3D ở port khác nhau).
- `VISIBILITY_PROPERTIES` — **điểm chỉnh quan trọng nhất.** Các phiên bản PLAXIS
  có thể đặt tên thuộc tính điều khiển hiện/ẩn khác nhau. Tool thử lần lượt các
  tên trong danh sách và dùng cái đầu tiên chạy được. Nếu bản PLAXIS của bạn
  dùng tên khác (kiểm tra bằng `obj.echo()` trong Python console của PLAXIS),
  chỉ cần thêm tên đó vào đầu danh sách.
- `ISOLATABLE_COLLECTIONS` — các nhóm đối tượng được duyệt để ẩn. Nhóm nào không
  tồn tại trong model sẽ tự bỏ qua, nên liệt kê rộng cho cả 2D và 3D đều an toàn.

---

## 6. Kiểm thử

Logic được kiểm thử bằng PLAXIS **giả lập**, không cần cài PLAXIS:

```bash
python tests/test_core.py
```

Kết quả mong đợi: *tất cả test PASS* (kiểm tra isolate ẩn đúng phần còn lại,
isolate nhiều đối tượng, unisolate khôi phục đúng trạng thái cũ, báo lỗi khi
chưa chọn gì, show_all, và unisolate khi không có file trạng thái).

---

## 6b. QUAN TRỌNG — Nếu Isolate không ẩn được đối tượng nào

PLAXIS Input đặt/đổi thuộc tính qua `setproperties()` / `g_i.set()`, nhưng **tên
thuộc tính điều khiển hiện/ẩn trên vùng vẽ khác nhau giữa các phiên bản** (và một
số phiên bản có thể không hỗ trợ điều khiển hiện/ẩn từ Python). Vì vậy nếu chạy
Isolate mà không có đối tượng nào bị ẩn, hãy làm bước chẩn đoán:

1. Chọn **1 đối tượng** bất kỳ trong PLAXIS.
2. Chạy **`plx_inspect.py`** (đăng ký như một Expert tool, hoặc chạy standalone).
3. Mở file **`PLAXIS_inspect_output.txt` trên Desktop** và đọc:
   - Mục **[2] echo()** liệt kê **toàn bộ thuộc tính** của đối tượng.
   - Mục **[3]** liệt kê các thuộc tính có giá trị `True/False` — ứng viên hiện/ẩn.
4. Nếu thấy tên nào rõ ràng là hiện/ẩn (ví dụ `Visible`, `Show`…), **thêm tên đó
   vào đầu** `VISIBILITY_PROPERTIES` trong `plaxis_isolate/config.py`, rồi chạy lại
   Isolate.
5. Nếu **không có** thuộc tính boolean nào liên quan hiện/ẩn → phiên bản PLAXIS đó
   không cho điều khiển hiện/ẩn từ Python; hãy gửi lại kết quả `plx_inspect.py`
   (kèm phiên bản PLAXIS) để được tư vấn tiếp.

---

## 7. Xử lý sự cố

| Hiện tượng | Nguyên nhân / khắc phục |
|-----------|--------------------------|
| *"Chua chon doi tuong nao"* | Chưa chọn gì. Hãy chọn ít nhất một đối tượng rồi chạy lại. |
| Chạy xong nhưng **không đối tượng nào bị ẩn** | Tên thuộc tính hiện/ẩn của phiên bản PLAXIS khác với mặc định → thêm tên đúng vào đầu `VISIBILITY_PROPERTIES`. |
| *"Khong the ket noi PLAXIS…"* (standalone) | Chưa bật Remote Scripting Server, hoặc sai Host/Port/Password trong `config.py`. |
| *"Khong tim thay module 'plxscripting'"* | Đang chạy standalone bằng Python không có `plxscripting`. Chạy tool từ **trong** PLAXIS, hoặc dùng Python đi kèm PLAXIS. |

---

## 8. Ghi chú kỹ thuật

- **API hiện/ẩn theo phiên bản:** PLAXIS không đảm bảo tên thuộc tính điều khiển
  hiển thị giống nhau qua mọi phiên bản, nên tool dò tên lúc chạy
  (`VISIBILITY_PROPERTIES`) và thử nhiều cách gọi `set` (`g_i.set(obj.Prop, v)`,
  `g_i.set(obj, "Prop", v)`, `obj.Prop.set(v)`, gán trực tiếp). Đây là điểm duy
  nhất bạn có thể cần chỉnh cho đúng bản PLAXIS của mình.
- **Lấy vùng chọn:** dùng `g_i.selection` (API chuẩn của PLAXIS Input).
- **2D vs 3D:** cùng một `g_i` API; script không phân biệt phiên bản.
