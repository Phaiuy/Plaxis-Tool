#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLAXIS Material-Set Selector (2D / 3D)
======================================

Công cụ chọn đối tượng theo Material set (Identification) cho PLAXIS Input.

Chức năng / Behaviour
---------------------
1. Khi CHẠY tool mà ĐANG CHỌN sẵn một số đối tượng trong PLAXIS:
   -> Hiện bảng các Material set (Identification) của riêng những đối tượng
      đang chọn (kèm số lượng đối tượng theo từng material set).

2. Khi CHẠY tool mà KHÔNG chọn đối tượng nào:
   -> Hiện bảng TOÀN BỘ Material set (Identification) đang có trong mô hình.

3. Chọn 1 (hoặc nhiều) dòng material set trong bảng rồi bấm
   "Select objects" -> tool sẽ chọn (highlight) toàn bộ đối tượng trong mô
   hình có material set tương ứng. Đây chính là mục đích "select đối tượng
   theo material set - identification".

Tool dùng chung cho cả PLAXIS 2D và 3D vì đều thông qua Remote Scripting
(plxscripting). Chỉ cần bật "Configure remote scripting server" trong PLAXIS
Input (menu Expert) rồi điền PORT + PASSWORD bên dưới.

Cách chạy
---------
A) Chạy như script Python bên ngoài PLAXIS:
       python plaxis_material_selector.py
   (Nhớ cài: pip install plxscripting  và điền PORT/PASSWORD.)

B) Chạy trực tiếp trong cửa sổ Python của PLAXIS (đã có sẵn biến g_i):
       run_from_plaxis(g_i)

