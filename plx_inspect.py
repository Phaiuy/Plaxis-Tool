# -*- coding: utf-8 -*-
"""
PLAXIS INSPECT (ban ghi ra FILE) - tim dung thuoc tinh dieu khien HIEN/AN.

VI SAO BAN KHONG THAY GI KHI CHAY?
  Khi PLAXIS chay mot Python tool, output cua print() KHONG hien trong command
  line / session history (command line chi hien lenh PLAXIS). Stdout cua Python
  thuong bi an. Vi vay file nay GHI KET QUA RA FILE de ban mo doc.

KET QUA DUOC GHI RA (theo thu tu uu tien noi ghi duoc):
  - <Desktop>\\PLAXIS_inspect_output.txt
  - <thu muc Home>\\PLAXIS_inspect_output.txt
  - <thu muc Temp>\\PLAXIS_inspect_output.txt
  - <thu muc chua script>\\PLAXIS_inspect_output.txt

CACH DUNG:
  1. Chon 1 doi tuong trong PLAXIS (vung ve hoac Model explorer).
  2. Chay file nay (Expert tool hoac trong cua so Python cua PLAXIS).
  3. Mo file PLAXIS_inspect_output.txt tren Desktop va doc / gui lai cho toi.

File nay CO TINH DOC LAP (khong phu thuoc package) va CHONG LOI, de chac chan
luon tao ra file ket qua ke ca khi co su co.
"""

import os
import sys
import io
import traceback

try:
    import tempfile
except Exception:
    tempfile = None


# ==========================================================================
#  Ghi file ket qua (bulletproof)
# ==========================================================================
def _output_targets():
    targets = []
    try:
        home = os.path.expanduser("~")
    except Exception:
        home = None
    if home:
        targets.append(os.path.join(home, "Desktop", "PLAXIS_inspect_output.txt"))
        targets.append(os.path.join(home, "PLAXIS_inspect_output.txt"))
    if tempfile is not None:
        try:
            targets.append(os.path.join(tempfile.gettempdir(),
                                        "PLAXIS_inspect_output.txt"))
        except Exception:
            pass
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        targets.append(os.path.join(here, "PLAXIS_inspect_output.txt"))
    except Exception:
        pass
    return targets


def write_report(text):
    written = []
    for path in _output_targets():
        try:
            parent = os.path.dirname(path)
            if parent and not os.path.isdir(parent):
                continue
            with io.open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            written.append(path)
        except Exception:
            continue
    # In ra stdout phong khi co console
    try:
        print(text)
        if written:
            print("\n>>> Da ghi ket qua ra:")
            for p in written:
                print("    " + p)
    except Exception:
        pass
    return written


# ==========================================================================
#  Tim g_i (nhung trong PLAXIS hoac ket noi standalone)
# ==========================================================================
def find_g_i(lines):
    # 1) Bien g_i do PLAXIS bom vao globals cua script
    g = globals().get("g_i", None)
    if g is not None:
        lines.append("Nguon g_i: globals() cua script (PLAXIS bom vao).")
        return g

    # 2) builtins / __main__
    try:
        import builtins
    except ImportError:
        import __builtin__ as builtins
    if hasattr(builtins, "g_i"):
        lines.append("Nguon g_i: builtins.")
        return getattr(builtins, "g_i")
    try:
        import __main__
        if hasattr(__main__, "g_i"):
            lines.append("Nguon g_i: __main__.")
            return getattr(__main__, "g_i")
    except Exception:
        pass

    # 3) Ket noi remote scripting server
    try:
        from plxscripting.easy import new_server
    except ImportError:
        lines.append("Khong co bien g_i s5n va khong import duoc plxscripting.")
        lines.append("=> Hay chay file nay TU BEN TRONG PLAXIS (Expert > Python),")
        lines.append("   hoac bat remote scripting server de chay standalone.")
        return None

    for port in (10000, 10001):
        try:
            s_i, g = new_server("localhost", port, timeout=10)
            _ = s_i.name
            lines.append("Nguon g_i: ket noi remote scripting server localhost:{}."
                         .format(port))
            return g
        except Exception as exc:
            lines.append("  - khong ket noi duoc port {}: {}".format(port, exc))
    return None


