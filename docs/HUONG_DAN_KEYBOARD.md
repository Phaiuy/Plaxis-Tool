# Hướng dẫn cài & chạy thư viện `keyboard`

Thư viện `keyboard` được dùng để bắt **phím tắt toàn cục** (global hotkey). Điểm
cần nhớ:

- **Cài đặt** (`pip install`): **KHÔNG** cần quyền admin.
- **Chạy** (bắt phím tắt): **CẦN** quyền Administrator trên Windows / `root` trên Linux.
  Đây chính là "quyền phù hợp" được nhắc tới. Nếu chạy thiếu quyền, tool sẽ báo lỗi
  hoặc không nhận được phím tắt nào.

---

## A. Windows (thường gặp — PLAXIS chạy trên Windows)

### Bước 0 — Xác định bạn dùng Python nào

Có 2 tình huống, tương ứng 2 cách chạy tool:

| Cách chạy | Python dùng | Cài `keyboard` vào đâu |
|-----------|-------------|------------------------|
| **A. Chạy ngoài** (`python run.py`) | Python hệ thống bạn tự cài | Python hệ thống |
| **B. Expert menu của PLAXIS** (`Shortcut_Command_2025.1.py`) | Python đi kèm PLAXIS | Python của PLAXIS |

> Quan trọng: phải cài `keyboard` vào **đúng** Python sẽ chạy tool. Cài nhầm chỗ là
> nguyên nhân phổ biến nhất của lỗi `ModuleNotFoundError: No module named 'keyboard'`.

### Bước 1 — Cài `keyboard`

**Nếu chạy Cách A (Python hệ thống):**

1. Mở **Command Prompt** (không cần admin để cài).
2. Gõ:
   ```bat
   pip install keyboard
   ```
   Nếu máy có nhiều bản Python, dùng:
   ```bat
   py -m pip install keyboard
   ```

**Nếu chạy Cách B (Python của PLAXIS):**

1. Tìm đường dẫn Python của PLAXIS. Cách chắc chắn nhất: trong PLAXIS mở
   `Expert → Python → Interpreter` (hoặc console Python bất kỳ của PLAXIS) rồi gõ:
   ```python
   import sys; print(sys.executable)
   ```
   Nó in ra đường dẫn, ví dụ:
   ```
   C:\ProgramData\Bentley\PLAXIS\PLAXIS 2D 2025\python\python.exe
   ```
2. Mở Command Prompt và cài `keyboard` bằng **chính** python đó (thay đường dẫn cho đúng):
   ```bat
   "C:\ProgramData\Bentley\PLAXIS\PLAXIS 2D 2025\python\python.exe" -m pip install keyboard
   ```

### Bước 2 — Chạy tool với quyền Administrator

**Cách A (chạy ngoài):**

- Cách nhanh: nhấp đúp file [`run_as_admin.bat`](../run_as_admin.bat) ở thư mục gốc dự án
  (sẽ hiện cửa sổ UAC hỏi quyền → chọn **Yes**).
- Hoặc thủ công: bấm **Start**, gõ `cmd`, nhấp phải **Command Prompt →
  Run as administrator**, rồi:
  ```bat
  cd /d "C:\đường-dẫn-tới\Plaxis-Tool"
  python run.py
  ```

**Cách B (Expert menu):**

- Đóng PLAXIS, sau đó **mở lại PLAXIS bằng quyền Admin**: nhấp phải biểu tượng
  PLAXIS → **Run as administrator**.
- Lý do: khi PLAXIS chạy script qua Expert menu, tiến trình Python con **kế thừa**
  quyền của PLAXIS. PLAXIS có quyền admin thì tool mới bắt được phím tắt.
- Sau đó vào `Expert → Python → Run...` chọn `Shortcut_Command_2025.1.py`.

### Bước 3 — Kiểm tra

Trước khi cần quyền admin, hãy thử phần không cần quyền để chắc chắn đã cài đúng:

```bat
python run.py --selftest
```
Nếu thấy "9/9 lệnh chạy OK" là logic tool và việc import ổn.

Sau đó chạy thật (`run_as_admin.bat` hoặc PLAXIS admin) và bấm thử phím tắt
(`Ctrl+Shift+D`...). Thoát bằng `Ctrl+Alt+Q`.

---

## B. Linux (cần `sudo`)

Trên Linux, `keyboard` đọc `/dev/input/*` nên cần `root`:

```bash
pip install keyboard          # cài (có thể cần --user)
sudo python run.py            # chạy với quyền root
```

> Lưu ý: nếu cài bằng `pip install --user`, khi chạy `sudo` có thể không thấy gói.
> Khi đó cài bằng `sudo pip install keyboard` hoặc dùng virtualenv rồi
> `sudo <venv>/bin/python run.py`.

---

## C. Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách xử lý |
|-------------|-------------|-----------|
| `ModuleNotFoundError: No module named 'keyboard'` | Cài vào Python khác với Python đang chạy | Cài đúng Python (xem Bước 0–1) |
| Chạy được nhưng bấm phím tắt không phản ứng | Thiếu quyền admin/root | Chạy lại bằng admin (Windows) / `sudo` (Linux) |
| `ImportError: You must be root to use this library on linux` | Chưa `sudo` | Chạy `sudo python run.py` |
| Tool báo lỗi kết nối PLAXIS | Chưa bật remote scripting server / sai port/password | Xem README, kiểm tra `config.json` |

---

## D. Nếu không muốn chạy bằng quyền Admin?

Thư viện `keyboard` **bắt buộc** cần quyền cao để hook toàn hệ thống — không có cách
lách. Nếu bạn không muốn cấp quyền admin, có thể cân nhắc hướng khác (không nằm trong
phiên bản hiện tại của tool): dùng thư viện `pynput` (một số trường hợp không cần
admin trên Windows), hoặc gắn tool thành nút bấm/tab trong giao diện thay vì phím tắt
toàn cục. Nếu cần, hãy báo để mình bổ sung.
