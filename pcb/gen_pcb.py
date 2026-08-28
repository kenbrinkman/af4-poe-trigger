#!/usr/bin/env python3
"""Generate the aF4 PoE Trigger Hat (rev D) KiCad PCB.

Coordinates are expressed in the Olimex ESP32-POE-ISO Rev N board frame, so the
socket positions come straight from the vendor CAD:
  ESP32 outline  x 90.15..118.15   y 90.00..188.15
  EXT1 pin1      (91.44, 123.22)   pin3 = GND    (91.44, 128.30)
  EXT2 pin1      (116.84, 123.22)  pin6 = GPIO32 (116.84, 135.92)
"""
import re, os, math

FPDIR = "/usr/share/kicad/footprints"

MIN_SLOT = 0.70   # PCBWay will not route a slot narrower than this; some library
                  # footprints (SJ1-3523N) specify 0.40 mm blade slots, which would
                  # trigger an engineering query. Widened here, annular ring checked.

BX0, BX1 = 89.15, 146.15      # 57.0 mm
BY0, BY1 = 110.00, 160.00     # 50.0 mm
GAP_L, GAP_R = 121.65, 126.35  # isolation frontier (logic | power)

nets = {}
def net(name):
    if name not in nets:
        nets[name] = len(nets) + 1
    return nets[name]
net("")

# ------------------------------------------------------------------- helpers
def load(lib, name):
    return open(os.path.join(FPDIR, lib + ".pretty", name + ".kicad_mod")).read()

def sexp_span(text, start):
    i = text.index("(", start)
    d, k = 0, text.index("(", start)
    while k < len(text):
        if text[k] == "(":
            d += 1
        elif text[k] == ")":
            d -= 1
            if d == 0:
                return i, k + 1
        k += 1
    raise ValueError("unbalanced s-expression")

def xf(fx, fy, px, py, rot):
    """KiCad footprint-local -> board coordinates."""
    a = math.radians(rot)
    return (fx + px * math.cos(a) + py * math.sin(a),
            fy - px * math.sin(a) + py * math.cos(a))

PADS = {}   # (ref, padnum) -> (x, y)
WIDENED = []
FPS = []

def place(lib, fpname, ref, value, x, y, rot=0, netmap=None):
    t = load(lib, fpname)
    netmap = netmap or {}

    # header: handle both quoted (KiCad 6/7) and bare (legacy) footprint names
    m = re.match(r'\(footprint\s+("?)([^"\s)]+)\1', t)
    hdr_end = m.end()
    t = ('(footprint "%s" (layer "F.Cu")\n  (at %.4f %.4f%s)'
         % (m.group(2), x, y, "" if rot == 0 else " %g" % rot)) + t[hdr_end:]
    # drop the footprint's own layer/tedit tokens that now duplicate ours
    t = re.sub(r'\(version \d+\)\s*', '', t, count=1)
    t = re.sub(r'\(generator [^)]*\)\s*', '', t, count=1)
    t = re.sub(r'\(layer "?F\.Cu"?\)\s*', '', t, count=1)
    t = re.sub(r'\(tedit [^)]*\)\s*', '', t, count=1)

    t = re.sub(r'\(fp_text reference ("?)[^"\s)]*\1',
               '(fp_text reference "%s"' % ref, t, count=1)
    t = re.sub(r'\(fp_text value ("?)[^"\s)]*\1',
               '(fp_text value "%s"' % value, t, count=1)
    s = t.find('(fp_text value')
    if s >= 0:
        a, b = sexp_span(t, s)
        blk = t[a:b]
        if " hide" not in blk:
            blk = re.sub(r'\(layer "?F\.Fab"?\)', lambda mm: mm.group(0) + " hide", blk, count=1)
        t = t[:a] + blk + t[b:]

    # strip any Edge.Cuts geometry the footprint carries (jack nose notches):
    # our board outline is a plain rectangle and the noses simply overhang it.
    for tag in ("(fp_line", "(fp_arc", "(fp_circle", "(fp_poly", "(fp_rect"):
        out, i = [], 0
        while True:
            j = t.find(tag, i)
            if j < 0:
                out.append(t[i:]); break
            a, b = sexp_span(t, j)
            blk = t[a:b]
            out.append(t[i:a])
            if 'Edge.Cuts' not in blk:
                out.append(blk)
            i = b
        t = "".join(out)

    # pads: rotate pad angles with the footprint, attach nets, record positions
    out, i = [], 0
    while True:
        j = t.find("(pad ", i)
        if j < 0:
            out.append(t[i:]); break
        out.append(t[i:j])
        a, b = sexp_span(t, j)
        pad = t[a:b]
        num = re.match(r'\(pad "?([^"\s]*)"?', pad).group(1)
        at = re.search(r'\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', pad)
        px, py = float(at.group(1)), float(at.group(2))
        if num:
            PADS[(ref, num)] = xf(x, y, px, py, rot)
        if rot:
            ang = float(at.group(3)) if at.group(3) else 0.0
            pad = (pad[:at.start()] + "(at %g %g %g)" % (px, py, (ang + rot) % 360)
                   + pad[at.end():])
        # manufacturability: widen any slot narrower than MIN_SLOT
        def widen(mm):
            a, bb = float(mm.group(1)), float(mm.group(2))
            na, nb = max(a, MIN_SLOT), max(bb, MIN_SLOT)
            if (na, nb) != (a, bb):
                WIDENED.append((ref, num, a, bb, na, nb))
            return "(drill oval %g %g)" % (na, nb)
        pad = re.sub(r'\(drill oval ([\d.]+) ([\d.]+)\)', widen, pad)
        if num in netmap:
            n = netmap[num]
            pad = pad[:-1] + ' (net %d "%s"))' % (net(n), n)
        out.append(pad)
        i = b
    FPS.append("".join(out))

