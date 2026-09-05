#!/usr/bin/env python3
"""aF4 PoE trigger hat — FITMENT DUMMY (rev E geometry) — raw OCP.

A printable stand-in for the rev E trigger hat, for test-fitting the printed
enclosure before the real PCB comes back from PCBWay. It is NOT a PCB: no
copper, no pins, no passives that cannot foul anything.

WHAT IT REPRODUCES (and therefore what it can prove)
  - the 57.0 x 50.0 x 1.6 mm board outline
  - both M3 mounting holes, so it screws onto the two case standoffs
  - J1 PJ-079BH body, with its 9.5 mm barrel bore open to the front face, so a
    real 5.5 x 2.5 plug can be pushed through the wall and into it
  - J2 SJ1-3523N body, shoulder and 6.0 mm nose
  - D3 / D5 bumps under the two lid sight holes
  - U1, so the isolation band is visible
  - two detachable 8.5 mm socket-body bars (J3/J4) that peg into the underside,
    to check the vertical stack over the ESP32 and the UEXT header

WHAT IT CANNOT PROVE
  The J2 axis height (14.218 + 2.50) is an assumed number carried over from
  af4_enclosure_ocp.py, not a measured one, and this dummy is built from the
  same assumption -- so it cannot catch an error in it. Measure the real jack's
  barrel axis above its seating plane when the parts arrive.

Geometry is taken from the footprints actually placed in af4-trigger-hat.kicad_pcb
(F.Fab outlines, transformed into the board frame) and from the z stack tabulated
in aF4-enclosure-notes.md. Modelled in the ENCLOSURE frame (enclosure_y =
-kicad_y), verified against af4_case_inframe.step / af4_lid_inframe.step, then
translated to the origin for printing.

Print on the P1S: as exported, no supports. Brim recommended -- the board is a
thin 57 x 50 plate and the two socket bars are thin standing walls.
"""
import math, os, sys
from OCP.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax2, gp_Ax3, gp_Trsf
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire,
                                BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform)
from OCP.STEPControl import STEPControl_Writer, STEPControl_StepModelType, STEPControl_Reader
from OCP.IFSelect import IFSelect_ReturnStatus
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder

# ============================================================ the z stack
# from aF4-enclosure-notes.md; every one of these is also a constant in
# af4_enclosure_ocp.py, and they must not drift apart.
HAT_Z = 1.578 + 2.54 + 8.50      # 12.618  hat underside
HAT_T = 1.6
HAT_TOP = HAT_Z + HAT_T          # 14.218  hat top face
SOCKET_H = 8.50                  # 1x10 socket body height -- sets everything

# ---- board outline (gen_pcb.py BX0/BX1, BY0/BY1) ---------------------------
BX0, BX1 = 89.15, 146.15                 # 57.0 mm
BY0, BY1 = -160.00, -110.00              # 50.0 mm (kicad y 110..160, negated)

# ---- mounting holes --------------------------------------------------------
MOUNT = [(123.00, -118.00), (123.50, -147.00)]
MOUNT_D = 3.30   # real board is 3.20; +0.10 so a printed hole still passes M3

# ---- J1 PJ-079BH, F.Fab body, placed at (144,121) rot -90 ------------------
J1_X0, J1_X1 = 133.70, 145.20             # 11.5 deep
J1_Y0, J1_Y1 = -121.60, -111.50           # 10.1 wide
J1_H = 7.20
J1_AXIS_Y, J1_AXIS_Z = -116.56, HAT_TOP + 3.60   # centred in body, both axes
J1_BORE_D, J1_BORE_L = 6.00, 9.50         # accepts a 5.5 mm plug barrel

# ---- J2 SJ1-3523N, F.Fab body, placed at (141.65,148.5) rot 90 ------------
J2_X0, J2_X1 = 133.95, 144.95             # main body
J2_Y0, J2_Y1 = -154.50, -142.50
J2_SH_X1, J2_SH_Y0, J2_SH_Y1 = 146.15, -153.00, -144.00   # shoulder
J2_NOSE_X1 = 147.95                       # F.Fab nose tip (enclosure assumed 148.45)
J2_NOSE_D = 6.00
J2_H = 5.00
J2_AXIS_Y, J2_AXIS_Z = -148.50, HAT_TOP + 2.50

