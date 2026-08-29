#!/usr/bin/env python3
"""aF4 PoE trigger enclosure — rev D (PCB hat) — raw OCP.

Modelled in the BOARD frame (same coords as ESP32-PoE-ISO_Rev_N.step), exported
both in-frame (fit check) and origin-translated (printing).

REV D CHANGE OF SHAPE
  The 25x25mm protoboard is gone. In its place a 57 x 50 mm PCB hat plugs onto
  the ESP32's EXT1/EXT2 headers and extends sideways past the board to carry a
  board-mounted barrel jack and 3.5 mm jack, which protrude through the +X wall.
  Deleted from rev C: protoboard bay and its four bosses, the vestigial MP1584EN
  buck pocket, the DC-099 hole in the input wall, and the PG7 gland in the output
  wall. The case loses 38 mm of length and gains 5.5 mm of width.

COORDINATE NOTE
  The hat is designed in KiCad with +Y running the other way. Enclosure Y is the
  negative of the hat's KiCad Y:  enclosure_y = -kicad_y.

MEASURED FACTS
  ESP32 board  x 90.15..118.15, y -188.15..-90, top z 1.578
  RJ45 face    x 101.26..117.14, z 0.758..14.498 @ y=-196.0 (flush plane)
  wings        x 99.06..119.34, z 4.17..11.08, y>=-194.0
  pins         to z=-8.59 below board;  RJ45 top z=16.70
  antenna tip  y=-83.69
  M2 mounts    (97.79,-185.42) (92.71,-117.47) (115.57,-117.47)
  UEXT box hdr 4.40 mm tall (vendor 3D model) — clears the hat easily
"""
import math
from OCP.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax2, gp_Trsf, gp_Ax1
from OCP.BRepPrimAPI import (BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder,
                             BRepPrimAPI_MakeCone, BRepPrimAPI_MakePrism)
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
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

# ============================================================ parameters
WALL, FLOOR, LID_T = 3.0, 2.4, 3.0

# --- the hat, in enclosure coordinates -------------------------------------
HAT_X0, HAT_X1 = 89.15, 146.15          # 57.0 mm wide
HAT_Y0, HAT_Y1 = -160.00, -110.00       # 50.0 mm long (kicad y 110..160)
HAT_T = 1.6
# stack: ESP32 top 1.578 + male header plastic 2.54 + socket body 8.5
HAT_Z = 1.578 + 2.54 + 8.50             # 12.618 -> hat underside
HAT_TOP = HAT_Z + HAT_T                 # 14.218 -> hat top face
HAT_PIN_DROP = 3.4                      # THT pin protrusion below the hat

# jack axes, from the vendor 3D models (see aF4-pcb-notes.md)
J1_Y, J1_AXIS_Z = -116.56, HAT_TOP + 3.60   # barrel jack, body 7.2 tall
J1_FACE_X = 145.28                          # front face of the jack body
J2_Y, J2_AXIS_Z = -148.50, HAT_TOP + 2.50   # 3.5 mm jack, body 5.0 tall
J2_NOSE_X = 148.45                          # nose tip, 6.0 mm dia

# --- interior -------------------------------------------------------------
IX0 = 87.50                              # 1.65 clear of the hat's left edge
IX1 = 146.65                             # 0.50 clear of the hat's right edge
IY0 = -193.00                            # RJ45 flush plane at OY0 = -196.0
IY1 = -82.00                             # 1.7 past the antenna tip (-83.69)
IZ0 = -9.50                              # under-board clearance for THT leads
IZ1 = 23.50                              # 2.1 above the barrel jack's crown
OX0, OX1 = IX0 - WALL, IX1 + WALL
OY0, OY1 = IY0 - WALL, IY1 + WALL
OZ0 = IZ0 - FLOOR
FILLET_R = 3.0

RJX0, RJX1, RJZ0, RJZ1 = 100.76, 117.64, 0.26, 15.0
WGX0, WGX1, WGZ0, WGZ1, WG_D = 98.4, 119.9, 3.5, 11.8, 1.5

# --- wall penetrations for the hat's jacks ---------------------------------
J1_HOLE_D = 7.4          # passes a 5.5 mm plug barrel with room, blocks the body
J1_CBORE_D = 13.0        # outside counterbore: thins the wall so the plug seats
J1_CBORE_T = 1.8         # leaves 1.2 mm of wall -> ~6.9 mm of plug engagement
J2_HOLE_D = 6.6          # 6.0 mm nose + 0.3 clearance per side