def PP(ref, pad):
    return PADS[(ref, str(pad))]

segs, vias, gfx = [], [], []
def seg(p1, p2, netname, layer="F.Cu", w=0.35):
    segs.append('  (segment (start %.4f %.4f) (end %.4f %.4f) (width %.2f) '
                '(layer "%s") (net %d))' % (p1[0], p1[1], p2[0], p2[1], w, layer, net(netname)))

def route(pts, netname, w=0.35, layer="F.Cu"):
    for p1, p2 in zip(pts, pts[1:]):
        if p1 != p2:
            seg(p1, p2, netname, layer, w)

def via(x, y, netname):
    vias.append('  (via (at %.4f %.4f) (size 0.9) (drill 0.45) '
                '(layers "F.Cu" "B.Cu") (net %d))' % (x, y, net(netname)))

def line(x1, y1, x2, y2, layer, w=0.15):
    gfx.append('  (gr_line (start %.4f %.4f) (end %.4f %.4f) (stroke (width %.2f) '
               '(type solid)) (layer "%s"))' % (x1, y1, x2, y2, w, layer))

def text(s, x, y, layer="F.SilkS", size=1.0, thick=0.15, rot=0, just=None):
    j = ' (justify %s)' % just if just else ''
    gfx.append('  (gr_text "%s" (at %.4f %.4f%s) (layer "%s") (effects (font '
               '(size %.2f %.2f) (thickness %.2f))%s))'
               % (s, x, y, "" if rot == 0 else " %g" % rot, layer, size, size, thick, j))

# ================================================================ PLACEMENT
# ---- logic domain ----------------------------------------------------------
place("Connector_PinSocket_2.54mm", "PinSocket_1x10_P2.54mm_Vertical",
      "J3", "EXT1", 91.44, 123.22, 0, {"3": "GNDL"})
place("Connector_PinSocket_2.54mm", "PinSocket_1x10_P2.54mm_Vertical",
      "J4", "EXT2", 116.84, 123.22, 0, {"6": "GPIO32"})

# The PhotoMOS bridges the isolation frontier: pins 1/2 (LED) in the logic
# domain, pins 3/4 (a symmetric MOSFET pair) in the feeder-power domain.
place("Package_SO", "SO-4_4.4x2.3mm_P1.27mm", "U1", "AQY212GS", 124.00, 137.00, 0,
      {"1": "LED_A", "2": "GNDL", "3": "TIP", "4": "+10V4"})
place("Resistor_SMD", "R_0805_2012Metric", "R1", "220R", 120.50, 132.00, 0,
      {"1": "GPIO32", "2": "LED_A"})
place("Resistor_SMD", "R_0805_2012Metric", "R2", "10k", 112.00, 132.11, 0,
      {"1": "GNDL", "2": "GPIO32"})

# ---- power domain: connectors ----------------------------------------------
place("Connector_BarrelJack", "BarrelJack_CUI_PJ-079BH_Horizontal",
      "J1", "PJ-079BH", 144.00, 121.00, 270, {"1": "+12V_RAW", "2": "GNDP"})
place("Connector_Audio", "Jack_3.5mm_CUI_SJ1-3523N_Horizontal",
      "J2", "SJ1-3523N", 141.65, 148.50, 90, {"T": "TIP", "S": "GNDP", "R": "GNDP"})

