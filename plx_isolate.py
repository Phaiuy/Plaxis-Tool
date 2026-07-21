# -*- coding: utf-8 -*-
"""
PLAXIS ISOLATE - chi hien doi tuong dang chon, an tat ca phan con lai.

Dung cho CA PLAXIS 2D va 3D.

LUU Y: khi PLAXIS chay Python tool, print() KHONG hien tren command line.
Ket qua duoc ghi ra file (mac dinh: <Desktop>\\PLAXIS_isolate_log.txt).

Cach dung:
  1. Chon doi tuong trong PLAXIS (vung ve hoac Model explorer).
  2. Chay tool nay -> chi doi tuong dang chon con hien, phan con lai bi an.
  3. Chay plx_unisolate.py de khoi phuc.
"""

import os
import sys
import traceback


def _script_dir():
    """Thu muc chua script, chong loi khi __file__ khong duoc dinh nghia."""
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()


_HERE = _script_dir()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


def _emergency_log(text):
    """Ghi loi ra file phong khi khong import duoc package."""
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
        core.isolate(g_i)
    except Exception:
        tb = "ISOLATE gap loi:\n\n" + traceback.format_exc()
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
