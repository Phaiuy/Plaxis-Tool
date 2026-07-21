# -*- coding: utf-8 -*-
"""
PLAXIS ISOLATE - chi hien doi tuong dang chon, an tat ca phan con lai.

Dung cho CA PLAXIS 2D va 3D.

Cach dung:
  * Trong PLAXIS: Expert > Configure Python tools... (hoac Expert > Python),
    tro toi file nay. PLAXIS se cung cap s5n bien `g_i`.
  * Standalone: `python plx_isolate.py` (can bat remote scripting server va
    cau hinh trong plaxis_isolate/config.py).

Buoc lam viec:
  1. Chon doi tuong tren vung ve (hoac Model explorer) trong PLAXIS.
  2. Chay tool nay -> chi doi tuong dang chon con hien, phan con lai bi an.
  3. Chay plx_unisolate.py de khoi phuc.
"""

import os
import sys

# Cho phep chay du PLAXIS goi file tu thu muc lam viec bat ky.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from plaxis_isolate import core


def main():
    # `g_i` co the da duoc PLAXIS bom vao globals khi chay dang Expert tool.
    g_i = globals().get("g_i", None)
    try:
        core.isolate(g_i)
    except Exception as exc:
        print("ISOLATE loi: {}".format(exc))
        raise


if __name__ == "__main__":
    main()
else:
    # Khi PLAXIS `exec` file nay trong namespace co s5n `g_i`, khoi __main__
    # co the khong chay -> goi truc tiep de dam bao tool thuc thi.
    main()
