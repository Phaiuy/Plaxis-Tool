# -*- coding: utf-8 -*-
"""
Cau hinh cho PLAXIS Isolate Tool.

Chinh cac gia tri o day cho phu hop voi may / phien ban PLAXIS cua ban.
Khi tool chay NHUNG BEN TRONG PLAXIS (Expert menu) thi phan ket noi ben duoi
KHONG duoc dung toi (vi da co s5n bien `g_i`); chi khi chay NGOAI (standalone)
tool moi mo ket noi toi remote scripting server bang cac tham so nay.
"""

# ---------------------------------------------------------------------------
# 1) Ket noi toi Remote Scripting Server (chi dung khi chay STANDALONE ngoai PLAXIS)
# ---------------------------------------------------------------------------
# Bat server trong PLAXIS: Expert > Configure remote scripting server...
# roi dien dung Host / Port / Password ma PLAXIS hien thi.
HOST = "localhost"

# PLAXIS 2D va 3D deu cho phep tu chon port. Neu ban chay dong thoi ca 2D & 3D
# hay dat port khac nhau. Tool se thu lan luot cac port trong danh sach nay.
INPUT_PORTS = [10000, 10001]

# Mat khau do PLAXIS sinh ra khi bat scripting server. De trong "" neu server
# duoc cau hinh khong dung mat khau.
PASSWORD = ""

# Thoi gian cho khi ket noi (giay).
CONNECT_TIMEOUT = 10.0

# ---------------------------------------------------------------------------
# 2) Thuoc tinh dieu khien hien/an cua doi tuong
# ---------------------------------------------------------------------------
# PLAXIS o cac phien ban khac nhau co the dung ten thuoc tinh khac nhau de
# dieu khien hien thi doi tuong tren vung ve. Tool se thu lan luot cac ten
# duoi day va dung cai dau tien "chay duoc" tren doi tuong.
#
# Neu phien ban PLAXIS cua ban dung ten khac, chi can them vao dau danh sach.
VISIBILITY_PROPERTIES = ["Visible", "Visibility", "Show", "Shown"]

# ---------------------------------------------------------------------------
# 3) Cac collection (nhom doi tuong) duoc coi la "co the isolate"
# ---------------------------------------------------------------------------
# Day la "vu tru" doi tuong ma tool se duyet qua de an (tru phan dang chon).
# Tool guard tung ten -> collection nao khong ton tai trong model se bo qua,
# nen co the liet ke rong rai cho ca 2D lan 3D ma khong loi.
ISOLATABLE_COLLECTIONS = [
    # --- Hinh hoc co ban ---
    "Points", "Lines", "Polygons", "Surfaces", "Volumes",
    # --- Dat / borehole ---
    "Soils", "SoilVolumes", "Boreholes",
    # --- Ket cau ---
    "Plates", "Beams", "Geogrids",
    "EmbeddedBeams", "EmbeddedBeamRows", "EmbeddedPiles",
    "Anchors", "NodeToNodeAnchors", "FixedEndAnchors",
    "Interfaces", "PositiveInterfaces", "NegativeInterfaces",
    # --- Tai trong ---
    "PointLoads", "LineLoads", "SurfaceLoads", "Loads",
    # --- Dieu kien nuoc / thoat nuoc ---
    "Wells", "Drains", "LineDrains", "SurfaceDrains",
    # --- Prescribed displacement ---
    "PointPrescribedDisplacements",
    "LinePrescribedDisplacements",
    "SurfacePrescribedDisplacements",
]

# ---------------------------------------------------------------------------
# 4) Luu / khoi phuc trang thai
# ---------------------------------------------------------------------------
# Khi isolate, tool luu lai trang thai hien/an truoc do ra file tam de lenh
# Unisolate co the khoi phuc chinh xac. De None de dung thu muc temp mac dinh.
STATE_DIR = None  # None -> tempfile.gettempdir()
STATE_FILENAME = "plaxis_isolate_state.json"