# ---- power domain: input chain ---------------------------------------------
place("Resistor_SMD", "R_1206_3216Metric", "F1", "010", 129.50, 112.00, 180,
      {"1": "+12V_RAW", "2": "+12V_F"})     # rot 180 puts pad 1 on the right
place("Diode_SMD", "D_SMA", "D1", "SS14", 128.20, 117.50, 90,
      {"1": "+12V", "2": "+12V_F"})         # pad1 = cathode, lower
place("Diode_SMD", "D_SMA", "D2", "SMAJ15A", 128.20, 126.50, 270,
      {"1": "+12V", "2": "GNDP"})           # pad1 = cathode, upper

# ---- power domain: regulator ------------------------------------------------
place("Capacitor_SMD", "C_1206_3216Metric", "C1", "10uF/50V", 132.60, 124.50, 180,
      {"1": "+12V", "2": "GNDP"})           # pad1 right
place("Package_TO_SOT_SMD", "SOT-223-3_TabPin2", "U2", "LM1117MPX-ADJ",
      141.00, 127.50, 180, {"1": "ADJ", "2": "+10V4", "3": "+12V"})
place("Capacitor_Tantalum_SMD", "CP_EIA-3528-21_Kemet-B", "C2", "10uF/25V",
      138.50, 134.00, 180, {"1": "+10V4", "2": "GNDP"})
place("Resistor_SMD", "R_0805_2012Metric", "R4", "121R", 143.00, 133.00, 180,
      {"1": "+10V4", "2": "ADJ"})
place("Resistor_SMD", "R_0805_2012Metric", "R5", "887R", 143.00, 136.00, 0,
      {"1": "ADJ", "2": "GNDP"})

# ---- power domain: indicators and trigger output ---------------------------
place("Resistor_SMD", "R_0805_2012Metric", "R6", "1k0", 136.00, 139.00, 0,
      {"1": "+10V4", "2": "PWRLED"})
place("LED_SMD", "LED_0805_2012Metric", "D3", "GRN", 139.50, 139.00, 180,
      {"1": "GNDP", "2": "PWRLED"})
place("Resistor_SMD", "R_0805_2012Metric", "R3", "100k", 128.20, 143.30, 90,
      {"1": "TIP", "2": "GNDP"})
place("Resistor_SMD", "R_0805_2012Metric", "R7", "6k8", 128.20, 147.20, 270,
      {"1": "TIP", "2": "FEEDLED"})
place("LED_SMD", "LED_0805_2012Metric", "D5", "YEL", 128.20, 150.80, 90,
      {"1": "GNDP", "2": "FEEDLED"})
place("Diode_SMD", "D_SMB", "D4", "SMBJ13CA", 129.90, 156.00, 0,
      {"1": "TIP", "2": "GNDP"})

# ---- test points -----------------------------------------------------------
for ref, val, x, y, n in [("TP1", "12V", 131.50, 120.00, "+12V"),
                          ("TP2", "10V4", 134.00, 131.00, "+10V4"),
                          ("TP4", "GND", 132.00, 145.00, "GNDP"),
                          ("TP3", "TIP", 131.50, 150.00, "TIP"),
                          ("TP5", "GNDL", 105.00, 143.00, "GNDL")]:
    place("TestPoint", "TestPoint_Pad_D1.5mm", ref, val, x, y, 0, {"1": n})

# ---- mounting holes --------------------------------------------------------
# Both sit in the isolation band, at the only X where a floor standoff in the
# enclosure clears the ESP32's right edge (118.15 in the Olimex frame) while the
# screw head still clears the parts column.
for ref, x, y in [("H1", 123.00, 118.00), ("H2", 123.50, 147.00)]:
    place("MountingHole", "MountingHole_3.2mm_M3_ISO7380", ref, "M3", x, y, 0)

# ================================================================== ROUTING
# Grounds ride the two pours; only signal and power nets are routed.
route([PP("J4", "6"), (118.60, 135.92), (118.60, 132.00), PP("R1", "1")], "GPIO32")
route([(118.60, 132.11), PP("R2", "2")], "GPIO32")
route([PP("R1", "2"), (121.60, 132.00), (121.60, 136.365), PP("U1", "1")], "LED_A")

# 12 V in -> polyfuse -> reverse-polarity Schottky -> TVS -> bulk cap -> LDO
route([PP("J1", "1"), (141.60, 121.00), (141.60, 114.00),
       (PP("F1", "1")[0], 114.00), PP("F1", "1")], "+12V_RAW", w=0.60)