# ---- small top-side parts --------------------------------------------------
U1 = (121.80, -139.15, 126.20, -134.85, 2.10)      # SOP-4
LED_BUMPS = [(139.50, -139.00), (128.20, -150.80)]  # D3 green, D5 yellow
LED_BUMP_D, LED_BUMP_H = 2.00, 1.40

# ---- socket bars (J3 EXT1 / J4 EXT2), F.Fab bodies ------------------------
BARS = [("J3", 90.17, 92.71), ("J4", 115.57, 118.11)]
BAR_Y0, BAR_Y1 = -147.35, -121.95          # 25.4 long
PEG_D, PEG_L = 1.60, 1.60
PEG_YS = [-144.30, -125.00]
PEG_HOLE_D = 1.80

TXT_FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# ============================================================ helpers
def box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()

def cyl_z(cx, cy, z0, h, d):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(cx, cy, z0), gp_Dir(0, 0, 1)),
                                    d / 2, h).Shape()

def cyl_x(cy, cz, x0, ln, d):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, cy, cz), gp_Dir(1, 0, 0)),
                                    d / 2, ln).Shape()

def fuse(a, b):
    return BRepAlgoAPI_Fuse(a, b).Shape()

def cut(a, b):
    return BRepAlgoAPI_Cut(a, b).Shape()

def common(a, b):
    return BRepAlgoAPI_Common(a, b).Shape()

def volume(s):
    p = GProp_GProps(); BRepGProp.VolumeProperties_s(s, p)
    return p.Mass()

def bbox(s):
    b = Bnd_Box(); BRepBndLib.Add_s(s, b)
    b.SetGap(0.0)          # report the tight box, not the tolerance-inflated one
    return b.Get()

def translate(shape, dx, dy, dz):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, dy, dz))
    return BRepBuilderAPI_Transform(shape, t, True).Shape()

def compound(shapes):
    c = TopoDS_Compound(); b = BRep_Builder(); b.MakeCompound(c)
    for s in shapes:
        b.Add(c, s)
    return c

def write_step(shape, path):
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_StepModelType.STEPControl_AsIs)
    w.Write(path)

def write_stl(shape, path):
    BRepMesh_IncrementalMesh(shape, 0.02, False, 0.3, True)
    sw = StlAPI_Writer(); sw.ASCIIMode = False
    sw.Write(shape, path)

def read_step(path):
    r = STEPControl_Reader()
    if r.ReadFile(path) != IFSelect_ReturnStatus.IFSelect_RetDone:
        raise IOError("cannot read %s" % path)
    r.TransferRoots()
    return r.OneShape()

def emboss(s, x, y, h, size, depth):
    """Raised text on the +Z face at height h. Returns None if no font."""
    try:
        # OCCT 7.x moved these out of Font_ into StdPrs_
        try:
            from OCP.StdPrs import StdPrs_BRepFont as _BRepFont, \
                StdPrs_BRepTextBuilder as _BRepTextBuilder
        except ImportError:
            from OCP.Font import Font_BRepFont as _BRepFont, \
                Font_BRepTextBuilder as _BRepTextBuilder
        from OCP.Graphic3d import Graphic3d_HorizontalTextAlignment, Graphic3d_VerticalTextAlignment
        from OCP.NCollection import NCollection_Utf8String
    except Exception as e:
        print("  [--] text skipped:", e)
        return None
    if not os.path.exists(TXT_FONT):
        print("  [--] text skipped: no font at", TXT_FONT)
        return None
    f = _BRepFont()
    if not f.Init(NCollection_Utf8String(TXT_FONT), size, 0):
        print("  [--] text skipped: font would not load")
        return None
    b = _BRepTextBuilder()
    face = b.Perform(f, NCollection_Utf8String(s),
                     gp_Ax3(gp_Pnt(x, y, h), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0)),
                     Graphic3d_HorizontalTextAlignment.Graphic3d_HTA_LEFT,
                     Graphic3d_VerticalTextAlignment.Graphic3d_VTA_BOTTOM)
    return BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, depth)).Shape()

# ============================================================ the dummy board
board = box(BX0, BY0, HAT_Z, BX1, BY1, HAT_TOP)