# --- mounts ----------------------------------------------------------------
BOSSES_BOARD = [(97.79, -185.42), (92.71, -117.47), (115.57, -117.47)]
# Hat bosses rise from the floor to the hat's underside. They sit in the hat's
# isolation band, at the only X that clears the ESP32's right edge (118.15)
# below and the parts column (from 126.45) above.
BOSSES_HAT = [(123.00, -118.00), (123.50, -147.00)]
HAT_BOSS_D = 7.0
M2_PILOT, M3_PILOT = 1.7, 2.5
LID_BOSS_D, LB_IN = 9.0, 4.0
LID_ZB = 15.0
LID_BOSSES = [
    (IX0 + LB_IN, IY0 + LB_IN, LID_ZB),
    (IX1 - LB_IN, IY0 + LB_IN, LID_ZB),
    (IX0 + LB_IN, IY1 - LB_IN, LID_ZB),
    (IX1 - LB_IN, IY1 - LB_IN, LID_ZB),
]

# --- LED sight holes in the lid (D3 rail-live, D5 feed) --------------------
LED_HOLES = [(139.50, -139.00), (128.20, -150.80)]
LED_HOLE_D = 3.5

# ============================================================ helpers
def box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()

def cyl_z(cx, cy, z0, h, d):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(cx, cy, z0), gp_Dir(0, 0, 1)),
                                    d / 2, h).Shape()

def cyl_x(cy, cz, x0, ln, d):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, cy, cz), gp_Dir(1, 0, 0)),
                                    d / 2, ln).Shape()

def cone_z(cx, cy, ztop, r_top, r_bot, h):
    return BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(cx, cy, ztop - h), gp_Dir(0, 0, 1)),
                                r_bot, r_top, h).Shape()

def fuse(a, b):
    return BRepAlgoAPI_Fuse(a, b).Shape()

def cut(a, b):
    return BRepAlgoAPI_Cut(a, b).Shape()

def common(a, b):
    return BRepAlgoAPI_Common(a, b).Shape()

TD_CAP = 6.0

def teardrop_x(cy, cz, x0, x1, d, cap=TD_CAP):
    """Hole along +X with a truncated 45 deg roof so it prints without support.
    The crown stays under the plug's shoulder / the jack nose, so it is hidden."""
    ln = x1 - x0
    s = cyl_x(cy, cz, x0, ln, d)
    r = d / 2
    k = r * math.sin(math.radians(45))
    apex = r / math.cos(math.radians(45))
    w = apex - cap
    if w <= 0.4:
        w = 0.4
    pts = [gp_Pnt(x0, cy - k, cz + k), gp_Pnt(x0, cy + k, cz + k),
           gp_Pnt(x0, cy + w, cz + cap), gp_Pnt(x0, cy - w, cz + cap)]
    mw = BRepBuilderAPI_MakeWire()
    for i in range(4):
        mw.Add(BRepBuilderAPI_MakeEdge(pts[i], pts[(i + 1) % 4]).Edge())
    f = BRepBuilderAPI_MakeFace(mw.Wire()).Face()
    tri = BRepPrimAPI_MakePrism(f, gp_Vec(ln, 0, 0)).Shape()
    return fuse(s, tri)

def fillet_vertical_edges(shape, r):
    mk = BRepFilletAPI_MakeFillet(shape)
    ex = TopExp_Explorer(shape, TopAbs_ShapeEnum.TopAbs_EDGE)
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
            if (abs(p1.X() - p2.X()) < 1e-6 and abs(p1.Y() - p2.Y()) < 1e-6
                    and abs(p1.Z() - p2.Z()) > 1):
                key = (round(p1.X(), 3), round(p1.Y(), 3))
                if key not in seen:
                    seen.add(key)
                    mk.Add(r, e)
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

# ============================================================ case
outer = box(OX0, OY0, OZ0, OX1, OY1, IZ1)
outer = fillet_vertical_edges(outer, FILLET_R)
case = cut(outer, box(IX0, IY0, IZ0, IX1, IY1, IZ1 + 1))

