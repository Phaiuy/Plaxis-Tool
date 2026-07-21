"""Điểm khởi chạy Plaxis Hotkey Tool.

Chạy:  python -m plaxis_hotkeys.main
Hoặc:  python run.py
"""

from __future__ import annotations

import argparse
import sys

from .config import load_config, resolve_connection
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
    parser.add_argument(
        "--selftest", action="store_true",
        help="Chạy thử toàn bộ lệnh với PLAXIS giả lập (không cần PLAXIS/keyboard).",
    )
    # parse_known_args: PLAXIS (Expert → Python → Run) truyền thêm port/password
    # dưới dạng tham số dòng lệnh — ta giữ lại trong `extra` để hợp nhất.
    args, extra = parser.parse_known_args(argv)

    cfg = load_config(args.config)

    if args.selftest:
        return _run_selftest(cfg)

    conn = resolve_connection(cfg.connection, extra)

    print("=" * 50)
    print(" Plaxis Hotkey Tool")
    print("=" * 50)
    print(f"Kết nối: {conn.host}:{conn.port}"
          + (" (có password)" if conn.password else " (không password)"))

    client = PlaxisClient(conn)
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
    try:
        manager.register(cfg.shortcuts)
        manager.run_forever()
    except KeyboardInterrupt:
        print("\nĐã thoát.")
    except RuntimeError as exc:
        print(f"[lỗi] {exc}")
        return 1
    return 0


def _run_selftest(cfg) -> int:
    """Chạy thử tất cả lệnh với PLAXIS giả lập, không cần phần mềm thật."""
    from ._mock import FakeGlobalInput, FakeServer

    print("=" * 50)
    print(" Plaxis Hotkey Tool — SELFTEST (PLAXIS giả lập)")
    print("=" * 50)

    client = PlaxisClient(cfg.connection)
    client.g_i = FakeGlobalInput()
    client.s_i = FakeServer()
    print(f"Đối tượng đang chọn (giả lập): {client.selection()}\n")

    steps = [
        ("delete", lambda: client.delete()),
        ("move",   lambda: client.move(1.0, 2.0, 0.0)),
        ("array",  lambda: client.array(nx=3, ny=2, dx=5.0, dy=5.0)),
        ("copy",   lambda: client.copy(2.0, 0.0, 0.0)),
        ("rotate", lambda: client.rotate(90.0)),
        ("group",  lambda: client.group()),
        ("ungroup", lambda: client.ungroup()),
        ("undo",   lambda: client.undo()),
        ("redo",   lambda: client.redo()),
    ]

    failed = 0
    for name, fn in steps:
        print(f"-> {name}")
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"   [LỖI] {name}: {exc}")
    print()

    total = len(steps)
    ok = total - failed
    print(f"Kết quả selftest: {ok}/{total} lệnh chạy OK"
          + (f", {failed} lỗi" if failed else ""))
    print(f"Tổng số lệnh gửi tới PLAXIS-giả: {len(client.g_i.calls)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
