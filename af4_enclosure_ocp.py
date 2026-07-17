#!/usr/bin/env python3
"""aF4 PoE trigger enclosure (ESP32-POE-ISO + AQY212 protoboard) — raw OCP.
Modeled in the BOARD frame (same coords as ESP32-PoE-ISO_Rev_N.step), exported
both in-frame (fit check) and origin-translated (printing).

Measured board facts:
  board   x 90.15..118.15, y -188.15..-90, top z 1.578
  RJ45    face x 101.26..117.14, z 0.758..14.498 @ y=-196.0 (flush plane)
  wings   x 99.06..119.34, z 4.17..11.08, y>=-194.0
  pins    to z=-8.59 below board;  RJ45 top z=16.70; headers z=13.15
  antenna tip y=-83.69
  M2 mount holes (97.79,-185.42) (92.71,-117.47) (115.57,-117.47)
"""
import math
from OCP.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax2, gp_Trsf, gp_Ax1
from OCP.BRepPrimAPI import (BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder,
                             BRepPrimAPI_MakeCone, BRepPrimAPI_MakePrism)
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
from OCP.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire,
                                BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform)
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_ShapeEnum
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.STEPControl import STEPControl_Writer, STEPControl_StepModelType
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

# ---------------- parameters ----------------
WALL, FLOOR, LID_T = 3.0, 2.4, 3.0
IX0, IX1 = 74.5, 120.2   # left wall pushed out 4mm for PG7 locknut clearance
IY0, IY1 = -197.0, -44.0  # input wall pushed out 4mm (v2 fit check: gland nut+stub protrude
                          # 5.0mm past inner face; old 4.85mm wall-to-board gap => board rode
                          # the nut. Now nut face y=-192.0, board edge -188.15: 3.85mm clear.
                          # RJ45 jack face (y=-196) recesses 1mm behind inner face — plug
                          # reaches it through the wall tunnel).
                          # output wall pushed out 14mm: gland nut + cable zone in front of protoboard
IZ0, IZ1 = -9.5, 27.0
OX0, OX1 = IX0 - WALL, IX1 + WALL
OY0, OY1 = IY0 - WALL, IY1 + WALL          # OY0=-200.0; RJ45 face (y=-196) recessed 4mm
OZ0 = IZ0 - FLOOR
FILLET_R = 3.0

# RJ45 tunnel: jack face is now 4mm behind the outer plane, so the opening is a
# through-tunnel the plug body/boot must pass. Width 16.88 clears any snagless
# boot (~13.5); z opened up to -1.5..16.5 for boot + latch clearance.
RJX0, RJX1, RJZ0, RJZ1 = 100.76, 117.64, -1.5, 16.5

GLAND_D = 12.6
G1X, G1Z = 86.0, 4.0     # nut edge (r~10.5) : 11.0 to left wall, 2.6 to RJ45 wing (x=99.06)
CX = (IX0 + IX1) / 2
G2X, G2Z = CX, 4.0

BOSSES_BOARD = [(97.79, -185.42), (92.71, -117.47), (115.57, -117.47)]
# 6 perfboard grid pitches (15.24mm) so mount holes land on the 2.54mm grid
PB = 15.24 / 2
BOSSES_PROTO = [(CX - PB, -70 - PB), (CX + PB, -70 - PB), (CX - PB, -70 + PB), (CX + PB, -70 + PB)]
PROTO_H = 6.0
M2_PILOT, M3_PILOT = 1.7, 2.5
LID_BOSS_D, LB_IN = 9.0, 4.0
LID_BOSSES = [
    (IX0 + LB_IN, IY0 + LB_IN, 18.0),
    (IX1 - LB_IN, IY0 + LB_IN, 18.0),
    (IX0 + LB_IN, IY1 - LB_IN, 15.0),
    (IX1 - LB_IN, IY1 - LB_IN, 15.0),
]

# ---------------- helpers ----------------
def box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()

def cyl_z(cx, cy, z0, h, d):
    ax = gp_Ax2(gp_Pnt(cx, cy, z0), gp_Dir(0, 0, 1))
    return BRepPrimAPI_MakeCylinder(ax, d / 2, h).Shape()