# RJ45 flush opening + latch-wing relief + top shield-bump relief
case = cut(case, box(RJX0, OY0 - 1, RJZ0, RJX1, IY0 + 0.01, RJZ1))
case = cut(case, box(WGX0, IY0 - WG_D, WGZ0, WGX1, IY0 + 0.01, WGZ1))
case = cut(case, box(104.5, IY0 - WG_D, 14.8, 113.9, IY0 + 0.01, 17.0))

# +X wall: the hat's two jacks
case = cut(case, teardrop_x(J1_Y, J1_AXIS_Z, IX1 - 1, OX1 + 1, J1_HOLE_D))
case = cut(case, cyl_x(J1_Y, J1_AXIS_Z, OX1 - J1_CBORE_T, J1_CBORE_T + 1,
                       J1_CBORE_D))
case = cut(case, teardrop_x(J2_Y, J2_AXIS_Z, IX1 - 1, OX1 + 1, J2_HOLE_D))

# ESP32 board standoffs (top z=0), M2 pilots
for bx, by in BOSSES_BOARD:
    case = fuse(case, cyl_z(bx, by, IZ0, 0.0 - IZ0, 6.0))
    case = cut(case, cyl_z(bx, by, -8.0, 8.01, M2_PILOT))

# hat standoffs: floor up to the hat's underside, M3 pilots
for bx, by in BOSSES_HAT:
    case = fuse(case, cyl_z(bx, by, IZ0, HAT_Z - IZ0, HAT_BOSS_D))
    case = cut(case, cyl_z(bx, by, HAT_Z - 11.0, 11.01, M3_PILOT))
    # gusset into the floor: a tall thin post needs a foot
    case = fuse(case, cone_z(bx, by, IZ0 + 6.0, HAT_BOSS_D / 2,
                             HAT_BOSS_D / 2 + 3.0, 6.0))

# wall-mount tabs, one per long side, flush with the case bottom
TAB_W, TAB_L, TAB_T, TAB_HOLE = 16.0, 12.0, 4.0, 4.5
TYM = (OY0 + OY1) / 2
for wx, sgn in ((OX0, -1), (OX1, 1)):
    tx0, tx1 = sorted((wx, wx + sgn * TAB_L))
    case = fuse(case, box(tx0, TYM - TAB_W / 2, OZ0, tx1, TYM + TAB_W / 2,
                          OZ0 + TAB_T))
    case = cut(case, cyl_z(wx + sgn * (TAB_L - 5.5), TYM, OZ0 - 0.01,
                           TAB_T + 0.02, TAB_HOLE))

# lid bosses, pilot open at the bottom so screws cannot bottom out
for bx, by, zb in LID_BOSSES:
    case = fuse(case, cyl_z(bx, by, zb, IZ1 - zb, LID_BOSS_D))
    case = cut(case, cyl_z(bx, by, zb - 0.01, IZ1 - zb + 0.02, M3_PILOT))

# ============================================================ lid
lid = box(OX0, OY0, IZ1, OX1, OY1, IZ1 + LID_T)
lid = fillet_vertical_edges(lid, FILLET_R)
LIP_L, LIP_T, LIP_H, CLR = 30.0, 1.2, 2.0, 0.25
ymid = (IY0 + IY1) / 2
for lx0 in (IX0 + CLR, IX1 - CLR - LIP_T):
    lid = fuse(lid, box(lx0, ymid - LIP_L / 2, IZ1 - LIP_H, lx0 + LIP_T,
                        ymid + LIP_L / 2, IZ1))
LIP_L2 = 26.0
xmid = (IX0 + IX1) / 2
for ly0 in (IY0 + CLR, IY1 - CLR - LIP_T):
    lid = fuse(lid, box(xmid - LIP_L2 / 2, ly0, IZ1 - LIP_H,
                        xmid + LIP_L2 / 2, ly0 + LIP_T, IZ1))
for bx, by, zb in LID_BOSSES:
    lid = cut(lid, cyl_z(bx, by, IZ1 - 0.01, LID_T + 0.02, 3.4))
    lid = cut(lid, cone_z(bx, by, IZ1 + LID_T + 0.01, 6.8 / 2 + 0.01, 3.4 / 2, 1.71))
