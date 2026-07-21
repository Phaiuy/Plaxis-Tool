"""Đăng ký phím tắt toàn cục và ánh xạ tới các lệnh Plaxis."""

from __future__ import annotations

from typing import Callable, Dict

from . import ui
from .plaxis_client import PlaxisClient


class HotkeyManager:
    """Gắn phím tắt với các hành động điều khiển Plaxis."""

    def __init__(self, client: PlaxisClient):
        self.client = client
        self._registered = []

    # Xây dựng bảng ánh xạ tên lệnh -> hàm xử lý.
    def _build_actions(self) -> Dict[str, Callable[[], None]]:
        return {
            "delete": self._action_delete,
            "move": self._action_move,
            "array": self._action_array,
            "copy": self._action_copy,
            "rotate": self._action_rotate,
            "group": self.client.group,
            "ungroup": self.client.ungroup,
            "undo": self.client.undo,
            "redo": self.client.redo,
        }

    # ------------------------------------------------------------------ #
    # Các action bọc thêm xử lý lỗi / hộp thoại tham số
    # ------------------------------------------------------------------ #
    def _safe(self, fn: Callable[[], None], name: str) -> Callable[[], None]:
        def wrapper():
            try:
                fn()
            except Exception as exc:  # noqa: BLE001 - tránh làm sập listener
                print(f"[{name}] Lỗi: {exc}")
        return wrapper

    def _action_delete(self):
        self.client.delete()

    def _action_move(self):
        params = ui.ask_move()
        if params is None:
            return
        self.client.move(**params)

    def _action_array(self):
        params = ui.ask_array()
        if params is None:
            return
        self.client.array(**params)

    def _action_copy(self):
        params = ui.ask_copy()
        if params is None:
            return
        self.client.copy(**params)

    def _action_rotate(self):
        params = ui.ask_rotate()
        if params is None:
            return
        self.client.rotate(**params)

    # ------------------------------------------------------------------ #
    # Đăng ký / chạy
    # ------------------------------------------------------------------ #
    @staticmethod
    def _import_keyboard():
        """Import thư viện keyboard, báo lỗi rõ ràng nếu thiếu."""
        try:
            import keyboard  # noqa: F401
            return keyboard
        except ImportError as exc:
            raise RuntimeError(
                "Chưa cài thư viện 'keyboard' (cần để bắt phím tắt toàn cục).\n"
                "  Cài đặt: pip install keyboard\n"
                "  Nếu chạy qua Expert menu của PLAXIS, cài vào đúng Python của PLAXIS:\n"
                '    "<thư mục PLAXIS>\\python\\python.exe" -m pip install keyboard'
            ) from exc

    def register(self, shortcuts: Dict[str, str]) -> None:
        """Đăng ký các phím tắt từ config: {tên_lệnh: tổ_hợp_phím}."""
        keyboard = self._import_keyboard()

        actions = self._build_actions()
        for command, hotkey in shortcuts.items():
            action = actions.get(command)
            if action is None:
                print(f"[hotkey] Bỏ qua lệnh không hỗ trợ: '{command}'")
                continue
            if not hotkey:
                continue
            keyboard.add_hotkey(hotkey, self._safe(action, command))
            self._registered.append((hotkey, command))
            print(f"[hotkey] {hotkey:<16} -> {command}")

    def run_forever(self) -> None:
        """Lắng nghe phím tắt cho tới khi nhấn Ctrl+Alt+Q để thoát."""
        keyboard = self._import_keyboard()

        print("\nĐang lắng nghe phím tắt... Nhấn Ctrl+Alt+Q để thoát.")
        # keyboard.wait tự chặn tới khi tổ hợp phím được nhấn; gỡ hook sau khi thoát.
        keyboard.wait("ctrl+alt+q")
        keyboard.unhook_all()
        print("Đã dừng lắng nghe phím tắt.")
