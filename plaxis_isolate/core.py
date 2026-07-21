# -*- coding: utf-8 -*-
"""
Loi (core) cho PLAXIS Isolate Tool.

Cung cap 3 chuc nang chinh, dung chung cho ca PLAXIS 2D va 3D:

    isolate(g_i=None)    -> chi hien doi tuong dang chon, an tat ca phan con lai
    unisolate(g_i=None)  -> khoi phuc lai trang thai hien/an truoc khi isolate
    show_all(g_i=None)   -> hien tat ca doi tuong (khong can file trang thai)

Thiet ke de chay o CA HAI moi truong:

  * NHUNG trong PLAXIS (Expert > Python / Run Python Tool): PLAXIS da cung cap
    s5n bien toan cuc `g_i`. Truyen thang no vao, hoac de tool tu tim.
  * STANDALONE (chay tu Python ben ngoai): tool tu mo ket noi toi remote
    scripting server dua theo cau hinh trong config.py.

Ma nguon co chu dich "phong thu" (defensive) vi API hien/an cua PLAXIS co the
khac nhau giua cac phien ban; xem config.VISIBILITY_PROPERTIES.
"""

from __future__ import print_function

import json
import os
import tempfile

try:
    from . import config
except (ImportError, ValueError):  # chay truc tiep, khong phai dang package
    import config


# ===========================================================================
#  Ghi log (print() cua PLAXIS tool KHONG hien tren man hinh -> ghi ra file)
# ===========================================================================
_LOG_PATH = [None]  # cache duong dan file log da chon


def _log_targets():
    targets = []
    try:
        home = os.path.expanduser("~")
    except Exception:
        home = None
    if home:
        targets.append(os.path.join(home, "Desktop", config.LOG_FILENAME))
        targets.append(os.path.join(home, config.LOG_FILENAME))
    try:
        targets.append(os.path.join(tempfile.gettempdir(), config.LOG_FILENAME))
    except Exception:
        pass
    return targets


def _choose_log_path():
    if _LOG_PATH[0] is not None:
        return _LOG_PATH[0]
    for path in _log_targets():
        parent = os.path.dirname(path)
        if parent and not os.path.isdir(parent):
            continue
        try:
            with open(path, "a"):
                pass
            _LOG_PATH[0] = path
            return path
        except Exception:
            continue
    _LOG_PATH[0] = ""  # khong ghi duoc file nao
    return ""


def log_reset(title):
    """Bat dau mot phien log moi (ghi de file cu), voi tieu de + thoi diem."""
    if not getattr(config, "LOG_TO_FILE", True):
        return
    import datetime
    path = _choose_log_path()
    if not path:
        return
    try:
        with open(path, "w") as fh:
            fh.write("=== {} === {}\n".format(title, datetime.datetime.now()))
    except Exception:
        pass


def log(msg=""):
    """In ra stdout VA ghi vao file log (de nguoi dung xem duoc trong PLAXIS)."""
    try:
        print(msg)
    except Exception:
        pass
    if not getattr(config, "LOG_TO_FILE", True):
        return
    path = _choose_log_path()
    if not path:
        return
    try:
        with open(path, "a") as fh:
            fh.write(msg + "\n")
    except Exception:
        pass


def log_path():
    """Tra ve duong dan file log dang dung (de bao cho nguoi dung)."""
    return _LOG_PATH[0] or ""


# ===========================================================================
#  Ket noi / lay g_i
# ===========================================================================
def get_g_i(g_i=None):
    """Tra ve doi tuong global input `g_i`.

    Thu tu uu tien:
      1. Tham so `g_i` truyen vao.
      2. Bien toan cuc `g_i` co s5n (khi chay ben trong PLAXIS).
      3. Mo ket noi moi toi remote scripting server (khi chay standalone).
    """
    if g_i is not None:
        return g_i

    # Dang chay ben trong PLAXIS? -> g_i thuong nam trong builtins/globals.
    injected = _find_injected_g_i()
    if injected is not None:
        return injected

    # Chay ngoai -> ket noi remote scripting server.
    return _connect_new_server()


