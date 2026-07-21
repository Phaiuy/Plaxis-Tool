# -*- coding: utf-8 -*-
"""
PLAXIS UNISOLATE - khoi phuc hien/an nhu truoc khi Isolate.

Dung cho CA PLAXIS 2D va 3D.

Neu khong tim thay trang thai da luu (vi du da dong/mo lai project) thi tool
se chuyen sang "hien tat ca doi tuong".
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
        core.unisolate(g_i)
    except Exception as exc:
        print("UNISOLATE loi: {}".format(exc))
        raise


if __name__ == "__main__":
    main()
else:
    main()
