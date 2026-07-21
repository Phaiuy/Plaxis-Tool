"""PLAXIS giả lập dùng cho kiểm thử (self-test) khi không có PLAXIS thật.

Ghi lại mọi lệnh được gọi để có thể kiểm tra logic của tool mà không cần
kết nối phần mềm PLAXIS.
"""

from __future__ import annotations

from typing import List, Tuple


class _FakeObject:
    """Đối tượng PLAXIS giả (thay cho Point, Line, Soil...)."""

    def __init__(self, name: str):
        self.Name = name

    def __repr__(self) -> str:
        return f"<{self.Name}>"


class FakeGlobalInput:
    """Giả lập đối tượng g_i của plxscripting, ghi lại các lệnh đã gọi."""

    def __init__(self, selection=None):
        # Mặc định có sẵn 2 đối tượng đang được "chọn".
        self.selection = selection if selection is not None else [
            _FakeObject("Line_1"),
            _FakeObject("Point_3"),
        ]
        self.calls: List[Tuple[str, tuple]] = []

    def _record(self, name: str, *args):
        self.calls.append((name, args))
        print(f"   [PLAXIS-giả] gọi {name}{args}")

    def delete(self, *objs):
        self._record("delete", *objs)

    def move(self, objs, vector):
        self._record("move", objs, vector)

    def array(self, objs, nx, ny, nz, vector):
        self._record("array", objs, nx, ny, nz, vector)

    def rotate(self, objs, angle, center):
        self._record("rotate", objs, angle, center)

    def group(self, *objs):
        self._record("group", *objs)

    def ungroup(self, *objs):
        self._record("ungroup", *objs)

    def undo(self):
        self._record("undo")

    def redo(self):
        self._record("redo")


class FakeServer:
    """Giả lập đối tượng s_i của plxscripting."""

    def __init__(self):
        self.commands: List[str] = []

    def call_and_handle_command(self, command: str):
        self.commands.append(command)
        print(f"   [PLAXIS-giả] lệnh thô: {command}")
        return command
