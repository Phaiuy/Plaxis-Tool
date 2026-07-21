# -*- coding: utf-8 -*-
"""
PLAXIS SHOW ALL - hien lai tat ca doi tuong (khong phu thuoc file trang thai).

Dung cho CA PLAXIS 2D va 3D. Huu ich khi ban chi muon "reset" hien thi ma
khong quan tam trang thai truoc do.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from plaxis_isolate import core


def main():
    g_i = globals().get("g_i", None)
    try:
        core.show_all(g_i)
    except Exception as exc:
        print("SHOW ALL loi: {}".format(exc))
        raise


if __name__ == "__main__":
    main()
else:
    main()