def _find_injected_g_i():
    """Tim bien `g_i` do PLAXIS bom vao moi truong khi chay Expert tool."""
    try:
        import builtins  # Python 3
    except ImportError:  # Python 2
        import __builtin__ as builtins
    if hasattr(builtins, "g_i"):
        return getattr(builtins, "g_i")

    # Mot so phien ban bom vao globals cua __main__.
    try:
        import __main__
        if hasattr(__main__, "g_i"):
            return getattr(__main__, "g_i")
    except Exception:
        pass
    return None


def _connect_new_server():
    """Mo ket noi standalone toi PLAXIS Input qua plxscripting."""
    try:
        from plxscripting.easy import new_server
    except ImportError:
        raise RuntimeError(
            "Khong tim thay module 'plxscripting'. Hay chay tool nay ben trong "
            "PLAXIS (Expert > Python), hoac cai dat plxscripting va bat remote "
            "scripting server (Expert > Configure remote scripting server...)."
        )

    last_err = None
    for port in config.INPUT_PORTS:
        try:
            kwargs = {"timeout": config.CONNECT_TIMEOUT}
            if config.PASSWORD:
                kwargs["password"] = config.PASSWORD
            s_i, g_i = new_server(config.HOST, port, **kwargs)
            # Cham nhe de chac chan ket noi song.
            _ = s_i.name
            print("Da ket noi PLAXIS tai {}:{}".format(config.HOST, port))
            return g_i
        except Exception as exc:  # thu port tiep theo
            last_err = exc
            continue

    raise RuntimeError(
        "Khong the ket noi PLAXIS tren cac port {}. "
        "Kiem tra remote scripting server da bat va dung Host/Port/Password "
        "trong config.py. Loi cuoi: {}".format(config.INPUT_PORTS, last_err)
    )


# ===========================================================================
#  Doc / ghi thuoc tinh hien-an (defensive theo phien ban PLAXIS)
# ===========================================================================
def _get_property(obj, name):
    """Tra ve proxy thuoc tinh `name` cua `obj`, hoac None neu khong co."""
    try:
        prop = getattr(obj, name)
    except Exception:
        return None
    return prop


def _read_value(prop):
    """Doc gia tri boolean tu mot proxy thuoc tinh PLAXIS."""
    # Proxy PLAXIS thuong co `.value`; du phong dung truc tiep.
    for attr in ("value",):
        if hasattr(prop, attr):
            try:
                return bool(getattr(prop, attr))
            except Exception:
                pass
    try:
        return bool(prop)
    except Exception:
        return None


def find_visibility_property(obj):
    """Tim ten thuoc tinh hien/an dung duoc tren `obj`.

    Tra ve (ten, gia_tri_hien_tai) hoac (None, None) neu doi tuong nay khong
    co thuoc tinh hien/an nao trong danh sach config.VISIBILITY_PROPERTIES.
    """
    for name in config.VISIBILITY_PROPERTIES:
        prop = _get_property(obj, name)
        if prop is None:
            continue
        val = _read_value(prop)
        if val is not None:
            return name, val
    return None, None


def _set_property(g_i, obj, name, value):
    """Dat thuoc tinh `name` = `value`, thu nhieu cach goi theo API PLAXIS."""
    prop = _get_property(obj, name)

    # Cach 1 (pho bien nhat): g_i.set(obj.Prop, value)
    if prop is not None:
        try:
            g_i.set(prop, value)
            return True
        except Exception:
            pass

    # Cach 2: g_i.set(obj, "Prop", value)
    try:
        g_i.set(obj, name, value)
        return True
    except Exception:
        pass

    # Cach 3: obj.Prop.set(value)
    if prop is not None and hasattr(prop, "set"):
        try:
            prop.set(value)
            return True
        except Exception:
            pass

    # Cach 4: gan truc tiep
    try:
        setattr(obj, name, value)
        return True
    except Exception:
        pass

    return False


