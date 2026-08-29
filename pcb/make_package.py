#!/usr/bin/env python3
"""Build the PCBWay upload package: BOM, centroid, fab notes, zip."""
import csv, os, math, zipfile, shutil
import pcbnew

BRD = "af4-trigger-hat.kicad_pcb"
b = pcbnew.LoadBoard(BRD)

# board origin: lower-left corner, Y up (unambiguous for the assembler)
bbox = b.GetBoardEdgesBoundingBox()
X0 = pcbnew.ToMM(bbox.GetLeft())
Y1 = pcbnew.ToMM(bbox.GetBottom())
W = pcbnew.ToMM(bbox.GetWidth()) - 0.15   # edge line is 0.15 mm wide
H = pcbnew.ToMM(bbox.GetHeight()) - 0.15
X0 += 0.075
Y1 -= 0.075
print("board %.2f x %.2f mm, origin at (%.3f, %.3f)" % (W, H, X0, Y1))

# --------------------------------------------------------------------- BOM
# Manufacturer part numbers. PCBWay sources turn-key orders by MPN.
PARTS = [
    # refs, qty, description, package, type, manufacturer, mpn, notes
    (["U1"], "PhotoMOS solid-state relay, 1 Form A, 60 V / 1 A, 1500 Vrms isolation",
     "SOP-4", "SMD", "Panasonic", "AQY212GS",
     "Isolates ESP32 logic from the feeder supply. Pins 3/4 are a symmetric "
     "MOSFET pair - no polarity."),
    (["U2"], "LDO regulator, adjustable, 800 mA", "SOT-223", "SMD",
     "Texas Instruments", "LM1117MPX-ADJ/NOPB",
     "Tab is VOUT. Set to 10.4 V by R4/R5."),
    (["D1"], "Schottky rectifier, 40 V / 1 A", "SMA (DO-214AC)", "SMD",
     "Vishay", "SS14-E3/61T", "Reverse-polarity protection, in series with the 12 V input."),
    (["D2"], "TVS diode, unidirectional, 13 V standoff, 400 W", "SMA (DO-214AC)",
     "SMD", "Littelfuse", "SMAJ13A",
     "Input clamp. Standoff sits above the 12 V rail; cathode to +12 V."),
    (["D4"], "TVS diode, bidirectional, 13 V standoff, 600 W", "SMB (DO-214AA)",
     "SMD", "Littelfuse", "SMBJ13CA",
     "Across the trigger pair at the jack. Bidirectional - no orientation."),
    (["D3"], "LED, green, 2.2 V typ", "0805", "SMD", "Kingbright", "APT2012SGC",
     "10.4 V rail live indicator."),
    (["D5"], "LED, yellow, 2.0 V typ", "0805", "SMD", "Kingbright", "APT2012SYCK",
     "Lights while the trigger output is asserted."),
    (["F1"], "PPTC resettable fuse, 0.10 A hold / 0.25 A trip, 60 V", "1206", "SMD",
     "Littelfuse", "1206L010/60WR",
     "On the 12 V tap. Feeder supply can source 12.5 A."),
    (["C1"], "Capacitor, 10 uF, 50 V, X5R", "1206", "SMD", "Murata",
     "GRM31CR61H106KA12L", "Regulator input bulk."),
    (["C2"], "Capacitor, tantalum, 10 uF, 25 V", "EIA-3528 (case B)", "SMD",
     "Kemet", "T491B106K025AT",
     "Regulator output. Tantalum is required - the LM1117 needs output-cap ESR. "
     "POLARISED: + to the 10.4 V rail."),
    (["R1"], "Resistor, 220 R, 1%, 1/8 W", "0805", "SMD", "Yageo",
     "RC0805FR-07220RL", "PhotoMOS LED current set, ~9 mA from GPIO32."),
    (["R2"], "Resistor, 10 k, 1%, 1/8 W", "0805", "SMD", "Yageo",
     "RC0805FR-0710KL", "GPIO32 pulldown - holds the PhotoMOS off at boot."),
    (["R3"], "Resistor, 100 k, 1%, 1/8 W", "0805", "SMD", "Yageo",
     "RC0805FR-07100KL", "Trigger-line bleed, guarantees the 0 V re-arm."),
    (["R4"], "Resistor, 121 R, 1%, 1/8 W", "0805", "SMD", "Yageo",
     "RC0805FR-07121RL", "LM1117 divider, VOUT to ADJ."),
    (["R5"], "Resistor, 887 R, 1%, 1/8 W", "0805", "SMD", "Yageo",
     "RC0805FR-07887RL",
     "LM1117 divider, ADJ to GND. Vout = 1.25*(1+887/121) + Iadj*887 = 10.47 V."),
    (["R6"], "Resistor, 1.0 k, 1%, 1/8 W", "0805", "SMD", "Yageo",
     "RC0805FR-071KL",
     "D3 green LED series resistor. 8.2 mA - APT2012SGC is only 12 mcd at 20 mA, "
     "so it needs the current to be readable through the lid sight hole."),
    (["R7"], "Resistor, 6.8 k, 1%, 1/8 W", "0805", "SMD", "Yageo",
     "RC0805FR-076K8L",
     "D5 yellow LED series resistor. 1.2 mA - APT2012SYCK is 150 mcd at 20 mA, "
     "so it needs far less current than D3 to match it."),
    (["J1"], "DC power jack, 5.5 x 2.5 mm, 2.5 mm centre pin, 24 V / 5 A",
     "Right-angle THT", "THT", "Same Sky (CUI)", "PJ-079BH",
     "MUST be the 2.5 mm centre-pin part. Terminal 3 (switch) is unconnected."),
    (["J2"], "Audio jack, 3.5 mm, 3-conductor, right angle", "THT", "THT",
     "Same Sky (CUI)", "SJ1-3523N",
     "Tip = trigger signal. Ring is tied to sleeve on the board."),
    (["J3", "J4"], "Socket header, 1x10, 2.54 mm, vertical", "THT", "THT",
     "Sullins", "PPTC101LFBN-RC",
     "Mates the Olimex ESP32-POE-ISO EXT1/EXT2 headers."),
]