route([PP("F1", "2"), (128.20, PP("F1", "2")[1]), PP("D1", "2")],
      "+12V_F", w=0.60)
route([PP("D1", "1"), PP("D2", "1")], "+12V", w=0.60)
route([PP("D2", "1"), (128.20, 122.60), (131.50, 122.60), PP("TP1", "1")],
      "+12V", w=0.60)
route([(131.50, 122.60), (134.075, 122.60), PP("C1", "1")], "+12V", w=0.60)
route([(134.075, 123.20), (145.00, 123.20), (145.00, 125.20), PP("U2", "3")],
      "+12V", w=0.60)

# LDO out: tab -> C2, divider, indicator, PhotoMOS
route([(137.85, 127.50), (144.15, 127.50)], "+10V4", w=0.60)   # tab <-> pin 2
route([PP("U2", "2"), (137.85, 131.60), (134.00, 131.60), PP("TP2", "1")],
      "+10V4", w=0.60)
route([(137.85, 131.60), (140.25, 131.60), (140.25, 134.00), PP("C2", "1")],
      "+10V4", w=0.60)
route([(140.25, 131.60), (143.9125, 131.60), PP("R4", "1")], "+10V4", w=0.60)
route([PP("TP2", "1"), (134.00, 134.00), (129.50, 134.00),
       (129.50, 136.365), PP("U1", "4")], "+10V4", w=0.60)
route([(134.00, 134.00), (134.00, 139.00), PP("R6", "1")], "+10V4", w=0.50)
route([PP("R6", "2"), PP("D3", "2")], "PWRLED")

# adjust divider
route([PP("U2", "1"), (145.00, 129.80), (145.00, 134.50), (142.0875, 134.50),
       PP("R4", "2")], "ADJ")
route([(142.0875, 134.50), PP("R5", "1")], "ADJ")

# trigger output
route([PP("U1", "3"), (130.00, 137.635), (130.00, 144.2125), PP("R3", "1")],
      "TIP", w=0.50)
route([PP("R3", "1"), PP("R7", "1")], "TIP", w=0.50)
route([PP("R7", "2"), PP("D5", "2")], "FEEDLED")
route([(130.00, 143.50), (136.65, 143.50)], "TIP", w=0.50)
route([(130.00, 144.2125), (130.00, 154.00), (127.60, 154.00), PP("D4", "1")],
      "TIP", w=0.50)
route([(130.00, 150.00), PP("TP3", "1")], "TIP", w=0.50)

for vx, vy in [(96.00, 120.00), (96.00, 150.00), (108.00, 145.00),
               (112.00, 120.00)]:
    via(vx, vy, "GNDL")
for vx, vy in [(127.50, 132.00), (134.00, 118.00), (145.00, 140.00),
               (133.00, 158.00), (127.00, 158.00),
               (126.90, 141.00), (126.90, 152.80)]:
    via(vx, vy, "GNDP")

# ==================================================================== ZONES
def zone(netname, pts, layers, prio=0):
    poly = " ".join("(xy %.4f %.4f)" % (x, y) for x, y in pts)
    lay = " ".join('"%s"' % l for l in layers)
    return """  (zone (net %d) (net_name "%s") (layers %s) (hatch edge 0.5)
    (priority %d) (connect_pads (clearance 0.25))
    (min_thickness 0.20) (filled_areas_thickness no)
    (fill yes (thermal_gap 0.35) (thermal_bridge_width 0.5))
    (polygon (pts %s)))""" % (net(netname), netname, lay, prio, poly)

M = 0.4
logic_poly = [(BX0 + M, BY0 + M), (GAP_L, BY0 + M), (GAP_L, BY1 - M), (BX0 + M, BY1 - M)]
power_poly = [(GAP_R, BY0 + M), (BX1 - M, BY0 + M), (BX1 - M, BY1 - M), (GAP_R, BY1 - M)]
ZONES = [zone("GNDL", logic_poly, ["F.Cu", "B.Cu"]),
         zone("GNDP", power_poly, ["F.Cu", "B.Cu"])]

# =============================================================== BOARD EDGE
line(BX0, BY0, BX1, BY0, "Edge.Cuts")
line(BX1, BY0, BX1, BY1, "Edge.Cuts")
line(BX1, BY1, BX0, BY1, "Edge.Cuts")
line(BX0, BY1, BX0, BY0, "Edge.Cuts")