def set_visible(g_i, obj, visible):
    """Dat trang thai hien/an cho mot doi tuong. Tra ve True neu thanh cong."""
    name, _cur = find_visibility_property(obj)
    if name is None:
        return False
    return _set_property(g_i, obj, name, bool(visible))


# ===========================================================================
#  Nhan dien doi tuong
# ===========================================================================
def _obj_key(obj):
    """Sinh khoa dinh danh on dinh cho doi tuong (uu tien Name)."""
    for attr in ("Name",):
        prop = _get_property(obj, attr)
        if prop is not None:
            val = None
            try:
                val = prop.value
            except Exception:
                try:
                    val = str(prop)
                except Exception:
                    val = None
            if val:
                return str(val)
    # Du phong: dung repr/id
    try:
        return str(obj)
    except Exception:
        return "obj_{}".format(id(obj))


def get_selection(g_i):
    """Lay danh sach doi tuong dang duoc chon trong giao dien PLAXIS."""
    try:
        sel = g_i.selection
    except Exception as exc:
        raise RuntimeError(
            "Khong doc duoc vung chon (g_i.selection): {}".format(exc)
        )
    try:
        return list(sel)
    except Exception:
        # Mot so proxy khong iterate truc tiep -> ep ve list qua len/index.
        result = []
        try:
            for i in range(len(sel)):
                result.append(sel[i])
        except Exception:
            pass
        return result


def collect_all_objects(g_i):
    """Duyet cac collection trong config va gom tat ca doi tuong (da khu trung)."""
    seen = {}
    ordered = []
    for coll_name in config.ISOLATABLE_COLLECTIONS:
        coll = _get_property(g_i, coll_name)
        if coll is None:
            continue
        try:
            items = list(coll)
        except Exception:
            continue
        for obj in items:
            key = _obj_key(obj)
            if key in seen:
                continue
            seen[key] = obj
            ordered.append(obj)
    return ordered


# ===========================================================================
#  Luu / khoi phuc trang thai
# ===========================================================================
def _state_path(g_i):
    directory = config.STATE_DIR or tempfile.gettempdir()
    try:
        os.makedirs(directory)
    except Exception:
        pass
    project_key = _project_key(g_i)
    fname = config.STATE_FILENAME
    if project_key:
        base, ext = os.path.splitext(fname)
        fname = "{}_{}{}".format(base, project_key, ext)
    return os.path.join(directory, fname)


def _project_key(g_i):
    """Sinh khoa an toan (chi chu/so) tu ten project de tach file trang thai."""
    name = None
    for path in ("Project.Filename", "Project.Title", "Project.Name"):
        obj = g_i
        try:
            for part in path.split("."):
                obj = getattr(obj, part)
            name = getattr(obj, "value", None) or str(obj)
            if name:
                break
        except Exception:
            continue
    if not name:
        return ""
    safe = "".join(c if c.isalnum() else "_" for c in os.path.basename(str(name)))
    return safe[:60]


def _save_state(g_i, records):
    path = _state_path(g_i)
    try:
        with open(path, "w") as fh:
            json.dump(records, fh)
    except Exception as exc:
        log("Canh bao: khong luu duoc trang thai ({}). "
            "Unisolate se chi 'hien tat ca'.".format(exc))


def _load_state(g_i):
    path = _state_path(g_i)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as fh:
            return json.load(fh)
    except Exception:
        return None


