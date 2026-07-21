"""Lớp kết nối và gửi lệnh tới Plaxis Input qua Remote Scripting API.

Yêu cầu:
  - Đã bật Remote scripting server trong Plaxis Input
    (Expert > Configure remote scripting server), ghi lại port + password.
  - Cài thư viện plxscripting (đi kèm bản cài Plaxis hoặc `pip install plxscripting`).
"""

from __future__ import annotations

from typing import Any

from .config import ConnectionConfig


class PlaxisClient:
    """Bao bọc kết nối tới Plaxis, cung cấp các lệnh thao tác đối tượng."""

    def __init__(self, conn: ConnectionConfig):
        self._conn = conn
        self.s_i: Any = None  # server object
        self.g_i: Any = None  # global input object

    # ------------------------------------------------------------------ #
    # Kết nối
    # ------------------------------------------------------------------ #
    def connect(self) -> None:
        """Mở kết nối tới Plaxis Input server."""
        try:
            from plxscripting.easy import new_server
        except ImportError as exc:  # pragma: no cover - phụ thuộc môi trường
            raise RuntimeError(
                "Chưa cài thư viện 'plxscripting'. Cài đặt: pip install plxscripting"
            ) from exc

        kwargs = {}
        if self._conn.password:
            kwargs["password"] = self._conn.password

        self.s_i, self.g_i = new_server(
            self._conn.host, self._conn.port, **kwargs
        )
        print(
            f"[plaxis] Đã kết nối tới {self._conn.host}:{self._conn.port}"
        )

    @property
    def connected(self) -> bool:
        return self.g_i is not None

    def _require_connection(self) -> None:
        if not self.connected:
            raise RuntimeError("Chưa kết nối tới Plaxis. Gọi connect() trước.")

    # ------------------------------------------------------------------ #
    # Tiện ích chung
    # ------------------------------------------------------------------ #
    def selection(self):
        """Trả về danh sách đối tượng đang được chọn trong Plaxis."""
        self._require_connection()
        return list(self.g_i.selection)

    def run_raw(self, command: str):
        """Gửi một dòng lệnh thô tới command-line của Plaxis.

        Ví dụ: run_raw("delete Line_1") tương đương gõ lệnh trong Plaxis.
        """
        self._require_connection()
        # plxscripting expose command-line qua s_i.<...>; dùng tunnel chung:
        return self.s_i.call_and_handle_command(command)

    # ------------------------------------------------------------------ #
    # Các lệnh thao tác đối tượng
    # ------------------------------------------------------------------ #
    def delete(self):
        """Xóa các đối tượng đang chọn."""
        self._require_connection()
        selected = self.selection()
        if not selected:
            print("[delete] Không có đối tượng nào đang được chọn.")
            return
        self.g_i.delete(*selected)
        print(f"[delete] Đã xóa {len(selected)} đối tượng.")

    def move(self, dx: float, dy: float, dz: float = 0.0):
        """Di chuyển các đối tượng đang chọn theo vector (dx, dy, dz)."""
        self._require_connection()
        selected = self.selection()
        if not selected:
            print("[move] Không có đối tượng nào đang được chọn.")
            return
        self.g_i.move(selected, (dx, dy, dz))
        print(f"[move] Đã di chuyển {len(selected)} đối tượng theo ({dx}, {dy}, {dz}).")

    def array(self, nx: int, ny: int, dx: float, dy: float,
              nz: int = 1, dz: float = 0.0):
        """Tạo mảng (array) hình chữ nhật từ các đối tượng đang chọn.

        nx, ny, nz: số bản sao theo mỗi trục (tính cả bản gốc).
        dx, dy, dz: khoảng cách giữa các bản sao.
        """
        self._require_connection()
        selected = self.selection()
        if not selected:
            print("[array] Không có đối tượng nào đang được chọn.")
            return
        # Plaxis: array(objects, nx, ny, nz, (dx, dy, dz)) — tùy phiên bản.
        self.g_i.array(selected, nx, ny, nz, (dx, dy, dz))
        print(f"[array] Đã tạo mảng {nx}x{ny}x{nz} cho {len(selected)} đối tượng.")

    def copy(self, dx: float, dy: float, dz: float = 0.0):
        """Sao chép các đối tượng đang chọn với offset (dx, dy, dz)."""
        self._require_connection()
        selected = self.selection()
        if not selected:
            print("[copy] Không có đối tượng nào đang được chọn.")
            return
        # Sao chép = tạo array 2 phần tử theo 1 trục.
        self.g_i.array(selected, 2, 1, 1, (dx, dy, dz))
        print(f"[copy] Đã sao chép {len(selected)} đối tượng.")

    def rotate(self, angle: float, cx: float = 0.0, cy: float = 0.0, cz: float = 0.0):
        """Xoay đối tượng đang chọn quanh điểm (cx, cy, cz) một góc (độ)."""
        self._require_connection()
        selected = self.selection()
        if not selected:
            print("[rotate] Không có đối tượng nào đang được chọn.")
            return
        self.g_i.rotate(selected, angle, (cx, cy, cz))
        print(f"[rotate] Đã xoay {len(selected)} đối tượng {angle} độ.")

    def group(self):
        """Nhóm các đối tượng đang chọn."""
        self._require_connection()
        selected = self.selection()
        if not selected:
            print("[group] Không có đối tượng nào đang được chọn.")
            return
        self.g_i.group(*selected)
        print(f"[group] Đã nhóm {len(selected)} đối tượng.")

    def ungroup(self):
        """Bỏ nhóm các đối tượng đang chọn."""
        self._require_connection()
        selected = self.selection()
        if not selected:
            print("[ungroup] Không có đối tượng nào đang được chọn.")
            return
        self.g_i.ungroup(*selected)
        print(f"[ungroup] Đã bỏ nhóm {len(selected)} đối tượng.")

    def undo(self):
        """Hoàn tác thao tác gần nhất."""
        self._require_connection()
        self.g_i.undo()
        print("[undo] Đã hoàn tác.")

    def redo(self):
        """Làm lại thao tác vừa hoàn tác."""
        self._require_connection()
        self.g_i.redo()
        print("[redo] Đã làm lại.")
