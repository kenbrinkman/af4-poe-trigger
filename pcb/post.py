#!/usr/bin/env python3
"""Fill zones, run DRC, and report on the generated board."""
import pcbnew, sys, os, re

BRD = "af4-trigger-hat.kicad_pcb"
b = pcbnew.LoadBoard(BRD)

# --- fill copper pours ------------------------------------------------------
filler = pcbnew.ZONE_FILLER(b)
zones = b.Zones()
filler.Fill(zones)
b.BuildConnectivity()
pcbnew.SaveBoard(BRD, b)
print("zones filled:", len(zones))
for z in zones:
    print("   net=%-8s layers=%s  filled=%s"
          % (z.GetNetname(), z.GetLayerSet().FmtHex(), z.IsFilled()))

# --- DRC --------------------------------------------------------------------
pcbnew.WriteDRCReport(b, "drc.rpt", pcbnew.EDA_UNITS_MILLIMETRES, True)
rpt = open("drc.rpt").read()
print("\n===== DRC =====")
for line in rpt.splitlines():
    if line.startswith("**") or "violation" in line.lower() or "unconnected" in line.lower():
        print(" ", line)
errs = [l for l in rpt.splitlines() if l.strip().startswith("[")]
print("total flagged items:", len(errs))
from collections import Counter
c = Counter(re.match(r"\[([a-z_]+)\]", l.strip()).group(1) for l in errs)
for k, n in c.most_common():
    print("   %-28s %d" % (k, n))
open("drc_summary.txt", "w").write(rpt)

# --- connectivity -----------------------------------------------------------
print("\n===== nets =====")
for code, name in sorted(b.GetNetsByNetcode().items()):
    if code == 0:
        continue
    pads = [p for p in b.GetPads() if p.GetNetCode() == code]
    print("  %-10s pads=%d" % (name.GetNetname(), len(pads)))