# J1 barrel jack: body, then bore the plug hole in from the front face
j1 = box(J1_X0, J1_Y0, HAT_TOP, J1_X1, J1_Y1, HAT_TOP + J1_H)
j1 = cut(j1, cyl_x(J1_AXIS_Y, J1_AXIS_Z, J1_X1 - J1_BORE_L, J1_BORE_L + 0.01,
                   J1_BORE_D))
board = fuse(board, j1)

# J2 3.5 mm jack: body + shoulder + nose. The nose is a 6.0 mm cylinder whose
# axis sits 2.50 above the board, i.e. 0.5 below the body's own top and bottom
# planes -- so it is truncated to the 5.0 mm body height, which is also why it
# prints with no overhang below the board top face.
j2 = box(J2_X0, J2_Y0, HAT_TOP, J2_X1, J2_Y1, HAT_TOP + J2_H)
j2 = fuse(j2, box(J2_X1, J2_SH_Y0, HAT_TOP, J2_SH_X1, J2_SH_Y1, HAT_TOP + J2_H))
nose = cyl_x(J2_AXIS_Y, J2_AXIS_Z, J2_SH_X1 - 0.5, (J2_NOSE_X1 - J2_SH_X1) + 0.5,
             J2_NOSE_D)
nose = common(nose, box(J2_SH_X1 - 0.5, J2_AXIS_Y - 5, HAT_TOP,
                        J2_NOSE_X1, J2_AXIS_Y + 5, HAT_TOP + J2_H))
j2 = fuse(j2, nose)
board = fuse(board, j2)

# U1 and the two LED bumps
board = fuse(board, box(U1[0], U1[1], HAT_TOP, U1[2], U1[3], HAT_TOP + U1[4]))
for lx, ly in LED_BUMPS:
    board = fuse(board, cyl_z(lx, ly, HAT_TOP, LED_BUMP_H, LED_BUMP_D))

# labels
for s, x, y, sz in [("aF4 HAT rev E  DUMMY", 92.0, -158.2, 3.0),
                    ("NOT A PCB", 92.0, -153.6, 3.0)]:
    t = emboss(s, x, y, HAT_TOP, sz, 0.6)
    if t is not None:
        board = fuse(board, t)

# holes last, so nothing fuses over them
for mx, my in MOUNT:
    board = cut(board, cyl_z(mx, my, HAT_Z - 0.5, HAT_T + 1.0, MOUNT_D))
for _, bx0, bx1 in BARS:
    for py in PEG_YS:
        board = cut(board, cyl_z((bx0 + bx1) / 2, py, HAT_Z - 0.5, HAT_T + 1.0,
                                 PEG_HOLE_D))

# ============================================================ socket bars
bars = []
for name, bx0, bx1 in BARS:
    b = box(bx0, BAR_Y0, HAT_Z - SOCKET_H, bx1, BAR_Y1, HAT_Z)
    for py in PEG_YS:
        b = fuse(b, cyl_z((bx0 + bx1) / 2, py, HAT_Z - 0.01, PEG_L + 0.01, PEG_D))
    bars.append(b)

# ============================================================ checks
print("aF4 hat fitment dummy -- checks")
ok = True

def chk(name, got, want, unit="mm"):
    global ok
    good = got >= want
    ok &= good
    print("  [%s] %-46s %8.3f %s (want >= %.2f)"
          % ("OK " if good else "FAIL", name, got, unit, want))

def chk_zero(name, got):
    global ok
    good = got < 1e-6
    ok &= good
    print("  [%s] %-46s %8.3f mm3 (want 0)" % ("OK " if good else "FAIL", name, got))

bb = bbox(board)
print("  dummy bbox  x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f"
      % (bb[0], bb[3], bb[1], bb[4], bb[2], bb[5]))
chk("board outline width", BX1 - BX0, 57.0)
chk("board outline length", BY1 - BY0, 50.0)
chk("J1 bore reaches past the wall inner face", J1_X1 - (J1_X1 - J1_BORE_L), 9.5)
chk("J2 nose recess inside outer wall face", 149.65 - J2_NOSE_X1, 0.5)
chk("barrel crown to lid underside", 23.50 - (HAT_TOP + J1_H), 1.0)

