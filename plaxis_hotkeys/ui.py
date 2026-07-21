"""Hộp thoại nhỏ để nhập tham số cho các lệnh cần thông số (move, array...).

Dùng tkinter (có sẵn trong Python chuẩn) để không thêm phụ thuộc.
"""

from __future__ import annotations

from typing import Optional, Sequence


def _ask_values(title: str, fields: Sequence[tuple[str, str]]) -> Optional[dict]:
    """Hiển thị form nhập nhiều giá trị.

    fields: danh sách (label, giá_trị_mặc_định).
    Trả về dict {label: giá trị dạng chuỗi} hoặc None nếu người dùng hủy.
    """
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:  # pragma: no cover - môi trường không có GUI
        # Không có GUI: fallback nhập qua console.
        result = {}
        print(f"\n== {title} ==")
        for label, default in fields:
            raw = input(f"  {label} [{default}]: ").strip()
            result[label] = raw if raw else default
        return result

    root = tk.Tk()
    root.title(title)
    root.resizable(False, False)
    root.attributes("-topmost", True)

    entries: dict[str, tk.Entry] = {}
    for i, (label, default) in enumerate(fields):
        ttk.Label(root, text=label).grid(row=i, column=0, padx=8, pady=4, sticky="e")
        var = tk.StringVar(value=str(default))
        ent = ttk.Entry(root, textvariable=var, width=15)
        ent.grid(row=i, column=1, padx=8, pady=4)
        entries[label] = var

    state = {"ok": False}

    def on_ok(event=None):
        state["ok"] = True
        root.destroy()

    def on_cancel(event=None):
        root.destroy()

    btns = ttk.Frame(root)
    btns.grid(row=len(fields), column=0, columnspan=2, pady=8)
    ttk.Button(btns, text="OK", command=on_ok).pack(side="left", padx=4)
    ttk.Button(btns, text="Hủy", command=on_cancel).pack(side="left", padx=4)

    root.bind("<Return>", on_ok)
    root.bind("<Escape>", on_cancel)

    # Đặt con trỏ vào ô đầu tiên
    if fields:
        first = root.grid_slaves(row=0, column=1)
        if first:
            first[0].focus_set()

    root.eval("tk::PlaceWindow . center")
    root.mainloop()

    if not state["ok"]:
        return None
    return {label: var.get() for label, var in entries.items()}


def _to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: str, default: int = 1) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def ask_move() -> Optional[dict]:
    """Hỏi vector di chuyển (dx, dy, dz)."""
    vals = _ask_values("Di chuyển (Move)", [("dx", "0"), ("dy", "0"), ("dz", "0")])
    if vals is None:
        return None
    return {
        "dx": _to_float(vals["dx"]),
        "dy": _to_float(vals["dy"]),
        "dz": _to_float(vals["dz"]),
    }


def ask_copy() -> Optional[dict]:
    """Hỏi offset sao chép (dx, dy, dz)."""
    vals = _ask_values("Sao chép (Copy)", [("dx", "1"), ("dy", "0"), ("dz", "0")])
    if vals is None:
        return None
    return {
        "dx": _to_float(vals["dx"]),
        "dy": _to_float(vals["dy"]),
        "dz": _to_float(vals["dz"]),
    }


def ask_array() -> Optional[dict]:
    """Hỏi thông số tạo mảng (số bản sao + khoảng cách)."""
    vals = _ask_values(
        "Tạo mảng (Array)",
        [
            ("nx", "2"), ("ny", "1"), ("nz", "1"),
            ("dx", "1"), ("dy", "0"), ("dz", "0"),
        ],
    )
    if vals is None:
        return None
    return {
        "nx": _to_int(vals["nx"]),
        "ny": _to_int(vals["ny"]),
        "nz": _to_int(vals["nz"]),
        "dx": _to_float(vals["dx"]),
        "dy": _to_float(vals["dy"]),
        "dz": _to_float(vals["dz"]),
    }


def ask_rotate() -> Optional[dict]:
    """Hỏi góc xoay và tâm xoay."""
    vals = _ask_values(
        "Xoay (Rotate)",
        [("angle (deg)", "90"), ("cx", "0"), ("cy", "0"), ("cz", "0")],
    )
    if vals is None:
        return None
    return {
        "angle": _to_float(vals["angle (deg)"]),
        "cx": _to_float(vals["cx"]),
        "cy": _to_float(vals["cy"]),
        "cz": _to_float(vals["cz"]),
    }