def cyl_y(cx, cz, y0, ln, d):
    ax = gp_Ax2(gp_Pnt(cx, y0, cz), gp_Dir(0, 1, 0))
    return BRepPrimAPI_MakeCylinder(ax, d / 2, ln).Shape()

def cone_z(cx, cy, ztop, r_top, r_bot, h):
    """cone from z=ztop-h (r_bot) up to ztop (r_top)"""
    ax = gp_Ax2(gp_Pnt(cx, cy, ztop - h), gp_Dir(0, 0, 1))
    return BRepPrimAPI_MakeCone(ax, r_bot, r_top, h).Shape()

def fuse(a, b):
    return BRepAlgoAPI_Fuse(a, b).Shape()

def cut(a, b):
    return BRepAlgoAPI_Cut(a, b).Shape()

TD_CAP = 6.8  # truncated-teardrop crown height above hole center: stays under the
              # PG7 hex body (~7.5mm across flats) and locknut (~9.5mm), flat bridge ~4.2mm

def teardrop_y(cx, cz, y0, y1, d):
    """hole along +Y with truncated 45deg roof (support-free, fully covered by gland)"""
    ln = y1 - y0
    s = cyl_y(cx, cz, y0, ln, d)
    r = d / 2
    k = r * math.sin(math.radians(45))
    apex = r / math.cos(math.radians(45))
    w = apex - TD_CAP  # half-width of flat crown
    pts = [gp_Pnt(cx - k, y0, cz + k), gp_Pnt(cx + k, y0, cz + k),
           gp_Pnt(cx + w, y0, cz + TD_CAP), gp_Pnt(cx - w, y0, cz + TD_CAP)]
    mw = BRepBuilderAPI_MakeWire()
    for i in range(4):
        mw.Add(BRepBuilderAPI_MakeEdge(pts[i], pts[(i + 1) % 4]).Edge())
    f = BRepBuilderAPI_MakeFace(mw.Wire()).Face()
    tri = BRepPrimAPI_MakePrism(f, gp_Vec(0, ln, 0)).Shape()
    return fuse(s, tri)

def fillet_vertical_edges(shape, r):
    mk = BRepFilletAPI_MakeFillet(shape)
    ex = TopExp_Explorer(shape, TopAbs_ShapeEnum.TopAbs_EDGE)
    n = 0
    seen = set()
    while ex.More():
        e = TopoDS.Edge_s(ex.Current())
        vx = TopExp_Explorer(e, TopAbs_ShapeEnum.TopAbs_VERTEX)
        pts = []
        while vx.More():
            pts.append(BRep_Tool.Pnt_s(TopoDS.Vertex_s(vx.Current())))
            vx.Next()
        if len(pts) == 2:
            p1, p2 = pts
            if abs(p1.X() - p2.X()) < 1e-6 and abs(p1.Y() - p2.Y()) < 1e-6 and abs(p1.Z() - p2.Z()) > 1:
                key = (round(p1.X(), 3), round(p1.Y(), 3))
                if key not in seen:
                    seen.add(key)
                    mk.Add(r, e)
                    n += 1
        ex.Next()
    return mk.Shape()

def volume(s):
    p = GProp_GProps(); BRepGProp.VolumeProperties_s(s, p)
    return p.Mass()

def bbox(s):
    b = Bnd_Box(); BRepBndLib.Add_s(s, b)
    return b.Get()

def write_step(shape, path):
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_StepModelType.STEPControl_AsIs)
    w.Write(path)

def write_stl(shape, path):
    BRepMesh_IncrementalMesh(shape, 0.02, False, 0.3, True)
    sw = StlAPI_Writer(); sw.ASCIIMode = False
    sw.Write(shape, path)

def translate(shape, dx, dy, dz):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, dy, dz))
    return BRepBuilderAPI_Transform(shape, t, True).Shape()

def rot_x180(shape):
    t = gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi)
    return BRepBuilderAPI_Transform(shape, t, True).Shape()