rows = []
for i, (refs, desc, pkg, typ, mfr, mpn, note) in enumerate(PARTS, 1):
    rows.append({
        "Line#": i,
        "Quantity Per Part Number": len(refs),
        "Reference Designator": ",".join(refs),
        "Part Number": mpn,
        "Part Description": desc,
        "Package": pkg,
        "Type": typ,
        "Manufacturers Name": mfr,
        "Manufacturers Part Number": mpn,
        "Distributors Part Number": "",
        "Notes": note,
    })

with open("af4-trigger-hat-BOM.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("BOM lines:", len(rows), " total placements:",
      sum(r["Quantity Per Part Number"] for r in rows))

# cross-check the BOM against the board
board_refs = {f.GetReference() for f in b.GetFootprints()
              if not f.GetReference().startswith(("H", "TP"))}
bom_refs = {r for p in PARTS for r in p[0]}
assert board_refs == bom_refs, ("BOM/board mismatch:",
                                board_refs ^ bom_refs)
print("BOM cross-check against board: OK (%d parts)" % len(bom_refs))

# ---------------------------------------------------------------- centroid
# PCBWay: "Only surface mounting parts are listed in the Centroid."
with open("af4-trigger-hat-centroid.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Mid X (mm)", "Mid Y (mm)", "Layer", "Rotation"])
    n = 0
    for fp in sorted(b.GetFootprints(), key=lambda x: x.GetReference()):
        ref = fp.GetReference()
        if ref.startswith(("H", "TP")):
            continue
        if fp.GetAttributes() & pcbnew.FP_THROUGH_HOLE:
            continue
        p = fp.GetPosition()
        x = pcbnew.ToMM(p.x) - X0
        y = Y1 - pcbnew.ToMM(p.y)
        rot = fp.GetOrientationDegrees() % 360
        side = "top" if fp.GetLayer() == pcbnew.F_Cu else "bottom"
        w.writerow([ref, "%.3f" % x, "%.3f" % y, side, "%.1f" % rot])
        n += 1
print("centroid rows (SMD only):", n)

# through-hole joint count, computed from the board - never hand-written.
# (An earlier hand-written "4 parts / 44 joints" survived here for revisions while
# the itemised list directly beneath it summed to 28. PCBWay prices hand-soldered
# joints, so that fiction had a price attached to it.)
tht = []
for fp in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    ref = fp.GetReference()
    if ref.startswith(("H", "TP")):
        continue
    pth = [p for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    if pth:
        tht.append((ref, len(pth)))
tht_parts = len(tht)
tht_joints = sum(c for _, c in tht)
tht_lines = "\n".join("                      %-3s %2d joints" % (r, c) for r, c in tht)
print("THT: %d parts / %d joints" % (tht_parts, tht_joints))

# ------------------------------------------------------------- fab README
open("PCBWay-README.txt", "w").write("""aF4 PoE Trigger Hat - rev E
Fabrication and assembly notes for PCBWay

BOARD
  Size              %.2f x %.2f mm (rectangular)
  Layers            2
  Thickness         1.6 mm
  Copper            1 oz
  Surface finish    ENIG preferred (HASL acceptable)
  Soldermask        any colour
  Silkscreen        white
  Min trace/space   0.35 mm / 0.20 mm  (well inside standard capability)
  Min drill         0.45 mm (stitching vias)
  Slots             plated, min width 0.70 mm (connector blade terminals on
                    J1 and J2). Deliberately widened from the 0.40 mm the
                    library footprint specifies, which is below routing
                    minimum; annular ring is 0.25 mm at the worst pad.
  Castellations     none
  Panelisation      not required

ASSEMBLY
  Quantity          5
  Sides populated   top only
  Unique part nos.  %d
  SMD placements    %d
  Through-hole      %d parts / %d joints:
%s
  Sourcing          full turn-key, by manufacturer part number (see BOM)

COORDINATE SYSTEM
  The centroid file uses the board's lower-left corner as (0,0) with Y
  increasing upward. Rotations are counter-clockwise in degrees.

CRITICAL NOTES
  1. J1 must be the 2.5 mm centre-pin variant (PJ-079BH). The visually
     similar PJ-002AH / PJ-102AH are 2.0-2.1 mm and will not fit the
     supplied power plug.
  2. C2 is a POLARISED tantalum. The + terminal goes to the 10.4 V rail
     (pad 1, marked on silkscreen and fab layer).
  3. D1, D2, D3, D5 are polarised. D4 is bidirectional - orientation
     does not matter.
  4. U1 straddles a deliberate copper-free isolation band running the
     height of the board. Do not add copper, vias or stitching in that
     band; it is the barrier between the logic side and the feeder-power
     side of the circuit.
  5. J3 and J4 must be seated flush and square - they mate with a header
     on another board and any tilt will prevent assembly.
""" % (W, H, len(rows), n, tht_parts, tht_joints, tht_lines))

# ------------------------------------------------------------------- zip
with zipfile.ZipFile("af4-trigger-hat-rev-E-PCBWay.zip", "w",
                     zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir("gerbers")):
        z.write(os.path.join("gerbers", fn), "gerbers/" + fn)
    for fn in ["af4-trigger-hat-BOM.csv", "af4-trigger-hat-centroid.csv",
               "PCBWay-README.txt"]:
        z.write(fn)
print("wrote af4-trigger-hat-rev-E-PCBWay.zip")
