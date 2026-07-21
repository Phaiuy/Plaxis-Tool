"""Kiểm thử logic lệnh với PLAXIS giả lập — không cần PLAXIS/keyboard.

Chạy:  python -m unittest discover -s tests
Hoặc:  python -m pytest tests/
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plaxis_hotkeys.config import (  # noqa: E402
    AppConfig, ConnectionConfig, resolve_connection,
)
from plaxis_hotkeys.plaxis_client import PlaxisClient  # noqa: E402
from plaxis_hotkeys._mock import FakeGlobalInput, FakeServer  # noqa: E402


def make_client():
    client = PlaxisClient(ConnectionConfig())
    client.g_i = FakeGlobalInput()
    client.s_i = FakeServer()
    return client


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.client = make_client()
        self.gi = self.client.g_i

    def _last(self):
        return self.gi.calls[-1]

    def test_delete(self):
        self.client.delete()
        name, args = self._last()
        self.assertEqual(name, "delete")
        self.assertEqual(len(args), 2)  # 2 đối tượng đang chọn

    def test_move(self):
        self.client.move(1.0, 2.0, 3.0)
        name, args = self._last()
        self.assertEqual(name, "move")
        self.assertEqual(args[1], (1.0, 2.0, 3.0))

    def test_array(self):
        self.client.array(nx=3, ny=2, dx=5.0, dy=5.0)
        name, args = self._last()
        self.assertEqual(name, "array")
        self.assertEqual(args[1:], (3, 2, 1, (5.0, 5.0, 0.0)))

    def test_copy_dung_array_2_phan_tu(self):
        self.client.copy(2.0, 0.0, 0.0)
        name, args = self._last()
        self.assertEqual(name, "array")
        self.assertEqual(args[1:], (2, 1, 1, (2.0, 0.0, 0.0)))

    def test_rotate(self):
        self.client.rotate(90.0)
        name, args = self._last()
        self.assertEqual(name, "rotate")
        self.assertEqual(args[1], 90.0)

    def test_group_ungroup_undo_redo(self):
        self.client.group()
        self.client.ungroup()
        self.client.undo()
        self.client.redo()
        names = [c[0] for c in self.gi.calls]
        self.assertEqual(names, ["group", "ungroup", "undo", "redo"])

    def test_khong_co_doi_tuong_chon_thi_khong_goi_lenh(self):
        self.gi.selection = []
        self.client.delete()
        self.assertEqual(self.gi.calls, [])  # không gọi delete khi rỗng


class TestResolveConnection(unittest.TestCase):
    def test_argv_ghi_de_config(self):
        base = ConnectionConfig(host="localhost", port=10000, password="")
        conn = resolve_connection(base, ["10001", "MyPassword"])
        self.assertEqual(conn.port, 10001)
        self.assertEqual(conn.password, "MyPassword")

    def test_khong_co_argv_giu_nguyen_config(self):
        base = ConnectionConfig(host="localhost", port=10000, password="abc")
        conn = resolve_connection(base, [])
        self.assertEqual(conn.port, 10000)
        self.assertEqual(conn.password, "abc")

    def test_env_ghi_de(self):
        base = ConnectionConfig()
        os.environ["PLAXIS_PORT"] = "20000"
        try:
            conn = resolve_connection(base, [])
            self.assertEqual(conn.port, 20000)
        finally:
            del os.environ["PLAXIS_PORT"]


class TestConfig(unittest.TestCase):
    def test_from_dict(self):
        cfg = AppConfig.from_dict({
            "connection": {"host": "h", "port": 5, "password": "p"},
            "shortcuts": {"delete": "ctrl+d"},
        })
        self.assertEqual(cfg.connection.host, "h")
        self.assertEqual(cfg.connection.port, 5)
        self.assertEqual(cfg.shortcuts["delete"], "ctrl+d")


if __name__ == "__main__":
    unittest.main(verbosity=2)
