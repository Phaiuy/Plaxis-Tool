"""Điểm khởi chạy Plaxis Hotkey Tool.

Chạy:  python -m plaxis_hotkeys.main
Hoặc:  python run.py
"""

from __future__ import annotations

import argparse
import sys

from .config import load_config
from .hotkey_manager import HotkeyManager
from .plaxis_client import PlaxisClient


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gán phím tắt điều khiển lệnh Plaxis (delete, array, move...)."
    )
    parser.add_argument(
        "-c", "--config", default=None,
        help="Đường dẫn file config.json (mặc định: config.json ở gốc dự án).",
    )
    parser.add_argument(
        "--no-connect", action="store_true",
        help="Chỉ hiển thị bảng phím tắt, không kết nối Plaxis (để kiểm tra).",
    )
    args = parser.parse_args(argv)

    cfg = load_config(args.config)

    print("=" * 50)
    print(" Plaxis Hotkey Tool")
    print("=" * 50)

    client = PlaxisClient(cfg.connection)
    if not args.no_connect:
        try:
            client.connect()
        except Exception as exc:  # noqa: BLE001
            print(f"[lỗi] Không kết nối được Plaxis: {exc}")
            print("      Kiểm tra: đã bật Remote scripting server trong Plaxis chưa,")
            print("      host/port/password trong config.json có đúng không.")
            return 1

    manager = HotkeyManager(client)

    if args.no_connect:
        print("\nBảng phím tắt (chế độ --no-connect, không đăng ký):")
        for command, hotkey in cfg.shortcuts.items():
            print(f"[hotkey] {hotkey:<16} -> {command}")
        print("\n(--no-connect) Không lắng nghe phím tắt. Thoát.")
        return 0

    print("\nBảng phím tắt:")
    manager.register(cfg.shortcuts)

    try:
        manager.run_forever()
    except KeyboardInterrupt:
        print("\nĐã thoát.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