# LED sight holes, chamfered on the outside for a wider viewing cone
for lx, ly in LED_HOLES:
    lid = cut(lid, cyl_z(lx, ly, IZ1 - 0.01, LID_T + 0.02, LED_HOLE_D))
    lid = cut(lid, cone_z(lx, ly, IZ1 + LID_T + 0.01,
                          LED_HOLE_D / 2 + 1.2, LED_HOLE_D / 2, 1.21))

# ============================================================ checks
def clear(name, got, want, unit="mm"):
    ok = "OK " if got >= want else "FAIL"
    print("  [%s] %-42s %7.2f %s (want >= %.2f)" % (ok, name, got, unit, want))
    return got >= want

print("rev D enclosure — geometry checks")
ok = True
ok &= clear("hat left edge to interior wall", HAT_X0 - IX0, 1.0)
ok &= clear("hat right edge to interior wall", IX1 - HAT_X1, 0.3)
ok &= clear("hat front edge to interior wall", HAT_Y0 - IY0, 1.0)
ok &= clear("hat back edge to interior wall", IY1 - HAT_Y1, 1.0)
ok &= clear("barrel jack crown to lid underside", IZ1 - (HAT_TOP + 7.2), 1.0)
ok &= clear("hat underside pins to ESP32 top", (HAT_Z - HAT_PIN_DROP) - 1.578, 2.0)
ok &= clear("hat underside pins to UEXT header top", (HAT_Z - HAT_PIN_DROP) - (1.578 + 4.40), 1.0)
ok &= clear("RJ45 crown to lid underside", IZ1 - 16.70, 2.0)
ok &= clear("interior past antenna tip", IY1 - (-83.69), 1.0)
for bx, by in BOSSES_HAT:
    ok &= clear("hat boss %.1f clear of ESP32 edge" % bx,
                bx - HAT_BOSS_D / 2 - 118.15, 0.5)
ok &= clear("J1 plug engagement", 9.5 - ((WALL - J1_CBORE_T) + (IX1 - J1_FACE_X)), 5.0)
ok &= clear("J2 nose recess inside outer face", OX1 - J2_NOSE_X, 0.5)
print("  all geometry checks pass" if ok else "  *** CHECKS FAILED ***")

# solid interference test: does the case body intersect the hat's envelope?
# The bosses are meant to touch each board's underside, so the tests start at
# the plane each board sits on: anything above that is a real collision.
hat_env = box(HAT_X0, HAT_Y0, HAT_Z, HAT_X1, HAT_Y1, HAT_TOP + 7.2)
v1 = volume(common(case, hat_env))
esp_env = box(90.15, -188.15, 0.0, 118.15, -90.0, 1.578 + 4.40)
v2 = volume(common(case, esp_env))
print("  [%s] case intersects hat envelope        %8.3f mm3 (want 0)"
      % ("OK " if v1 < 1e-6 else "FAIL", v1))
print("  [%s] case intersects ESP32 envelope      %8.3f mm3 (want 0)"
      % ("OK " if v2 < 1e-6 else "FAIL", v2))
lid_env = box(IX0, IY0, IZ1, IX1, IY1, IZ1 + LID_T)
v3 = volume(common(lid_env, hat_env))
print("  [%s] lid volume intersects hat envelope  %8.3f mm3 (want 0)"
      % ("OK " if v3 < 1e-6 else "FAIL", v3))

print("case volume cm3:", round(volume(case) / 1000, 1),
      " lid:", round(volume(lid) / 1000, 1))
cb = [round(v, 2) for v in bbox(case)]
print("case bbox:", cb)
print("external: %.1f x %.1f x %.1f mm"
      % (OX1 - OX0, OY1 - OY0, (IZ1 + LID_T) - OZ0))

# ============================================================ export
write_step(case, "af4_case_inframe.step")
write_step(lid, "af4_lid_inframe.step")

case_p = translate(case, -OX0, -OY0, -OZ0)
lid_p = rot_x180(lid)
b = bbox(lid_p)
lid_p = translate(lid_p, -b[0], -b[1], -b[2])

write_stl(case_p, "aF4-trigger-case.stl")
write_stl(lid_p, "aF4-trigger-lid.stl")
write_step(case_p, "aF4-trigger-case.step")
write_step(lid_p, "aF4-trigger-lid.step")
print("exports done")