def _clear_state(g_i):
    path = _state_path(g_i)
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# ===========================================================================
#  Cac lenh chinh
# ===========================================================================
def isolate(g_i=None, verbose=True):
    """Chi hien doi tuong dang chon; an tat ca doi tuong con lai.

    Tra ve dict tom tat: {hidden, kept, skipped}.
    """
    g_i = get_g_i(g_i)
    if verbose:
        log_reset("ISOLATE")

    selection = get_selection(g_i)
    if not selection:
        msg = ("Chua chon doi tuong nao. Hay chon it nhat mot doi tuong tren "
               "vung ve (hoac trong Model explorer) roi chay lai Isolate.")
        if verbose:
            log(msg)
        raise RuntimeError(msg)

    selected_keys = set(_obj_key(o) for o in selection)
    all_objects = collect_all_objects(g_i)

    records = []      # trang thai truoc do de khoi phuc
    hidden = 0
    kept = 0
    skipped = 0

    for obj in all_objects:
        key = _obj_key(obj)
        prop_name, cur_vis = find_visibility_property(obj)
        if prop_name is None:
            skipped += 1
            continue

        # Ghi lai trang thai cu (du no la doi tuong dang chon hay khong).
        records.append({"key": key, "prop": prop_name, "visible": bool(cur_vis)})

        want_visible = key in selected_keys
        if want_visible:
            if cur_vis is not True:
                set_visible(g_i, obj, True)
            kept += 1
        else:
            if cur_vis is not False:
                set_visible(g_i, obj, False)
            hidden += 1

    # Dam bao chinh cac doi tuong dang chon luon hien (ke ca khi khong nam
    # trong cac collection da liet ke).
    for obj in selection:
        prop_name, _ = find_visibility_property(obj)
        if prop_name is not None:
            set_visible(g_i, obj, True)

    _save_state(g_i, records)

    if verbose:
        log("Isolate xong: giu hien {} | an {} | bo qua (khong co thuoc tinh "
            "hien/an) {}.".format(kept, hidden, skipped))
        if hidden == 0 and (skipped > 0 or kept > 0):
            log("")
            log("!!! KHONG AN DUOC DOI TUONG NAO.")
            log("    Phien ban PLAXIS cua ban dung ten thuoc tinh hien/an khac "
                "voi mac dinh (Visible/Visibility/Show/Shown), hoac khong ho "
                "tro dieu khien hien/an tu Python.")
            log("    => Chay 'plx_inspect.py' (chon 1 doi tuong roi chay) de "
                "PLAXIS liet ke dung ten thuoc tinh, sau do them ten do vao "
                "DAU config.VISIBILITY_PROPERTIES.")
        if log_path():
            log("(Ket qua nay duoc ghi tai: {})".format(log_path()))

    return {"hidden": hidden, "kept": kept, "skipped": skipped}


def unisolate(g_i=None, verbose=True):
    """Khoi phuc trang thai hien/an nhu truoc khi isolate.

    Neu khong tim thay file trang thai -> chuyen sang show_all().
    """
    g_i = get_g_i(g_i)
    if verbose:
        log_reset("UNISOLATE")

    records = _load_state(g_i)
    if not records:
        if verbose:
            log("Khong co trang thai da luu -> hien tat ca doi tuong.")
        return show_all(g_i, verbose=verbose)

    index = {_obj_key(o): o for o in collect_all_objects(g_i)}
    restored = 0
    missing = 0
    for rec in records:
        obj = index.get(rec.get("key"))
        if obj is None:
            missing += 1
            continue
        if set_visible(g_i, obj, rec.get("visible", True)):
            restored += 1

    _clear_state(g_i)

    if verbose:
        log("Unisolate xong: khoi phuc {} doi tuong"
            "{}.".format(restored,
                         " (bo qua {} khong tim thay)".format(missing)
                         if missing else ""))
        if log_path():
            log("(Ket qua nay duoc ghi tai: {})".format(log_path()))
    return {"restored": restored, "missing": missing}


def show_all(g_i=None, verbose=True):
    """Hien tat ca doi tuong (khong phu thuoc file trang thai)."""
    g_i = get_g_i(g_i)
    shown = 0
    for obj in collect_all_objects(g_i):
        if set_visible(g_i, obj, True):
            shown += 1
    _clear_state(g_i)
    if verbose:
        log("Da hien lai {} doi tuong.".format(shown))
        if log_path():
            log("(Ket qua nay duoc ghi tai: {})".format(log_path()))
    return {"shown": shown}