# ==========================================================================
#  Doc thuoc tinh
# ==========================================================================
CANDIDATE_NAMES = ["Visible", "Visibility", "Show", "Shown", "IsVisible",
                   "Hidden", "Hide", "ShowInModel", "VisibleInModel"]


def _get_prop(obj, name):
    try:
        return getattr(obj, name)
    except Exception:
        return None


def _read_value(prop):
    if hasattr(prop, "value"):
        try:
            return prop.value
        except Exception:
            pass
    try:
        return str(prop)
    except Exception:
        return None


def _obj_name(obj):
    prop = _get_prop(obj, "Name")
    if prop is not None:
        try:
            return str(prop.value)
        except Exception:
            pass
    try:
        return str(obj)
    except Exception:
        return "<obj>"


def _echo_text(g_i, obj):
    for getter in (lambda: obj.echo(), lambda: g_i.echo(obj)):
        try:
            txt = getter()
            if txt:
                return str(txt)
        except Exception:
            continue
    return None


def _sample_object(g_i, lines):
    # Uu tien selection
    try:
        sel = list(g_i.selection)
    except Exception as exc:
        sel = []
        lines.append("Khong doc duoc g_i.selection: {}".format(exc))
    if sel:
        return sel[0], "selection ({} doi tuong dang chon)".format(len(sel))

    lines.append("Vung chon rong -> thu lay doi tuong dau tien tu cac collection.")
    for coll_name in ["Points", "Lines", "Surfaces", "Volumes", "Soils",
                      "SoilVolumes", "Plates", "Beams", "Geogrids", "Anchors"]:
        coll = _get_prop(g_i, coll_name)
        if coll is None:
            continue
        try:
            items = list(coll)
        except Exception:
            continue
        if items:
            return items[0], "collection '{}'".format(coll_name)
    return None, None


