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

2026-09-18 CHANGE — 12 V INPUT MOVED TO A PANEL JACK
  The rev E boards arrived with J1, the board-mounted barrel jack, rotated 180
  deg: gen_pcb.py places it at rot 270, which aims CUI's bore (footprint-local
  y +10.32) at board x 133.68 — into the middle of the hat. All five boards are
  built that way. They are used AS BUILT: J1 stays fitted and dead, and the 12 V
  feed is taken from its pads on the hat's UNDERSIDE (pad 1 +12V_RAW at y -121.0,
  pad 2 GNDP at y -112.5, both outboard of the ESP32's right edge, so there is
  open air under them) to a panel-mount jack in the +X wall. The old J1
  penetration is gone and the wall is solid there. See §A4.

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
  TALL PARTS under the hat, calipered 2026-09-16 from the board's BOTTOM face
  (z = 0 here, the plane the M2 standoffs stop at):
    electrolytic cap beside DCDC1  13.4   (vendor model 13.15)
    DCDC1 isolated power module     11.5   (vendor model 11.99)
    UEXT1 box header                11.2   (vendor model 11.53)
  Until 2026-09-16 this line read "UEXT box hdr 4.40 mm tall — clears the hat
  easily". It was wrong by ~7 mm, and it left the cap 0.78 mm INTO the hat.
  The hat was raised 1.5 mm (HAT_LIFT) to fix it. See §6.3 of the master ref.