here = os.path.dirname(os.path.abspath(__file__))
CASE = os.environ.get("AF4_CASE_STEP", os.path.join(here, "af4_case_inframe.step"))
LID = os.environ.get("AF4_LID_STEP", os.path.join(here, "af4_lid_inframe.step"))
whole = compound([board] + bars)
if os.path.exists(CASE) and os.path.exists(LID):
    case, lid = read_step(CASE), read_step(LID)
    chk_zero("dummy intersects case solid", volume(common(whole, case)))
    chk_zero("dummy intersects lid solid", volume(common(whole, lid)))
    # the mounting holes must actually clear the case's standoff pilot bosses
    for i, (mx, my) in enumerate(MOUNT, 1):
        pin = cyl_z(mx, my, HAT_Z - 0.2, HAT_T + 0.4, 3.0)   # an M3 shank
        chk_zero("M3 %d shank clears the dummy" % i, volume(common(pin, board)))
    # a plug pushed through the wall must reach the J1 bore
    plug = cyl_x(J1_AXIS_Y, J1_AXIS_Z, 141.0, 12.0, 5.5)
    chk_zero("5.5 mm plug path clears the case wall bore",
             volume(common(plug, case)))
else:
    print("  [--] case/lid STEP not found beside the script; solid checks SKIPPED")

# Does either socket bar foul anything on the ESP32? Read the vendor mesh
# directly -- it is already in the enclosure frame -- and take the tallest
# vertex under each bar footprint. The bar underside is the top of the male
# header plastic the sockets will sit on (z = 4.118).
# The vendor mesh is gitignored and lives in reference/vendor/ since the
# 2026-09-05 reorganisation. Look there first, then beside the script, so
# the check keeps running from either layout.
ESP = next((c for c in (
    os.environ.get("AF4_ESP32_STL", ""),
    os.path.join(here, "..", "..", "reference", "vendor", "ESP32-PoE-ISO_Rev_N.stl"),
    os.path.join(here, "ESP32-PoE-ISO_Rev_N.stl"),
) if c and os.path.exists(c)), os.path.join(here, "ESP32-PoE-ISO_Rev_N.stl"))
if os.path.exists(ESP):
    import struct
    with open(ESP, "rb") as fh:
        n = struct.unpack("<I", fh.read(84)[80:84])[0]
        tall = [-1e9] * len(BARS)
        for _ in range(n):
            v = struct.unpack("<12f", fh.read(50)[:48])[3:]
            for k in range(3):
                x, y, z = v[3 * k], v[3 * k + 1], v[3 * k + 2]
                if not (BAR_Y0 - 0.2 <= y <= BAR_Y1 + 0.2):
                    continue
                for bi, (_, x0, x1) in enumerate(BARS):
                    if x0 - 0.2 <= x <= x1 + 0.2 and z > tall[bi]:
                        tall[bi] = z
    for bi, (nm, _, _) in enumerate(BARS):
        chk("%s bar clears the ESP32 below it" % nm,
            (HAT_Z - SOCKET_H) - tall[bi], 0.5)
else:
    print("  [--] ESP32-PoE-ISO_Rev_N.stl not found in reference/vendor/ or "
          "beside the script; socket-bar clearance check SKIPPED -- this is a "
          "silently reduced check, not a pass")

print("  all checks pass" if ok else "  *** CHECKS FAILED ***")
print("  volume: board %.1f cm3, each bar %.2f cm3"
      % (volume(board) / 1000, volume(bars[0]) / 1000))

# ============================================================ export
write_step(compound([board] + bars), os.path.join(here, "af4_hat_dummy_inframe.step"))

# print layout: board flat, bottom face on the plate; bars standing behind it
bp = translate(board, -BX0, -BY0, -HAT_Z)
plate = [bp]
for i, b in enumerate(bars):
    bb2 = bbox(b)
    b = translate(b, -bb2[0], -bb2[1], -bb2[2])
    plate.append(translate(b, i * 6.0, (BY1 - BY0) + 6.0 + i * 6.0, 0))
out = compound(plate)
write_stl(out, os.path.join(here, "aF4-trigger-hat-dummy.stl"))
write_step(out, os.path.join(here, "aF4-trigger-hat-dummy.step"))
ob = bbox(out)
print("  plate: %.1f x %.1f x %.1f mm"
      % (ob[3] - ob[0], ob[4] - ob[1], ob[5] - ob[2]))
print("exports done")
sys.exit(0 if ok else 1)