# ---------------- case ----------------
outer = box(OX0, OY0, OZ0, OX1, OY1, IZ1)
outer = fillet_vertical_edges(outer, FILLET_R)
case = cut(outer, box(IX0, IY0, IZ0, IX1, IY1, IZ1 + 1))

# RJ45 tunnel (jack recessed; wings at y>=-194.0 and the top shield bump now sit
# fully inside the cavity — the old inner-face relief pockets are no longer needed)
case = cut(case, box(RJX0, OY0 - 1, RJZ0, RJX1, IY0 + 0.01, RJZ1))

# gland holes
case = cut(case, teardrop_y(G1X, G1Z, OY0 - 1, IY0 + 1, GLAND_D))
case = cut(case, teardrop_y(G2X, G2Z, IY1 - 1, OY1 + 1, GLAND_D))

# board standoffs (top z=0), M2 pilots
for bx, by in BOSSES_BOARD:
    case = fuse(case, cyl_z(bx, by, IZ0, 0.0 - IZ0, 6.0))
    case = cut(case, cyl_z(bx, by, -8.0, 8.01, M2_PILOT))

# protoboard bosses
for bx, by in BOSSES_PROTO:
    case = fuse(case, cyl_z(bx, by, IZ0, PROTO_H, 6.0))
    case = cut(case, cyl_z(bx, by, IZ0 + PROTO_H - 5.5, 5.51, M2_PILOT))

# --- buck converter drop-in pocket (measured from actual MP1584EN STEP model) ---
# Module: 22.4 x 17.1, PCB 1.6, components to 4.6 total; back face is FLAT bare PCB.
# Both long edges and the short-edge middles carry components; corner pads get
# solder + wires. Nothing may grip any edge => pocket touches ONLY the flat back
# and the bottom edge face:
#   - back flat against wall (0.3 gap), landscape, pot side up/front
#   - bottom PCB edge rests on a shelf (shelf stops before the component zone)
#   - side fences beyond the board ends (0.4 play, no contact)
#   - flexible front post, centered, with a stepped snap nub over the top-front;
#     module drops in from above, post flexes ~0.5mm, nub prevents lift/tip-out
BUCK_CY = -139.0
MOD_HALF = 11.2            # half of 22.4 length (along wall)
MOD_BOT = -5.5             # bottom edge resting height
MOD_TOP = MOD_BOT + 17.1   # 11.6
PCB_BACK = IX0 + 0.3       # 74.8
PCB_FRONT = PCB_BACK + 1.6 # 76.4
COMP_FRONT = PCB_BACK + 4.6  # 79.4 (tallest component face)
# shelf: supports PCB strip only (stops 0.2 past PCB front)
case = fuse(case, box(IX0, BUCK_CY - MOD_HALF - 1.3, IZ0,
                      PCB_FRONT + 0.2, BUCK_CY + MOD_HALF + 1.3, MOD_BOT))
# side fences (0.4 play each end, 2.4 thick, full component depth + 0.8)
for sgn in (-1, 1):
    fy = BUCK_CY + sgn * (MOD_HALF + 0.4)
    fy2 = fy + sgn * 2.4
    case = fuse(case, box(IX0, min(fy, fy2), IZ0, COMP_FRONT + 0.8, max(fy, fy2), 8.0))
# front snap post: moved 1.2 inboard after v1 fit check (was COMP_FRONT+0.5 —
# nub tip barely reached the component plane, no real engagement). Inner face
# now 0.7 PAST the tallest-component plane: light press contact, real retention.
POST_INSET = 1.2
POST_T = 2.0                   # thinned from 2.2: needs ~1.5mm flex on insert
POST_X0 = COMP_FRONT + 0.5 - POST_INSET   # 78.7
case = fuse(case, box(POST_X0, BUCK_CY - 3.0, IZ0, POST_X0 + POST_T, BUCK_CY + 3.0, MOD_TOP + 1.8))
# stepped nub (points toward wall, hooks over top-front components; 1.2 deep,
# 1.4 tall lip, 3-step staircase = insert lead-in)
case = fuse(case, box(POST_X0 - 0.4, BUCK_CY - 3.0, MOD_TOP + 0.2, POST_X0, BUCK_CY + 3.0, MOD_TOP + 1.6))
case = fuse(case, box(POST_X0 - 0.8, BUCK_CY - 3.0, MOD_TOP + 0.2, POST_X0, BUCK_CY + 3.0, MOD_TOP + 1.1))
case = fuse(case, box(POST_X0 - 1.2, BUCK_CY - 3.0, MOD_TOP + 0.2, POST_X0, BUCK_CY + 3.0, MOD_TOP + 0.6))

