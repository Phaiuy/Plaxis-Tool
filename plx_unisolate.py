# -*- coding: utf-8 -*-
"""
PLAXIS UNISOLATE - khoi phuc hien/an nhu truoc khi Isolate.

Dung cho CA PLAXIS 2D va 3D.

LUU Y: ket qua duoc ghi ra file (mac dinh: <Desktop>\\PLAXIS_isolate_log.txt),
vi print() cua Python tool khong hien tren command line PLAXIS.

Neu khong tim thay trang thai da luu thi tool se "hien tat ca doi tuong".
"""

import os
import sys
import traceback


def _script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()


_HERE = _script_dir()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


def _emergency_log(text):
    try:
        import io
        home = os.path.expanduser("~")
        for path in (os.path.join(home, "Desktop", "PLAXIS_isolate_log.txt"),
                     os.path.join(home, "PLAXIS_isolate_log.txt")):
            parent = os.path.dirname(path)
            if parent and not os.path.isdir(parent):
                continue
            with io.open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            return
    except Exception:
        pass


def main():
    g_i = globals().get("g_i", None)
    try:
        from plaxis_isolate import core
        core.unisolate(g_i)
    except Exception:
        tb = "UNISOLATE gap loi:\n\n" + traceback.format_exc()
        try:
            from plaxis_isolate import core
            core.log(tb)
        except Exception:
            _emergency_log(tb)
        try:
            print(tb)
        except Exception:
            pass


main()
