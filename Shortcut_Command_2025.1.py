"""PLAXIS Python tool — dùng để chạy trực tiếp từ menu Expert của PLAXIS.

Cách dùng trong PLAXIS Input:
    Expert  ->  Python  ->  Run...   (hoặc thêm vào danh sách Python tools)
và chọn file này.

Khi chạy theo cách đó, PLAXIS tự truyền thông tin kết nối (port, password) của
remote scripting server đang chạy vào script qua tham số dòng lệnh. Script sẽ tự
nhận các tham số này (xem plaxis_hotkeys/config.py -> resolve_connection).
Nếu PLAXIS không truyền, tool sẽ đọc từ config.json.

Lưu ý: thư viện 'keyboard' cần được cài trong Python mà PLAXIS dùng để chạy tool.
Cài bằng chính Python đó, ví dụ (Windows):
    "<thư mục PLAXIS>\\python\\python.exe" -m pip install keyboard
"""

import os
import sys

# Đảm bảo import được package plaxis_hotkeys khi PLAXIS chạy file này trực tiếp.
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_DIR not in sys.path:
    sys.path.insert(0, _PROJECT_DIR)

from plaxis_hotkeys.main import main  # noqa: E402

if __name__ == "__main__":
    # sys.argv[1:] chứa các tham số PLAXIS truyền vào (port, password...).
    raise SystemExit(main(sys.argv[1:]))