Author: Plaxis-Tool
"""

import sys

# --------------------------------------------------------------------------- #
#  CẤU HÌNH KẾT NỐI  -  chỉnh cho khớp với PLAXIS Input của bạn                #
#  (Expert -> Configure remote scripting server -> lấy Port & Password)       #
# --------------------------------------------------------------------------- #
HOST = "localhost"
PORT = 10000            # cổng remote scripting server của PLAXIS Input
PASSWORD = ""           # mật khẩu remote scripting server

# Tên các collection có thể chứa đối tượng gán được material.
# Không phải phiên bản/không gian (2D/3D) nào cũng có đủ, nên duyệt an toàn.
_OBJECT_COLLECTIONS = (
    "Soils",              # soil volumes
    "Plates",
    "Beams",
    "Geogrids",
    "EmbeddedBeams",
    "EmbeddedBeamRows",
    "NodeToNodeAnchors",
    "FixedEndAnchors",
    "Anchors",
    "Interfaces",
)

# Tên các collection chứa material set trong mô hình.
_MATERIAL_COLLECTIONS = (
    "Materials",
    "SoilMaterials",
    "PlateMaterials",
    "BeamMaterials",
    "GeogridMaterials",
    "EmbeddedBeamMaterials",
    "AnchorMaterials",
    "InterfaceMaterials",
)


# --------------------------------------------------------------------------- #
#  Helpers đọc dữ liệu từ plxscripting một cách "chịu lỗi"                     #
# --------------------------------------------------------------------------- #
def _value(obj):
    """Trả về giá trị nguyên thủy của một property proxy (nếu có .value)."""
    try:
        return obj.value
    except Exception:
        return obj


def _identification(mat):
    """Lấy chuỗi Identification (tên material set) từ một material object."""
    if mat is None:
        return None
    for attr in ("Identification", "Name"):
        try:
            val = _value(getattr(mat, attr))
            if val:
                return str(val)
        except Exception:
            continue
    try:
        return str(mat)
    except Exception:
        return None


def _object_name(obj):
    """Lấy tên hiển thị của một đối tượng trong mô hình."""
    for attr in ("Name", "Identification"):
        try:
            val = _value(getattr(obj, attr))
            if val:
                return str(val)
        except Exception:
            continue
    try:
        return str(obj)
    except Exception:
        return "<object>"


def _object_material(obj, g_i=None):
    """
    Trả về material object gán cho `obj`, hoặc None nếu không có.

    Xử lý cả trường hợp .Material là property thường lẫn property phụ thuộc
    giai đoạn (staged) - khi đó thử đọc theo từng phase.
    """
    try:
        mat = _value(obj.Material)
    except Exception:
        mat = None

    # Nếu đọc trực tiếp đã ra material có Identification -> dùng luôn.
    if mat is not None and _identification(mat) is not None:
        return mat

    # Fallback: material gán theo phase (staged construction).
    if g_i is not None:
        try:
            phases = list(g_i.Phases)
        except Exception:
            phases = []
        for ph in phases:
            try:
                staged = _value(obj.Material[ph])
            except Exception:
                staged = None
            if staged is not None and _identification(staged) is not None:
                return staged
    return mat


def _iter_collection(g_i, name):
    """Duyệt an toàn một collection trên g_i theo tên; bỏ qua nếu không có."""
    try:
        coll = getattr(g_i, name)
    except Exception:
        return
    try:
        for item in coll:
            yield item
    except Exception:
        return


# --------------------------------------------------------------------------- #
#  Lõi nghiệp vụ                                                               #
# --------------------------------------------------------------------------- #
class MaterialSelector(object):
    """Bao bọc mọi thao tác với mô hình PLAXIS thông qua g_i."""

    def __init__(self, g_i):
        self.g_i = g_i

    # -- Đọc selection hiện tại ------------------------------------------- #
    def get_selection(self):
        """Trả về list đối tượng đang được chọn trong PLAXIS Input."""
        try:
            return [o for o in self.g_i.selection]
        except Exception:
            return []

    # -- Danh sách toàn bộ đối tượng có material trong mô hình ------------- #
    def iter_model_objects(self):
        """Sinh ra (yield) toàn bộ đối tượng có thể gán material trong mô hình."""
        seen = set()
        for coll_name in _OBJECT_COLLECTIONS:
            for obj in _iter_collection(self.g_i, coll_name):
                key = id(obj)
                if key in seen:
                    continue
                seen.add(key)
                yield obj

    # -- Bảng material set của các đối tượng đang chọn -------------------- #
    def table_for_objects(self, objects):
        """
        Nhận list đối tượng -> trả về dict:
            { identification: {"objects": [obj, ...], "type": <material type>} }
        """
        table = {}
        for obj in objects:
            mat = _object_material(obj, self.g_i)
            ident = _identification(mat) or "<no material>"
            entry = table.setdefault(ident, {"objects": [], "type": _material_type(mat)})
            entry["objects"].append(obj)
        return table

    # -- Bảng toàn bộ material set trong mô hình -------------------------- #
    def table_all_materials(self):
        """
        Trả về dict giống table_for_objects nhưng cho TẤT CẢ material set khai
        báo trong mô hình. "objects" là các đối tượng thực sự đang dùng set đó.
        """
        # 1) Khởi tạo từ mọi material set đã khai báo (kể cả set chưa dùng).
        table = {}
        seen_mat = set()
        for coll_name in _MATERIAL_COLLECTIONS:
            for mat in _iter_collection(self.g_i, coll_name):
                if id(mat) in seen_mat:
                    continue
                seen_mat.add(id(mat))
                ident = _identification(mat)
                if ident is None:
                    continue
                table.setdefault(ident, {"objects": [], "type": _material_type(mat)})

        # 2) Đếm đối tượng đang dùng từng material set.
        for obj in self.iter_model_objects():
            mat = _object_material(obj, self.g_i)
            ident = _identification(mat)
            if ident is None:
                continue
            entry = table.setdefault(ident, {"objects": [], "type": _material_type(mat)})
            entry["objects"].append(obj)
        return table

    # -- Chọn đối tượng theo (các) identification ------------------------- #
    def objects_with_identifications(self, identifications):
        """Trả về list đối tượng trong mô hình có material set thuộc `identifications`."""
        wanted = set(identifications)
        result = []
        for obj in self.iter_model_objects():
            mat = _object_material(obj, self.g_i)
            ident = _identification(mat)
            if ident in wanted:
                result.append(obj)
        return result

    def select_objects(self, objects):
        """Đặt selection của PLAXIS Input thành đúng `objects`."""
        g_i = self.g_i
        # Cách 1 (được plxscripting hỗ trợ chính thức): gán trực tiếp.
        try:
            g_i.selection = list(objects)
            return True
        except Exception:
            pass
        # Cách 2: xoá sạch rồi append từng cái.
        try:
            try:
                del g_i.selection[:]
            except Exception:
                pass
            for obj in objects:
                g_i.selection.append(obj)
            return True
        except Exception:
            return False


def _material_type(mat):
    """Cố gắng đọc loại material (SoilModel / MaterialType) để hiển thị thêm."""
    if mat is None:
        return ""
    for attr in ("MaterialType", "TypeName", "SoilModel"):
        try:
            val = _value(getattr(mat, attr))
            if val:
                return str(val)
        except Exception:
            continue
    return ""


# --------------------------------------------------------------------------- #
#  Kết nối tới PLAXIS                                                          #
# --------------------------------------------------------------------------- #
def connect(host=HOST, port=PORT, password=PASSWORD):
    """
    Kết nối tới PLAXIS Input remote scripting server, trả về (s_i, g_i).
    Raise nếu thiếu plxscripting hoặc không kết nối được.
    """
    try:
        from plxscripting.easy import new_server
    except ImportError as exc:
        raise RuntimeError(
            "Chưa cài plxscripting. Chạy: pip install plxscripting"
        ) from exc

    kwargs = {}
    if password:
        kwargs["password"] = password
    s_i, g_i = new_server(host, port, **kwargs)
    return s_i, g_i


# --------------------------------------------------------------------------- #
#  Giao diện bảng (tkinter)                                                    #
# --------------------------------------------------------------------------- #
def show_gui(selector, title_suffix, table, on_select):
    """
    Hiện cửa sổ bảng material set.

    table       : dict { identification: {"objects": [...], "type": str} }
    on_select   : callback(list_identifications) -> chọn đối tượng trong PLAXIS.
    """
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except Exception:
        # Không có tkinter -> in ra console.
        print_table(title_suffix, table)
        return

    root = tk.Tk()
    root.title("PLAXIS - Material Set Selector")
    root.geometry("620x460")

    header = tk.Label(
        root,
        text=title_suffix,
        font=("Segoe UI", 11, "bold"),
        anchor="w",
        justify="left",
        wraplength=590,
        pady=8,
        padx=10,
    )
    header.pack(fill="x")

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=10, pady=(0, 8))

    columns = ("identification", "type", "count")
    tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="extended")
    tree.heading("identification", text="Material set (Identification)")
    tree.heading("type", text="Type / Model")
    tree.heading("count", text="Objects")
    tree.column("identification", width=320, anchor="w")
    tree.column("type", width=180, anchor="w")
    tree.column("count", width=70, anchor="center")

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    for ident in sorted(table.keys(), key=lambda s: s.lower()):
        entry = table[ident]
        tree.insert(
            "",
            "end",
            iid=ident,
            values=(ident, entry.get("type", ""), len(entry["objects"])),
        )

    # -- Thanh nút bên dưới ------------------------------------------------ #
    btn_bar = tk.Frame(root)
    btn_bar.pack(fill="x", padx=10, pady=(0, 10))

    status = tk.Label(root, text="", anchor="w", fg="#046307", padx=10)
    status.pack(fill="x", side="bottom")

    def do_select():
        idents = list(tree.selection())
        if not idents:
            messagebox.showinfo(
                "Chưa chọn material set",
                "Hãy chọn ít nhất một dòng material set trong bảng.",
            )
            return
        try:
            n = on_select(idents)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Lỗi", "Không chọn được đối tượng:\n%s" % exc)
            return
        status.config(
            text="Đã chọn %d đối tượng theo material set: %s"
            % (n, ", ".join(idents))
        )

    def do_refresh():
        root.destroy()
        run(selector.g_i)  # chạy lại toàn bộ luồng để cập nhật selection/model

    tk.Button(btn_bar, text="Select objects", width=16, command=do_select).pack(
        side="left"
    )
    tk.Button(btn_bar, text="Refresh", width=10, command=do_refresh).pack(
        side="left", padx=6
    )
    tk.Button(btn_bar, text="Close", width=10, command=root.destroy).pack(
        side="right"
    )

    root.mainloop()


def print_table(title_suffix, table):
    """In bảng ra console (fallback khi không có GUI)."""
    print("\n" + "=" * 70)
    print(title_suffix)
    print("=" * 70)
    header = "{:<40} {:<18} {:>6}".format("Material set (Identification)", "Type", "Objs")
    print(header)
    print("-" * 70)
    for ident in sorted(table.keys(), key=lambda s: s.lower()):
        entry = table[ident]
        print(
            "{:<40} {:<18} {:>6}".format(
                ident[:40], str(entry.get("type", ""))[:18], len(entry["objects"])
            )
        )
    print("=" * 70 + "\n")


# --------------------------------------------------------------------------- #
#  Luồng chính                                                                 #
# --------------------------------------------------------------------------- #
def run(g_i):
    """
    Luồng chính khi đã có g_i:
      - Có selection  -> bảng material set của các đối tượng đang chọn.
      - Không selection -> bảng toàn bộ material set trong mô hình.
    """
    selector = MaterialSelector(g_i)
    selection = selector.get_selection()

    if selection:
        table = selector.table_for_objects(selection)
        title = (
            "Đang chọn %d đối tượng.\n"
            "Bảng Material set (Identification) của các đối tượng đang chọn:"
            % len(selection)
        )
    else:
        table = selector.table_all_materials()
        title = (
            "Không có đối tượng nào được chọn.\n"
            "Bảng TOÀN BỘ Material set (Identification) trong mô hình:"
        )

    def on_select(idents):
        objs = selector.objects_with_identifications(idents)
        selector.select_objects(objs)
        return len(objs)

    show_gui(selector, title, table, on_select)


def run_from_plaxis(g_i):
    """Gọi hàm này khi chạy trực tiếp trong cửa sổ Python của PLAXIS."""
    run(g_i)


def main():
    """Điểm vào khi chạy như script độc lập bên ngoài PLAXIS."""
    try:
        _, g_i = connect()
    except Exception as exc:  # noqa: BLE001
        print("Không kết nối được PLAXIS: %s" % exc, file=sys.stderr)
        print(
            "Kiểm tra: đã bật remote scripting server trong PLAXIS Input chưa, "
            "PORT/PASSWORD trong file có đúng không, plxscripting đã cài chưa.",
            file=sys.stderr,
        )
        sys.exit(1)
    run(g_i)


if __name__ == "__main__":
    main()