"""
import math
import numpy as np
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

# ---- OCP 7.x / 8.x compatibility ------------------------------------------
# cadquery-ocp 8 (OCCT 8) dropped the "_s" suffix on static methods, made
# Bnd_Box.Get() return an unbound Limits struct, and removed
# NCollection_Utf8String. Resolve each once here so the geometry code below
# runs unchanged on either major version.
def _static(cls, name):
    f = getattr(cls, name + "_s", None)
    return f if f is not None else getattr(cls, name)

def _bbox6(b):
    lo, hi = b.CornerMin(), b.CornerMax()
    return (lo.X(), lo.Y(), lo.Z(), hi.X(), hi.Y(), hi.Z())

def _stl_binary(sw):
    try:
        sw.ASCIIMode = False
    except AttributeError:
        sw.SetASCIIMode(False)
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
# stack: ESP32 top 1.578 + male header plastic 2.54 + socket body 8.5 + lift.
# HAT_LIFT floats the sockets 1.5 mm above the header plastic so the hat clears
# the electrolytic cap beside DCDC1 (top z 13.4, measured). The hat is carried
# by its two M3 standoffs, not by the header plastic, so nothing needs to bear
# on the gap. Cost: pin engagement drops from ~5.8 to ~4.3 mm.
HAT_LIFT = 1.50
HAT_Z = 1.578 + 2.54 + 8.50 + HAT_LIFT  # 14.118 -> hat underside
HAT_TOP = HAT_Z + HAT_T                 # 15.718 -> hat top face
HDR_PLASTIC_TOP = 1.578 + 2.54          # 4.118
HDR_PIN_ABOVE = 5.84                    # standard 0.1" header mating length
SOCKET_H = 8.50

# Tall parts on the Olimex top face that sit under (or beside) the hat.
# x/y from ESP32-PoE-ISO_Rev_N.stl, enclosure frame; top z MEASURED 2026-09-16
# from the ESP32's bottom face with calipers. Measured values govern.
TALL_PARTS = [
    # name,                          x0,     y0,      x1,     y1,     top z
    ("UEXT1 box header",             94.00, -129.00, 114.50, -119.50, 11.2),
    ("DCDC1 power module",           98.70, -155.00, 118.10, -148.00, 11.5),
    ("electrolytic cap by DCDC1",   111.50, -161.50, 118.50, -155.00, 13.4),
]
TALL_MAX_Z = max(t[5] for t in TALL_PARTS)
HAT_PIN_DROP = 3.4                      # THT pin protrusion below the hat

# jack axes, from the vendor 3D models (see aF4-pcb-notes.md)
J2_Y, J2_AXIS_Z = -148.50, HAT_TOP + 2.50   # 3.5 mm jack, body 5.0 tall
J2_NOSE_X = 148.45                          # nose tip, 6.0 mm dia

# J1 is still FITTED to the hat — dead, bore facing inward, 7.2 mm tall — so it
# still needs room under the lid. It no longer penetrates any wall.
J1_BODY_H = 7.2
# Kept so the verifier can prove the old hole is CLOSED in the printed case:
J1_OLD_Y, J1_OLD_AXIS_Z, J1_OLD_HOLE_D = -116.56, HAT_TOP + 3.60, 7.4
# ...and as a warning. J1_OLD_Y is the jack BODY centre (footprint-local x
# -4.45). The bore axis is at local x -3.19, i.e. y -117.81, so this hole was
# 1.25 mm off axis against 0.95 mm of radial slack in a 7.4 mm bore: the plug
# would have fouled the wall even had the jack faced outward. A second datum
# taken by hand rather than from the part, same family as the 4.40 mm UEXT
# height. Rev F takes it from the model.

# --- interior -------------------------------------------------------------
IX0 = 87.50                              # 1.65 clear of the hat's left edge
IX1 = 146.65                             # 0.50 clear of the hat's right edge
IY0 = -193.00                            # RJ45 flush plane at OY0 = -196.0
IY1 = -82.00                             # 1.7 past the antenna tip (-83.69)
IZ0 = -9.50                              # under-board clearance for THT leads
IZ1 = 25.00                              # 2.1 above the barrel jack's crown (23.50 before HAT_LIFT)
OX0, OX1 = IX0 - WALL, IX1 + WALL
OY0, OY1 = IY0 - WALL, IY1 + WALL
OZ0 = IZ0 - FLOOR
FILLET_R = 3.0

RJX0, RJX1, RJZ0, RJZ1 = 100.76, 117.64, 0.26, 15.0
WGX0, WGX1, WGZ0, WGZ1, WG_D = 98.4, 119.9, 3.5, 11.8, 1.5

# --- wall penetrations for the hat's jacks ---------------------------------
J2_HOLE_D = 6.6          # 6.0 mm nose + 0.3 clearance per side
# J1's Ø7.4 hole and its Ø13 x 1.8 outside counterbore are deliberately absent.

# --- 12 V input: panel-mount jack in the +X wall ---------------------------
# POSITION. The window is bounded by the hat's near edge (HAT_Y0 = -160.0) and
# the -Y/+X lid boss (centre -189.0, Ø9 -> edge -184.5). PJ_Y sits mid-window.
# PJ_AXIS_Z keeps the whole jack below the hat plane (HAT_Z = 14.118) so the
# cable run to J1's pads passes under the hat, and 15.5 mm above the floor.
PJ_Y      = -172.50
PJ_AXIS_Z = 6.00

# THE PART: DALQUIS DC-099, 5.5 x 2.5 mm, 10 A, threaded panel mount, with
# 150 mm of 18 AWG pre-soldered leads -- RED IS +12 V, BLACK IS -, recorded on
# both rev C protoboard diagrams in archive/. Six in hand; rev C used this same
# part before the hat existed. Calipered by Kenny 2026-09-18 except as marked.
PJ_BARREL_D = 11.50      # threaded barrel, full diameter         [MEAS]
PJ_FLAT_H   = 10.50      # flat face to the opposite arc          [MEAS]
PJ_FLANGE_T =  1.50      # flange thickness                       [MEAS]
PJ_NUT_T    =  3.00      # nut thickness                          [MEAS]
PJ_NUT_AF   = 14.00      # nut across flats                       [MEAS]
PJ_NUT_AC   = 15.80      # nut across corners                     [MEAS]
PJ_THREAD_L =  9.00      # [VENDOR DRAWING] The drawing gives 2 + 9 + 9 against
                         # a stated 20 mm overall. The competing reading -- that
                         # the two 9s are diameters -- is ruled out by the
                         # calipered 11.5 mm barrel, so these are axial.
PJ_BODY_L   = 20.00      # [VENDOR DRAWING] overall length. Worst case: the
                         # whole part sitting inboard of the wall.
PJ_FLANGE_D = 16.00      # [ASSUMED UPPER BOUND] not calipered. Both only feed
PJ_BODY_D   = 13.00      # [ASSUMED UPPER BOUND] the clearance envelope, which
                         # the nut's 15.8 across-corners dominates anyway.
                         # Anything up to Ø20 still passes every check.
PJ_DIMS_VERIFIED = True

# RETENTION. The barrel carries a FLAT, so the part keys itself and no captive
# nut is needed: flange outside, 3.0 mm wall, nut inside, 9 - 3 - 3 = 3.0 mm of
# thread to spare. The wall hole is a D with the FLAT UP, which also makes its
# roof a flat bridge rather than a curved overhang -- so unlike J2 this hole
# needs no teardrop crown, and its envelope stays inside Ø11.9 where any
# plausible flange covers it.
#
# The pad-and-captive-hex-pocket scheme this block carried until the part was
# measured is gone. The manufacturer's flat does that job better, and the hex
# pocket would have eaten the wall the flange clamps.
PJ_FIT      = 0.40                                   # printed-hole clearance
PJ_HOLE_D   = PJ_BARREL_D + PJ_FIT                   # 11.90
PJ_FLAT_Z   = (PJ_FLAT_H + PJ_FIT) - PJ_HOLE_D / 2   # 4.95 above the axis
PJ_ENV_D    = max(PJ_BODY_D, PJ_FLANGE_D, PJ_NUT_AC)

# CABLE TIE POST. The 12 V pair is soldered to J1's pad tails on the hat's
# underside, which is the weakest joint in the whole repair. Anchor the cable
# here, between the jack and the hat, so nothing can pull on those tails.
TIE_X, TIE_Y = 143.00, -161.50
TIE_W, TIE_T, TIE_H = 7.0, 2.4, 6.0     # along y, along x, above the floor
TIE_SLOT_W, TIE_SLOT_H, TIE_SLOT_Z = 4.0, 2.2, 2.0

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

# --- LED sight holes in the lid -------------------------------------------
# Both sets now take a 3 mm PMMA rod light pipe. The bore is stepped: a
# clearance hole from the lid underside that lands on a smaller aperture at the
# top face, so the rod drops in from inside, seats on the step, and cannot fall
# through onto the LED. A bead of clear epoxy at the inner face retains and
# seals it -- better ingress-wise than the open holes this replaces.
#
# WHY PIPES AND NOT PLAIN HOLES. The hat's LEDs sit on HAT_TOP, 8.5 mm under
# the lid: a plain 3.5 mm hole gave an 11.6 deg viewing half-angle, which works.
# The Olimex LEDs are 21.2 mm down and the same hole gives 4.7 deg -- a
# look-at-it-dead-on-or-not-at-all indicator. Widening does not rescue it
# (4.5 mm only reaches 6.1 deg); the air gap is the limiter, not the aperture.
#
#   hat  D3 (GRN, rail live) and D5 (YEL, feed) -- 0805 on the hat top
#   PoE  PWR1 (RED, 3V3 rail) and LNK1 (GRN, ethernet link) -- 0603 on the
#        Olimex board. x/y read straight out of ESP32-PoE-ISO_Rev_N.step,
#        which is authored in this same frame. All four of its LEDs sit in one
#        column at x = 91.567 on a 5.715 mm pitch.
#
# The other two Olimex LEDs are deliberately absent:
#   ACT1  (y = -159.639) is 0.361 mm INSIDE the hat footprint (HAT_Y0 = -160.0)
#         and is blindfolded by 1.6 mm of opaque FR4. Nothing in the lid can
#         see it -- do not add a hole here.
#   CHRG1 (y = -176.784) is the LiPo charge LED and there is no battery in this
#         build. U3 (SOT-23-5) is also only 2.9 mm away, which a 3 mm pipe
#         would foul.
LED_HOLES_HAT = [(139.50, -139.00), (128.20, -150.80)]
LED_HOLES_POE = [(91.567, -171.069), (91.567, -165.354)]
LED_PIPE_D = 3.50            # rod clearance bore. 1/8" acrylic rod is sold as
                             # "3 mm" and runs 3.0-3.3 extruded, so this stays
                             # loose on purpose and the epoxy fills the annulus.
LED_APERTURE_D = 2.60        # aperture at the top face; the rod seats on it
LED_APERTURE_T = 0.90        # thickness of the aperture land
LED_Z_HAT = HAT_TOP + 0.70   # emitting face of an 0805 on the hat top
LED_Z_POE = 2.30             # emitting face of an 0603 on the Olimex board
LED_PIPE_GAP = 0.60          # pipe tip to LED: close, never touching

# --- engraved lid label ----------------------------------------------------
# Upright with the box held PORTRAIT: RJ45 end away from you, the two jacks on
# the left (Kenny's mockup, 2026-09-16). In the enclosure frame, looking down
# on the lid, that is text reading along -X with its top toward -Y (the RJ45
# end), i.e. LID_LABEL_ROT = 180. It read along +Y (ROT 90, landscape with the
# cable end on the left) until then. In the clear +Y half, away from every
# sight hole and boss counterbore. The lid prints top-face-down (rot_x180 at
# export), so this recess lands on the bed and comes out crisp.
LID_LINES = ["aF4 PoE", "Feed Trigger"]
LID_LABEL_ROT = 180          # degrees CCW from +X: the direction the text reads
LID_LABEL_SIZE = 6.5         # "Feed Trigger" is 45.4 mm here, across a 65.2 mm lid
LID_LABEL_DEPTH = 0.8
LID_LABEL_WEIGHT = "bold"
LID_LABEL_LEADING = 1.30
LID_LABEL_CX = 117.00        # centre of the block, lid X
LID_LABEL_CY = -108.00       # centre of the block, lid Y

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
        e = _static(TopoDS, 'Edge')(ex.Current())
        vx = TopExp_Explorer(e, TopAbs_ShapeEnum.TopAbs_VERTEX)
        pts = []
        while vx.More():
            pts.append(_static(BRep_Tool, 'Pnt')(_static(TopoDS, 'Vertex')(vx.Current())))
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
    p = GProp_GProps(); _static(BRepGProp, 'VolumeProperties')(s, p)
    return p.Mass()

def bbox(s):
    b = Bnd_Box(); _static(BRepBndLib, 'Add')(s, b)
    return _bbox6(b)

def write_step(shape, path):
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_StepModelType.STEPControl_AsIs)
    w.Write(path)

def write_stl(shape, path):
    BRepMesh_IncrementalMesh(shape, 0.02, False, 0.3, True)
    sw = StlAPI_Writer(); _stl_binary(sw)
    sw.Write(shape, path)

def translate(shape, dx, dy, dz):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, dy, dz))
    return BRepBuilderAPI_Transform(shape, t, True).Shape()

def rot_x180(shape):
    t = gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi)
    return BRepBuilderAPI_Transform(shape, t, True).Shape()

# ---- engraved text -------------------------------------------------------
# Same idiom as the Temp Junction Box / display-temp scripts: glyph outlines
# come from matplotlib's TextPath (DejaVu Sans ships with matplotlib, so the
# result is identical on any machine), then each closed loop is extruded in OCP
# and the counters are booleaned out. No shapely needed here.

def _glyph_loops(lines, size, leading):
    """Closed 2D loops for a block of text, centred on its own bounding box.

    Returns (outer_loops, hole_loops) in glyph space: +x along the reading
    direction, +y up the page.
    """
    try:
        from matplotlib.textpath import TextPath
        from matplotlib.font_manager import FontProperties
    except ImportError:                                   # pragma: no cover
        raise SystemExit("lid engraving needs matplotlib (pip install matplotlib)")
    fp = FontProperties(family="DejaVu Sans", weight=LID_LABEL_WEIGHT)
    step = size * leading
    total = step * (len(lines) - 1)
    loops = []
    for i, s in enumerate(lines):
        tp = TextPath((0, 0), s, size=size, prop=fp)
        raw = [np.asarray(p) for p in tp.to_polygons() if len(p) >= 4]
        if not raw:
            continue
        allpts = np.vstack(raw)
        dx = -(allpts[:, 0].min() + allpts[:, 0].max()) / 2.0   # centre this line
        dy = total / 2.0 - i * step
        for p in raw:
            loops.append(p + np.array([dx, dy]))
    if not loops:
        return [], []
    allpts = np.vstack(loops)
    dy = -(allpts[:, 1].min() + allpts[:, 1].max()) / 2.0       # centre the block
    loops = [p + np.array([0.0, dy]) for p in loops]

    def signed_area(p):
        x, y = p[:, 0], p[:, 1]
        return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)

    outers = [p for p in loops if signed_area(p) < 0]
    holes = [p for p in loops if signed_area(p) >= 0]
    return outers, holes

def _rot_label(p, rot):
    """Glyph space (+x reads, +y up) -> lid plan, rotated `rot` degrees CCW."""
    c = round(math.cos(math.radians(rot)), 12)
    s_ = round(math.sin(math.radians(rot)), 12)
    return (c * p[0] - s_ * p[1], s_ * p[0] + c * p[1])

def _loop_prism(pts, cx, cy, z0, h, rot=None):
    """Extrude one closed loop, text reading `rot` degrees CCW from +X."""
    rot = LID_LABEL_ROT if rot is None else rot
    mw = BRepBuilderAPI_MakeWire()
    q = [_rot_label(p, rot) for p in pts]
    q = [(x + cx, y + cy) for x, y in q]
    if math.hypot(q[0][0] - q[-1][0], q[0][1] - q[-1][1]) < 1e-9:
        q = q[:-1]
    n = len(q)
    added = 0
    for i in range(n):
        a, b = q[i], q[(i + 1) % n]
        if math.hypot(a[0] - b[0], a[1] - b[1]) < 1e-9:
            continue
        mw.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(a[0], a[1], z0),
                                       gp_Pnt(b[0], b[1], z0)).Edge())
        added += 1
    if added < 3:
        return None
    f = BRepBuilderAPI_MakeFace(mw.Wire(), True).Face()
    return BRepPrimAPI_MakePrism(f, gp_Vec(0, 0, h)).Shape()

def engrave(shape, lines, size, depth, cx, cy, ztop, leading=1.30):
    """Cut `lines` into the +Z face of `shape` at height `ztop`."""
    outers, holes = _glyph_loops(lines, size, leading)
    if not outers:
        return shape
    z0, h = ztop - depth, depth + 0.5
    text = None
    for p in outers:
        s = _loop_prism(p, cx, cy, z0, h)
        if s is not None:
            text = s if text is None else fuse(text, s)
    for p in holes:
        s = _loop_prism(p, cx, cy, z0 - 0.1, h + 0.2)
        if s is not None and text is not None:
            text = cut(text, s)
    print("  engraved %s  (%d outlines, %d counters)"
          % (" / ".join(lines), len(outers), len(holes)))
    return cut(shape, text)

# ============================================================ case
outer = box(OX0, OY0, OZ0, OX1, OY1, IZ1)
outer = fillet_vertical_edges(outer, FILLET_R)
case = cut(outer, box(IX0, IY0, IZ0, IX1, IY1, IZ1 + 1))

# RJ45 flush opening + latch-wing relief + top shield-bump relief
case = cut(case, box(RJX0, OY0 - 1, RJZ0, RJX1, IY0 + 0.01, RJZ1))
case = cut(case, box(WGX0, IY0 - WG_D, WGZ0, WGX1, IY0 + 0.01, WGZ1))
case = cut(case, box(104.5, IY0 - WG_D, 14.8, 113.9, IY0 + 0.01, 17.0))

# +X wall: the hat's 3.5 mm trigger jack. J1's barrel hole is deliberately
# absent — see the 2026-09-18 change note at the top of this file.
case = cut(case, teardrop_x(J2_Y, J2_AXIS_Z, IX1 - 1, OX1 + 1, J2_HOLE_D))

# +X wall: the 12 V panel jack. A D-hole keyed to the barrel's flat, FLAT UP:
# bore it round, then put the wall back above the flat plane. Flat up means the
# roof is a flat bridge, so this hole wants no teardrop.
case = cut(case, cyl_x(PJ_Y, PJ_AXIS_Z, IX1 - 1, (OX1 - IX1) + 2, PJ_HOLE_D))
_fy = PJ_HOLE_D / 2 + 0.50
case = fuse(case, box(IX1, PJ_Y - _fy, PJ_AXIS_Z + PJ_FLAT_Z,
                      OX1, PJ_Y + _fy, PJ_AXIS_Z + _fy))

# cable tie post on the floor, between the panel jack and the hat
case = fuse(case, box(TIE_X - TIE_T / 2, TIE_Y - TIE_W / 2, IZ0,
                      TIE_X + TIE_T / 2, TIE_Y + TIE_W / 2, IZ0 + TIE_H))
case = cut(case, box(TIE_X - TIE_T, TIE_Y - TIE_SLOT_W / 2, IZ0 + TIE_SLOT_Z,
                     TIE_X + TIE_T, TIE_Y + TIE_SLOT_W / 2,
                     IZ0 + TIE_SLOT_Z + TIE_SLOT_H))

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
# LED sight holes: stepped bore for a 3 mm rod light pipe, plus a light
# chamfer at the mouth. The rod goes in from the underside and seats on the
# aperture land, so it cannot migrate down onto the LED.
LED_HOLES = LED_HOLES_HAT + LED_HOLES_POE
for lx, ly in LED_HOLES:
    lid = cut(lid, cyl_z(lx, ly, IZ1 - 0.01,
                         LID_T - LED_APERTURE_T + 0.01, LED_PIPE_D))
    lid = cut(lid, cyl_z(lx, ly, IZ1 - 0.01, LID_T + 0.02, LED_APERTURE_D))
    lid = cut(lid, cone_z(lx, ly, IZ1 + LID_T + 0.01,
                          LED_APERTURE_D / 2 + 0.40, LED_APERTURE_D / 2, 0.41))

# engraved label, on the outer face
lid = engrave(lid, LID_LINES, LID_LABEL_SIZE, LID_LABEL_DEPTH,
              LID_LABEL_CX, LID_LABEL_CY, IZ1 + LID_T, LID_LABEL_LEADING)

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
ok &= clear("dead J1 crown to lid underside", IZ1 - (HAT_TOP + J1_BODY_H), 1.0)
ok &= clear("hat underside pins to ESP32 top", (HAT_Z - HAT_PIN_DROP) - 1.578, 2.0)
# Measured tall parts vs the hat's bare underside. Nothing on the hat hangs
# below its underside over the ESP32: J3/J4 pins solder on the top face, and the
# J1/J2 tails are outboard of the ESP32's right edge (x 118.15).
for nm, x0, y0, x1, y1, tz in TALL_PARTS:
    ok &= clear("hat underside to %s (meas.)" % nm, HAT_Z - tz, 0.5)
ok &= clear("header pin engagement in the sockets",
            (HDR_PLASTIC_TOP + HDR_PIN_ABOVE) - (HAT_Z - SOCKET_H), 3.5)
ok &= clear("RJ45 crown to lid underside", IZ1 - 16.70, 2.0)
ok &= clear("interior past antenna tip", IY1 - (-83.69), 1.0)
for bx, by in BOSSES_HAT:
    ok &= clear("hat boss %.1f clear of ESP32 edge" % bx,
                bx - HAT_BOSS_D / 2 - 118.15, 0.5)
ok &= clear("J2 nose recess inside outer face", OX1 - J2_NOSE_X, 0.5)

# --- 12 V panel jack --------------------------------------------------------
if not PJ_DIMS_VERIFIED:
    print("  [WARN] panel jack dimensions are PLACEHOLDERS — measure the part,"
          " set PJ_DIMS_VERIFIED, re-run, then print")
else:
    print("  [note] panel jack: barrel, flat and nut are calipered; thread and"
          " overall length are from the vendor drawing; flange and body"
          " diameters are assumed upper bounds (see the PJ_ block)")
ok &= clear("panel jack thread past the wall and nut",
            PJ_THREAD_L - (WALL + PJ_NUT_T), 0.50)
ok &= clear("wall left under the jack flange", WALL, 2.00)
ok &= clear("D-hole flat leaves a real key", PJ_HOLE_D / 2 - PJ_FLAT_Z, 0.50)
ok &= clear("flange covers the D-hole", (PJ_FLANGE_D - PJ_HOLE_D) / 2, 1.00)
ok &= clear("panel jack to hat near edge", HAT_Y0 - (PJ_Y + PJ_ENV_D / 2), 2.00)
ok &= clear("panel jack to the -Y lid boss",
            (PJ_Y - PJ_ENV_D / 2) - (IY0 + LB_IN + LID_BOSS_D / 2), 2.00)
ok &= clear("panel jack body above the floor",
            (PJ_AXIS_Z - PJ_BODY_D / 2) - IZ0, 2.00)
ok &= clear("panel jack body under the hat plane",
            HAT_Z - (PJ_AXIS_Z + PJ_BODY_D / 2), 0.00)
ok &= clear("panel jack body clear of the ESP32 edge",
            (IX1 - PJ_BODY_L) - 118.15, 2.00)
ok &= clear("tie post clear of the jack body",
            (TIE_Y - TIE_W / 2) - (PJ_Y + PJ_BODY_D / 2), 0.50)

# --- light pipes -----------------------------------------------------------
PIPE_SEAT_Z = IZ1 + LID_T - LED_APERTURE_T      # the land the rod seats on
PIPE_LEN_HAT = PIPE_SEAT_Z - LED_Z_HAT - LED_PIPE_GAP
PIPE_LEN_POE = PIPE_SEAT_Z - LED_Z_POE - LED_PIPE_GAP
ok &= clear("aperture land leaves a real step", (LED_PIPE_D - LED_APERTURE_D) / 2, 0.30)
# the two PoE pipes must stay outboard of the hat, which is opaque FR4
for lx, ly in LED_HOLES_POE:
    ok &= clear("PoE pipe %.1f clear of the hat edge" % -ly,
                HAT_Y0 - (ly + LED_PIPE_D / 2), 0.50)
# nearest tall neighbour on the Olimex board to either PoE pipe
for nm, nx, ny, nr in [("U3 SOT-23-5", 93.853, -178.562, 1.75),
                       ("TVS1 SOT-23-5", 97.282, -176.911, 1.75),
                       ("USB-UART1", 96.176, -152.654, 3.50)]:
    d = min(math.hypot(lx - nx, ly - ny) for lx, ly in LED_HOLES_POE)
    ok &= clear("PoE pipe clear of %s" % nm, d - LED_PIPE_D / 2 - nr, 0.30)
# pipes must not foul the lid's own screw counterbores
for lx, ly in LED_HOLES:
    d = min(math.hypot(lx - bx, ly - by) for bx, by, _ in LID_BOSSES)
    ok &= clear("sight hole %.1f,%.1f clear of lid boss" % (lx, ly),
                d - LED_PIPE_D / 2 - 6.8 / 2, 1.00)
# the label block, as engraved, must sit clear of the lid edge, every boss
# counterbore (6.8) and every sight-hole mouth (aperture + 0.8 chamfer)
_o, _h = _glyph_loops(LID_LINES, LID_LABEL_SIZE, LID_LABEL_LEADING)
_pts = np.array([_rot_label(p, LID_LABEL_ROT) for lp in _o for p in lp])
LBX0, LBY0 = _pts.min(0) + (LID_LABEL_CX, LID_LABEL_CY)
LBX1, LBY1 = _pts.max(0) + (LID_LABEL_CX, LID_LABEL_CY)
print("  lid label block x %.1f..%.1f  y %.1f..%.1f  (%.1f x %.1f mm)"
      % (LBX0, LBX1, LBY0, LBY1, LBX1 - LBX0, LBY1 - LBY0))
ok &= clear("lid label to lid edge", min(LBX0 - OX0, OX1 - LBX1, LBY0 - OY0, OY1 - LBY1), 4.0)
def _box_circle(cx, cy, r):
    dx = max(LBX0 - cx, 0, cx - LBX1); dy = max(LBY0 - cy, 0, cy - LBY1)
    return math.hypot(dx, dy) - r
ok &= clear("lid label clear of boss counterbores",
            min(_box_circle(bx, by, 6.8 / 2) for bx, by, _ in LID_BOSSES), 2.0)
ok &= clear("lid label clear of sight holes",
            min(_box_circle(lx, ly, LED_APERTURE_D / 2 + 0.40) for lx, ly in LED_HOLES), 2.0)
print("  light pipes: 3 mm rod, %d x %.1f mm (hat) + %d x %.1f mm (PoE),"
      " seat z=%.2f" % (len(LED_HOLES_HAT), PIPE_LEN_HAT,
                        len(LED_HOLES_POE), PIPE_LEN_POE, PIPE_SEAT_Z))
print("  all geometry checks pass" if ok else "  *** CHECKS FAILED ***")

# solid interference test: does the case body intersect the hat's envelope?
# The bosses are meant to touch each board's underside, so the tests start at
# the plane each board sits on: anything above that is a real collision.
hat_env = box(HAT_X0, HAT_Y0, HAT_Z, HAT_X1, HAT_Y1, HAT_TOP + J1_BODY_H)
v1 = volume(common(case, hat_env))
esp_env = box(90.15, -188.15, 0.0, 118.15, -90.0, TALL_MAX_Z)
v2 = volume(common(case, esp_env))
print("  [%s] case intersects hat envelope        %8.3f mm3 (want 0)"
      % ("OK " if v1 < 1e-6 else "FAIL", v1))
print("  [%s] case intersects ESP32 envelope      %8.3f mm3 (want 0)"
      % ("OK " if v2 < 1e-6 else "FAIL", v2))
lid_env = box(IX0, IY0, IZ1, IX1, IY1, IZ1 + LID_T)
# the hat's board slab against the measured tall parts, each grown 0.5 mm up
tall = None
for nm, x0, y0, x1, y1, tz in TALL_PARTS:
    t = box(x0, y0, 1.578, x1, y1, tz + 0.5)
    tall = t if tall is None else fuse(tall, t)
v6 = volume(common(box(HAT_X0, HAT_Y0, HAT_Z, HAT_X1, HAT_Y1, HAT_TOP), tall))
print("  [%s] hat PCB intersects tall parts +0.5  %8.3f mm3 (want 0)"
      % ("OK " if v6 < 1e-6 else "FAIL", v6))
v3 = volume(common(lid_env, hat_env))
print("  [%s] lid volume intersects hat envelope  %8.3f mm3 (want 0)"
      % ("OK " if v3 < 1e-6 else "FAIL", v3))

# The fitted light pipes hang off the lid. They must clear both PCBs -- this
# is the test that rules ACT1 out and would catch any future hole placed over
# something the hat covers.
pipes = None
for lx, ly in LED_HOLES_HAT:
    p = cyl_z(lx, ly, LED_Z_HAT + LED_PIPE_GAP, PIPE_LEN_HAT, LED_PIPE_D)
    pipes = p if pipes is None else fuse(pipes, p)
for lx, ly in LED_HOLES_POE:
    p = cyl_z(lx, ly, LED_Z_POE + LED_PIPE_GAP, PIPE_LEN_POE, LED_PIPE_D)
    pipes = fuse(pipes, p)
hat_pcb = box(HAT_X0, HAT_Y0, HAT_Z - HAT_PIN_DROP, HAT_X1, HAT_Y1, HAT_TOP)
esp_pcb = box(90.15, -188.15, 0.0, 118.15, -90.0, 1.578)
v4 = volume(common(pipes, hat_pcb))
v5 = volume(common(pipes, esp_pcb))
print("  [%s] light pipes intersect hat PCB       %8.3f mm3 (want 0)"
      % ("OK " if v4 < 1e-6 else "FAIL", v4))
print("  [%s] light pipes intersect ESP32 PCB     %8.3f mm3 (want 0)"
      % ("OK " if v5 < 1e-6 else "FAIL", v5))

# The panel jack's body is the one solid this case now has to make room for
# that no earlier revision had. Test it the way the light pipes are tested:
# as a solid, against every other solid in the box.
pj_body = cyl_x(PJ_Y, PJ_AXIS_Z, IX1 - PJ_BODY_L, PJ_BODY_L, PJ_BODY_D)
furniture = None
for bx, by, zb in LID_BOSSES:
    f_ = cyl_z(bx, by, zb, IZ1 - zb, LID_BOSS_D)
    furniture = f_ if furniture is None else fuse(furniture, f_)
for bx, by in BOSSES_HAT:                       # boss plus its gusset foot
    furniture = fuse(furniture, cyl_z(bx, by, IZ0, HAT_Z - IZ0, HAT_BOSS_D + 6.0))
for bx, by in BOSSES_BOARD:
    furniture = fuse(furniture, cyl_z(bx, by, IZ0, -IZ0, 6.0))
furniture = fuse(furniture, box(TIE_X - TIE_T / 2, TIE_Y - TIE_W / 2, IZ0,
                                TIE_X + TIE_T / 2, TIE_Y + TIE_W / 2, IZ0 + TIE_H))
for _nm, _other in (("hat envelope", hat_env), ("ESP32 envelope", esp_env),
                    ("lid volume", lid_env), ("case furniture", furniture)):
    _v = volume(common(pj_body, _other))
    print("  [%s] panel jack body vs %-16s %8.3f mm3 (want 0)"
          % ("OK " if _v < 1e-6 else "FAIL", _nm, _v))

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
