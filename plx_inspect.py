# -*- coding: utf-8 -*-
"""
PLAXIS INSPECT - cong cu chan doan de tim dung thuoc tinh dieu khien HIEN/AN.

Vi sao can file nay?
  API cua PLAXIS Input dat/doi thuoc tinh qua setproperties()/g_i.set()/gan
  truc tiep, nhung TEN thuoc tinh dieu khien hien/an tren vung ve (neu co) khac
  nhau giua cac phien ban. Script nay hoi CHINH PLAXIS cua ban de liet ke ra.

Cach dung:
  1. Chon 1 doi tuong trong PLAXIS (vung ve hoac Model explorer).
  2. Chay file nay (Expert > Python, hoac standalone).
  3. Doc phan ket qua in ra:
        - Toan bo thuoc tinh cua doi tuong (echo)
        - Cac thuoc tinh co gia tri kieu True/False (ung vien hien/an)
  4. Neu thay ten nao ro rang la "hien/an" (vi du Visible, Show, ...),
     them ten do vao DAU danh sach VISIBILITY_PROPERTIES trong
     plaxis_isolate/config.py roi chay lai Isolate.
  5. Neu KHONG co thuoc tinh boolean nao lien quan hien/an -> phien ban PLAXIS
     nay khong cho dieu khien hien/an tu Python (gui thong tin nay lai giup toi).

Gui lai toan bo ket qua in ra neu ban muon toi xac dinh gium.
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from plaxis_isolate import core, config


def _echo_text(g_i, obj):
    """Lay chuoi mo ta day du cua doi tuong (danh sach thuoc tinh + gia tri)."""
    # Cach 1: obj.echo()
    try:
        txt = obj.echo()
        if txt:
            return str(txt)
    except Exception:
        pass
    # Cach 2: g_i.echo(obj)
    try:
        txt = g_i.echo(obj)
        if txt:
            return str(txt)
    except Exception:
        pass
    return None


def _boolean_candidates_from_echo(text):
    """Tim cac ten thuoc tinh co gia tri True/False trong chuoi echo."""
    found = []
    if not text:
        return found
    for line in text.splitlines():
        # Cac dong echo thuong dang: "PropertyName: True" hoac "PropertyName True"
        m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*[:=]?\s*(True|False)\b", line)
        if m:
            found.append((m.group(1), m.group(2)))
    return found


def _probe_named_properties(obj):
    """Thu doc lan luot cac ten trong VISIBILITY_PROPERTIES tren doi tuong."""
    results = []
    for name in config.VISIBILITY_PROPERTIES:
        prop = core._get_property(obj, name)
        if prop is None:
            results.append((name, "khong co"))
            continue
        val = core._read_value(prop)
        results.append((name, "= {}".format(val)))
    return results


def _sample_object(g_i):
    """Lay 1 doi tuong de kiem tra: uu tien selection, roi den collection dau tien."""
    sel = core.get_selection(g_i)
    if sel:
        return sel[0], "selection"
    for coll_name in config.ISOLATABLE_COLLECTIONS:
        coll = core._get_property(g_i, coll_name)
        if coll is None:
            continue
        try:
            items = list(coll)
        except Exception:
            continue
        if items:
            return items[0], "collection '{}'".format(coll_name)
    return None, None


def main():
    g_i = globals().get("g_i", None)
    g_i = core.get_g_i(g_i)

    obj, source = _sample_object(g_i)
    print("=" * 64)
    print("PLAXIS INSPECT - tim thuoc tinh dieu khien HIEN/AN")
    print("=" * 64)

    if obj is None:
        print("Khong tim thay doi tuong nao de kiem tra. Hay chon 1 doi tuong "
              "roi chay lai.")
        return

    print("Doi tuong kiem tra: {}  (nguon: {})".format(core._obj_key(obj), source))
    print("-" * 64)

    # 1) Thu cac ten dang cau hinh
    print("[1] Thu cac ten trong config.VISIBILITY_PROPERTIES:")
    for name, status in _probe_named_properties(obj):
        print("    - {:<14} {}".format(name, status))
    print("-" * 64)

    # 2) Echo toan bo thuoc tinh
    text = _echo_text(g_i, obj)
    print("[2] echo() cua doi tuong (toan bo thuoc tinh):")
    if text:
        for line in text.splitlines():
            print("    " + line)
    else:
        print("    (khong lay duoc echo)")
    print("-" * 64)

    # 3) Cac ung vien boolean (co the la thuoc tinh hien/an)
    print("[3] Cac thuoc tinh co gia tri True/False (ung vien hien/an):")
    cands = _boolean_candidates_from_echo(text)
    if cands:
        for name, val in cands:
            print("    - {:<24} = {}".format(name, val))
        print("")
        print("    => Neu thay ten nao ro rang la hien/an (vd Visible/Show),")
        print("       them vao DAU config.VISIBILITY_PROPERTIES roi chay Isolate.")
    else:
        print("    (khong tim thay thuoc tinh boolean nao trong echo)")
        print("    => Co the phien ban PLAXIS nay khong cho dieu khien hien/an")
        print("       tu Python. Hay gui lai ket qua nay de toi tu van tiep.")
    print("=" * 64)


if __name__ == "__main__":
    main()
else:
    main()