# isolation frontier markers, broken where U1 bridges them
for lay in ("F.SilkS", "B.SilkS"):
    for x in (GAP_L + 0.5, GAP_R - 0.5):
        line(x, BY0 + 3.5, x, 134.0, lay, 0.2)
        line(x, 140.0, x, BY1 - 3.5, lay, 0.2)

# =============================================================== SILKSCREEN
text("aF4 PoE TRIGGER HAT", 107.00, 114.20, size=1.3, thick=0.24)
text("rev D    inD aF4 frozen feeder", 107.00, 116.60, size=0.85)
text("ISOLATION BARRIER", 124.00, 128.00, size=0.8, thick=0.15, rot=90)
text("EXT1", 95.60, 124.60, size=1.0)
text("EXT2", 112.40, 124.60, size=1.0)
text("PIN 1", 95.60, 121.60, size=0.75)
text("PIN 1", 112.40, 121.60, size=0.75)
text("GND = EXT1 pin 3", 105.00, 129.00, size=0.85)
text("GPIO32 = EXT2 pin 6", 105.00, 131.50, size=0.85)
text("J1 = 12V IN 5.5x2.5 CENTRE +", 105.00, 149.50, size=0.8)
text("J2 = TRIGGER OUT 3.5mm TIP", 105.00, 152.00, size=0.8)
text("10.4V 10s pulse, >=5 min apart", 105.00, 154.50, size=0.8)
text("K. Brinkman 2026", 105.00, 157.00, size=0.8)

# ==================================================================== EMIT
netdecl = "\n".join('  (net %d "%s")' % (i, n)
                    for n, i in sorted(nets.items(), key=lambda kv: kv[1]))

doc = """(kicad_pcb (version 20221018) (generator pcbnew)

  (general (thickness 1.6))
  (paper "A4")
  (title_block
    (title "aF4 PoE Trigger Hat")
    (date "2026-08-27")
    (rev "D")
    (company "inD aF4 frozen feeder")
  )

  (layers
    (0 "F.Cu" signal) (31 "B.Cu" signal)
    (32 "B.Adhes" user "B.Adhesive") (33 "F.Adhes" user "F.Adhesive")
    (34 "B.Paste" user) (35 "F.Paste" user)
    (36 "B.SilkS" user "B.Silkscreen") (37 "F.SilkS" user "F.Silkscreen")
    (38 "B.Mask" user) (39 "F.Mask" user)
    (40 "Dwgs.User" user "User.Drawings") (41 "Cmts.User" user "User.Comments")
    (42 "Eco1.User" user "User.Eco1") (43 "Eco2.User" user "User.Eco2")
    (44 "Edge.Cuts" user) (45 "Margin" user)
    (46 "B.CrtYd" user "B.Courtyard") (47 "F.CrtYd" user "F.Courtyard")
    (48 "B.Fab" user) (49 "F.Fab" user)
  )

  (setup
    (pad_to_mask_clearance 0)
    (pcbplotparams
      (layerselection 0x00010fc_ffffffff)
      (plot_on_all_layers_selection 0x0000000_00000000)
      (disableapertmacros false) (usegerberextensions false)
      (usegerberattributes true) (usegerberadvancedattributes true)
      (creategerberjobfile true) (dashed_line_dash_ratio 12.000000)
      (dashed_line_gap_ratio 3.000000) (svgprecision 6)
      (plotframeref false) (viasonmask false) (mode 1)
      (useauxorigin false) (hpglpennumber 1) (hpglpenspeed 20)
      (hpglpendiameter 15.000000) (pdf_front_fp_property_popups true)
      (pdf_back_fp_property_popups true) (dxfpolygonmode true)
      (dxfimperialunits true) (dxfusepcbnewfont true) (psnegative false)
      (psa4output false) (plotreference true) (plotvalue false)
      (plotinvisibletext false) (sketchpadsonfab false) (subtractmaskfromsilk true)
      (outputformat 1) (mirror false) (drillshape 1) (scaleselection 1)
      (outputdirectory "gerbers/")
    )
  )

%s

%s

%s

%s

%s
)
""" % (netdecl, "\n".join(FPS), "\n".join(gfx), "\n".join(segs + vias), "\n".join(ZONES))

open("af4-trigger-hat.kicad_pcb", "w").write(doc)
for ref, num, a, b, na, nb in WIDENED:
    print("  widened slot %s pad %s: %.2fx%.2f -> %.2fx%.2f mm" % (ref, num, a, b, na, nb))
print("nets %d | footprints %d | segments %d | board %.1f x %.1f mm"
      % (len(nets) - 1, len(FPS), len(segs), BX1 - BX0, BY1 - BY0))
