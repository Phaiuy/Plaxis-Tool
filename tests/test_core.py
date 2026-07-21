# -*- coding: utf-8 -*-
"""
Kiem thur logic core bang mot PLAXIS gia lap (mock) - khong can PLAXIS that.

Chay: python tests/test_core.py
"""

import os
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from plaxis_isolate import core, config


# --------------------------------------------------------------------------
#  Mock PLAXIS proxy
# --------------------------------------------------------------------------
class Prop(object):
    """Gia lap proxy thuoc tinh PLAXIS: co .value va .set()."""
    def __init__(self, owner, name, value):
        self._owner = owner
        self._name = name
        self.value = value

    def set(self, value):
        self.value = value
        self._owner._store[self._name] = value


class MockObj(object):
    def __init__(self, name, visible=True):
        self._store = {"Name": name, "Visible": visible}

    def __getattr__(self, item):
        # Chi cac thuoc tinh nam trong _store moi ton tai (giong PLAXIS that:
        # truy cap thuoc tinh khong co se raise).
        store = object.__getattribute__(self, "_store")
        if item in store:
            return Prop(self, item, store[item])
        raise AttributeError(item)

    def __str__(self):
        return self._store["Name"]


class MockCollection(list):
    pass


class MockProject(object):
    def __init__(self, name):
        self._store = {"Title": name}

    def __getattr__(self, item):
        store = object.__getattribute__(self, "_store")
        if item in store:
            return Prop(self, item, store[item])
        raise AttributeError(item)


class MockGi(object):
    """Gia lap g_i: co selection, cac collection, Project va set()."""
    def __init__(self, objects, selection, project="TestProj"):
        self.Points = MockCollection(objects)
        self.selection = MockCollection(selection)
        self.Project = MockProject(project)

    def set(self, prop, value):
        # Ho tro cach goi 1: g_i.set(obj.Prop, value)
        prop.set(value)


# --------------------------------------------------------------------------
#  Tien ich
# --------------------------------------------------------------------------
def vis(obj):
    return obj._store["Visible"]


def check(cond, msg):
    if not cond:
        raise AssertionError("FAIL: " + msg)
    print("  ok - " + msg)


def clean_state(g_i):
    core._clear_state(g_i)


# --------------------------------------------------------------------------
#  Cac test
# --------------------------------------------------------------------------
def test_isolate_hides_others():
    print("test_isolate_hides_others")
    a = MockObj("A", visible=True)
    b = MockObj("B", visible=True)
    c = MockObj("C", visible=True)
    g_i = MockGi([a, b, c], selection=[b])
    clean_state(g_i)

    res = core.isolate(g_i, verbose=False)

    check(vis(b) is True, "doi tuong dang chon (B) van hien")
    check(vis(a) is False, "A bi an")
    check(vis(c) is False, "C bi an")
    check(res["kept"] == 1 and res["hidden"] == 2, "tom tat: 1 giu, 2 an")
    clean_state(g_i)


def test_isolate_multi_selection():
    print("test_isolate_multi_selection")
    objs = [MockObj(n) for n in "ABCD"]
    g_i = MockGi(objs, selection=[objs[0], objs[2]])  # chon A & C
    clean_state(g_i)

    core.isolate(g_i, verbose=False)

    check(vis(objs[0]) is True, "A hien")
    check(vis(objs[2]) is True, "C hien")
    check(vis(objs[1]) is False, "B an")
    check(vis(objs[3]) is False, "D an")
    clean_state(g_i)


def test_unisolate_restores_state():
    print("test_unisolate_restores_state")
    a = MockObj("A", visible=True)
    b = MockObj("B", visible=False)  # B von da bi an tu truoc
    c = MockObj("C", visible=True)
    g_i = MockGi([a, b, c], selection=[a])
    clean_state(g_i)

    core.isolate(g_i, verbose=False)
    check(vis(a) is True and vis(b) is False and vis(c) is False,
          "sau isolate: chi A hien")

    core.unisolate(g_i, verbose=False)
    check(vis(a) is True, "khoi phuc: A hien (nhu cu)")
    check(vis(b) is False, "khoi phuc: B van an (dung trang thai cu)")
    check(vis(c) is True, "khoi phuc: C hien lai (nhu cu)")
    clean_state(g_i)


def test_isolate_no_selection_raises():
    print("test_isolate_no_selection_raises")
    g_i = MockGi([MockObj("A")], selection=[])
    clean_state(g_i)
    try:
        core.isolate(g_i, verbose=False)
        raise AssertionError("FAIL: dang le phai bao loi khi khong co selection")
    except RuntimeError as exc:
        check("Chua chon" in str(exc), "bao loi ro rang khi chua chon gi")
    clean_state(g_i)


def test_show_all():
    print("test_show_all")
    objs = [MockObj(n, visible=False) for n in "ABC"]
    g_i = MockGi(objs, selection=[])
    core.show_all(g_i, verbose=False)
    check(all(vis(o) is True for o in objs), "tat ca deu hien sau show_all")
    clean_state(g_i)


def test_unisolate_without_state_shows_all():
    print("test_unisolate_without_state_shows_all")
    objs = [MockObj(n, visible=False) for n in "ABC"]
    g_i = MockGi(objs, selection=[])
    clean_state(g_i)  # chac chan khong co file trang thai
    core.unisolate(g_i, verbose=False)
    check(all(vis(o) is True for o in objs),
          "khong co state -> hien tat ca")
    clean_state(g_i)


def main():
    tests = [
        test_isolate_hides_others,
        test_isolate_multi_selection,
        test_unisolate_restores_state,
        test_isolate_no_selection_raises,
        test_show_all,
        test_unisolate_without_state_shows_all,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as exc:
            failed += 1
            print("  " + str(exc))
    print("-" * 50)
    if failed:
        print("KET QUA: {} test THAT BAI".format(failed))
        sys.exit(1)
    print("KET QUA: tat ca {} test PASS".format(len(tests)))


if __name__ == "__main__":
    main()
