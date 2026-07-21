# Plaxis-Tool

Công cụ gán **phím tắt (hotkey)** cho các lệnh của Plaxis như `delete`, `array`,
`move`, `copy`, `rotate`, `group`... Khi nhấn tổ hợp phím, công cụ sẽ gửi lệnh tới
**Plaxis Input** thông qua **Remote Scripting API** (`plxscripting`), thao tác trên
các đối tượng đang được chọn.

## Tính năng

| Lệnh      | Phím tắt mặc định | Mô tả                                   |
|-----------|-------------------|-----------------------------------------|
| delete    | `Ctrl+Shift+D`    | Xóa các đối tượng đang chọn             |
| array     | `Ctrl+Shift+A`    | Tạo mảng (hỏi số bản sao + khoảng cách) |
| move      | `Ctrl+Shift+M`    | Di chuyển (hỏi dx, dy, dz)              |
| copy      | `Ctrl+Shift+C`    | Sao chép với offset                     |
| rotate    | `Ctrl+Shift+R`    | Xoay (hỏi góc + tâm xoay)               |
| group     | `Ctrl+Shift+G`    | Nhóm đối tượng                          |
| ungroup   | `Ctrl+Shift+U`    | Bỏ nhóm                                 |
| undo      | `Ctrl+Shift+Z`    | Hoàn tác                                |
| redo      | `Ctrl+Shift+Y`    | Làm lại                                 |

Thoát chương trình: `Ctrl+Alt+Q`.

## Cài đặt

```bash
pip install -r requirements.txt
```

> `plxscripting` thường đã có sẵn trong bản cài Plaxis. Nếu thiếu, dùng bản Python
> đi kèm Plaxis hoặc cài từ thư mục cài đặt Plaxis.

## Bật Remote Scripting trong Plaxis

1. Mở **Plaxis Input**.
2. Vào menu **Expert → Configure remote scripting server**.
3. Chọn **port** (mặc định `10000`) và đặt **password**, bấm **Start server**.
4. Ghi lại port + password để điền vào `config.json`.

## Cấu hình

Sửa file [`config.json`](./config.json):

```json
{
  "connection": {
    "host": "localhost",
    "port": 10000,
    "password": "MẬT_KHẨU_CỦA_BẠN"
  },
  "shortcuts": {
    "delete": "ctrl+shift+d",
    "array":  "ctrl+shift+a",
    "move":   "ctrl+shift+m"
  }
}
```

- `connection`: thông tin kết nối tới Plaxis remote scripting server.
- `shortcuts`: tùy chỉnh tổ hợp phím cho từng lệnh (cú pháp theo thư viện
  [`keyboard`](https://github.com/boppreh/keyboard), ví dụ `ctrl+shift+d`).

## Chạy

```bash
python run.py
```

Hoặc:

```bash
python -m plaxis_hotkeys.main
```

Kiểm tra bảng phím tắt mà không cần kết nối Plaxis:

```bash
python run.py --no-connect
```

## Cách dùng

1. Trong Plaxis, **chọn** các đối tượng cần thao tác.
2. Nhấn phím tắt tương ứng (ví dụ `Ctrl+Shift+D` để xóa).
3. Với các lệnh cần tham số (move, array, copy, rotate), một hộp thoại nhỏ sẽ hiện
   ra để nhập giá trị.

## Cấu trúc dự án

```
Plaxis-Tool/
├── config.json                 # Cấu hình kết nối + phím tắt
├── requirements.txt
├── run.py                      # Điểm khởi chạy nhanh
└── plaxis_hotkeys/
    ├── config.py               # Đọc cấu hình
    ├── plaxis_client.py        # Kết nối & gửi lệnh tới Plaxis
    ├── ui.py                   # Hộp thoại nhập tham số (tkinter)
    ├── hotkey_manager.py       # Đăng ký phím tắt toàn cục
    └── main.py                 # Luồng chính
```

## Lưu ý

- Trên Windows, thư viện `keyboard` cần chạy với quyền phù hợp để bắt phím tắt
  toàn cục. Trên Linux có thể cần chạy bằng `sudo`.
- Tên hàm/tham số lệnh trong `plaxis_client.py` (`g_i.array`, `g_i.move`...) có thể
  khác nhau đôi chút giữa các phiên bản Plaxis (2D/3D, các bản khác nhau). Nếu gặp
  lỗi lệnh, hãy đối chiếu với tài liệu Remote Scripting của phiên bản Plaxis đang dùng
  và chỉnh lại cho phù hợp.