# ==========================================================================
#  Main
# ==========================================================================
def build_report():
    import datetime
    L = []
    L.append("=" * 68)
    L.append("PLAXIS INSPECT - tim thuoc tinh dieu khien HIEN/AN")
    L.append("Thoi diem: {}".format(datetime.datetime.now()))
    L.append("Python: {}".format(sys.version.replace("\n", " ")))
    L.append("=" * 68)

    g_i = find_g_i(L)
    if g_i is None:
        L.append("")
        L.append("KHONG LAY DUOC g_i -> khong the kiem tra. Xem huong dan o tren.")
        return "\n".join(L)

    # [0] Bao cao vung chon (selection) - kiem tra selection co doc duoc khong
    L.append("")
    L.append("[0] Kiem tra g_i.selection (ban co dang chon doi tuong khong?):")
    try:
        sel = list(g_i.selection)
        L.append("    So doi tuong dang chon: {}".format(len(sel)))
        for o in sel[:20]:
            L.append("      * {}".format(_obj_name(o)))
        if not sel:
            L.append("    => selection RONG. Neu ban CO chon doi tuong ma van rong")
            L.append("       thi che do Run Python Tool khong giu duoc vung chon.")
    except Exception as exc:
        L.append("    Loi doc selection: {}".format(exc))
    L.append("-" * 68)

    obj, source = _sample_object(g_i, L)
    L.append("")
    if obj is None:
        L.append("Khong tim thay doi tuong nao de kiem tra.")
        L.append("Hay tao/chon it nhat 1 doi tuong roi chay lai.")
        return "\n".join(L)

    L.append("Doi tuong kiem tra: {}   (nguon: {})".format(_obj_name(obj), source))
    L.append("-" * 68)

    # [1] Thu cac ten ung vien
    L.append("[1] Thu doc cac ten thuoc tinh hien/an thuong gap:")
    any_found = False
    for name in CANDIDATE_NAMES:
        prop = _get_prop(obj, name)
        if prop is None:
            L.append("    - {:<16} : KHONG CO".format(name))
        else:
            any_found = True
            L.append("    - {:<16} : CO  (gia tri = {})".format(
                name, _read_value(prop)))
    if any_found:
        L.append("    => Ten nao ghi 'CO' chinh la ung vien -> them vao DAU")
        L.append("       config.VISIBILITY_PROPERTIES roi chay lai Isolate.")
    else:
        L.append("    => Khong ten nao ton tai tren doi tuong nay.")
    L.append("-" * 68)

    # [2] echo toan bo
    text = _echo_text(g_i, obj)
    L.append("[2] echo() cua doi tuong (TOAN BO thuoc tinh - phan quan trong nhat):")
    if text:
        for line in text.splitlines():
            L.append("    " + line)
    else:
        L.append("    (khong lay duoc echo cua doi tuong nay)")
    L.append("-" * 68)

    # [3] Cac thuoc tinh boolean tu echo
    L.append("[3] Cac thuoc tinh co gia tri True/False (ung vien hien/an):")
    import re
    cands = []
    if text:
        for line in text.splitlines():
            m = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*[:=]?\s*(True|False)\b", line)
            if m:
                cands.append((m.group(1), m.group(2)))
    if cands:
        for n, v in cands:
            L.append("    - {:<28} = {}".format(n, v))
    else:
        L.append("    (khong tim thay thuoc tinh boolean nao)")
    L.append("-" * 68)

    # [4] Quet dir(g_i) tim ten lenh lien quan hien/an/chon
    L.append("[4] Quet dir(g_i) tim lenh lien quan hien/an (vis/hid/show/isol/select):")
    try:
        names = [n for n in dir(g_i)]
    except Exception as exc:
        names = []
        L.append("    Loi dir(g_i): {}".format(exc))
    L.append("    (tong so ten g_i tra ve: {})".format(len(names)))
    key = ("vis", "hid", "show", "isol", "select", "displa")
    hits = [n for n in names if any(k in n.lower() for k in key)]
    if hits:
        for n in sorted(hits):
            L.append("    -> {}".format(n))
    else:
        L.append("    (khong co ten nao khop)")
    L.append("-" * 68)

    # [5] Quet dir(obj)
    L.append("[5] Quet dir(doi tuong) tim ten lien quan hien/an:")
    try:
        onames = [n for n in dir(obj)]
    except Exception as exc:
        onames = []
        L.append("    Loi dir(obj): {}".format(exc))
    ohits = [n for n in onames if any(k in n.lower() for k in key)]
    if ohits:
        for n in sorted(ohits):
            L.append("    -> {}".format(n))
    else:
        L.append("    (khong co ten nao khop; tong {} ten)".format(len(onames)))
    L.append("-" * 68)

    # [6] Thu GOI cac lenh hide/show (co the lam an 1 doi tuong - hoi phuc duoc)
    L.append("[6] Thu goi cac lenh hien/an (probe - an thu 1 doi tuong roi hien lai):")
    L.append("    (Neu lenh khong ton tai se bao loi 'unknown command' hoac tuong tu)")
    probe_cmds = ["hide", "show", "hidefromview", "showinview",
                  "setvisible", "visible", "isolate"]
    for cmd in probe_cmds:
        try:
            fn = getattr(g_i, cmd)
        except Exception as exc:
            L.append("    - {:<14}: getattr loi: {}".format(cmd, str(exc)[:120]))
            continue
        try:
            res = fn(obj)
            L.append("    - {:<14}: GOI DUOC! ket qua: {}".format(
                cmd, str(res)[:160]))
        except Exception as exc:
            L.append("    - {:<14}: loi khi goi: {}".format(cmd, str(exc)[:160]))
    # Co gang hien lai doi tuong vua thu an
    for cmd in ("show", "showinview"):
        try:
            getattr(g_i, cmd)(obj)
        except Exception:
            pass
    L.append("=" * 68)
    L.append("HUONG DAN:")
    L.append(" - Neu thay ten ro rang la hien/an (Visible/Show/Hidden...),")
    L.append("   them vao DAU config.VISIBILITY_PROPERTIES roi chay lai Isolate.")
    L.append(" - Neu khong co ten nao phu hop, gui lai TOAN BO file nay + phien")
    L.append("   ban PLAXIS (2D/3D, nam) de duoc tu van huong khac.")
    L.append("=" * 68)
    return "\n".join(L)


def main():
    try:
        report = build_report()
    except Exception:
        report = ("PLAXIS INSPECT gap loi khi chay:\n\n" +
                  traceback.format_exc())
    write_report(report)


main()
