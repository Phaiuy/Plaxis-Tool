"""Đọc / ghi cấu hình cho Plaxis Hotkey Tool."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict

# Đường dẫn config mặc định: config.json ở thư mục gốc dự án
DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json"
)

# Cấu hình mặc định dùng khi không tìm thấy file config.
DEFAULT_CONFIG = {
    "connection": {
        "host": "localhost",
        "port": 10000,
        "password": "",
    },
    "shortcuts": {
        "delete": "ctrl+shift+d",
        "array": "ctrl+shift+a",
        "move": "ctrl+shift+m",
        "copy": "ctrl+shift+c",
        "rotate": "ctrl+shift+r",
        "group": "ctrl+shift+g",
        "ungroup": "ctrl+shift+u",
        "undo": "ctrl+shift+z",
        "redo": "ctrl+shift+y",
    },
}


@dataclass
class ConnectionConfig:
    host: str = "localhost"
    port: int = 10000
    password: str = ""


@dataclass
class AppConfig:
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)
    shortcuts: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        conn = data.get("connection", {}) or {}
        return cls(
            connection=ConnectionConfig(
                host=conn.get("host", "localhost"),
                port=int(conn.get("port", 10000)),
                password=conn.get("password", ""),
            ),
            shortcuts=dict(data.get("shortcuts", {}) or {}),
        )


def load_config(path: str | None = None) -> AppConfig:
    """Đọc cấu hình từ file JSON. Nếu không có file thì dùng mặc định."""
    path = path or DEFAULT_CONFIG_PATH
    if not os.path.exists(path):
        print(f"[config] Không tìm thấy '{path}', dùng cấu hình mặc định.")
        return AppConfig.from_dict(DEFAULT_CONFIG)

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return AppConfig.from_dict(data)