# wall-mount tabs: one per long side, centered along Y, flush with case bottom
TAB_W, TAB_L, TAB_T = 16.0, 12.0, 4.0   # width along wall, protrusion, thickness
TAB_HOLE = 4.5                           # #8 / M4 clearance
TYM = (OY0 + OY1) / 2
for wx, sgn in ((OX0, -1), (OX1, 1)):
    tx0, tx1 = sorted((wx, wx + sgn * TAB_L))
    case = fuse(case, box(tx0, TYM - TAB_W / 2, OZ0, tx1, TYM + TAB_W / 2, OZ0 + TAB_T))
    case = cut(case, cyl_z(wx + sgn * (TAB_L - 5.5), TYM, OZ0 - 0.01, TAB_T + 0.02, TAB_HOLE))

# lid bosses, pilot open at bottom
for bx, by, zb in LID_BOSSES:
    case = fuse(case, cyl_z(bx, by, zb, IZ1 - zb, LID_BOSS_D))
    case = cut(case, cyl_z(bx, by, zb - 0.01, IZ1 - zb + 0.02, M3_PILOT))

# ---------------- lid ----------------
lid = box(OX0, OY0, IZ1, OX1, OY1, IZ1 + LID_T)
lid = fillet_vertical_edges(lid, FILLET_R)
LIP_L, LIP_T, LIP_H, CLR = 30.0, 1.2, 2.0, 0.25
ymid = (IY0 + IY1) / 2
for lx0 in (IX0 + CLR, IX1 - CLR - LIP_T):
    lid = fuse(lid, box(lx0, ymid - LIP_L / 2, IZ1 - LIP_H, lx0 + LIP_T, ymid + LIP_L / 2, IZ1))
# short-side lips: 26mm (not 30) so the ends clear the O9 corner lid bosses by ~1.4mm
LIP_L2 = 26.0
xmid = (IX0 + IX1) / 2
for ly0 in (IY0 + CLR, IY1 - CLR - LIP_T):
    lid = fuse(lid, box(xmid - LIP_L2 / 2, ly0, IZ1 - LIP_H, xmid + LIP_L2 / 2, ly0 + LIP_T, IZ1))
for bx, by, zb in LID_BOSSES:
    lid = cut(lid, cyl_z(bx, by, IZ1 - 0.01, LID_T + 0.02, 3.4))
    lid = cut(lid, cone_z(bx, by, IZ1 + LID_T + 0.01, 6.8 / 2 + 0.01, 3.4 / 2, 1.71))

# ---------------- report + export ----------------
print("case volume cm3:", round(volume(case) / 1000, 1), " lid:", round(volume(lid) / 1000, 1))
print("case bbox:", [round(v, 2) for v in bbox(case)])
print("lid bbox:", [round(v, 2) for v in bbox(lid)])

write_step(case, "af4_case_inframe.step")
write_step(lid, "af4_lid_inframe.step")

case_p = translate(case, -OX0, -OY0, -OZ0)
lid_p = rot_x180(lid)                       # flip: top face to bed
b = bbox(lid_p)
lid_p = translate(lid_p, -b[0], -b[1], -b[2])

write_stl(case_p, "aF4-trigger-case.stl")
write_stl(lid_p, "aF4-trigger-lid.stl")
write_step(case_p, "aF4-trigger-case.step")
write_step(lid_p, "aF4-trigger-lid.step")
print("exports done")
