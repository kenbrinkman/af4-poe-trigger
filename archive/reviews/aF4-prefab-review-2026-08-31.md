# Independent pre-fabrication review — aF4 PoE trigger hat, rev E

**Date:** 2026-08-31
**Reviewer:** independent pass (Claude Fable), against the staged rev E package
**Scope:** the five items no one but the author had checked, before the PCBWay resubmission
**Companion document:** `aF4-audit-2026-08-28.md`, which audited **rev D** and predates the U1 fix

---

## Bottom line

**Nothing in this package should stop the order.** All five items pass on independent
verification, four of them fully against primary sources, with one narrow and explicitly
bounded residual on the U1 land pattern. One human action is recommended before payment,
as a precaution rather than a blocker.

---

## Item 1 — U1 land pattern: VERIFIED, with one stated residual

**Footprint file** (`pcb/footprints/aF4.pretty/AQY212GS_SOP4_Panasonic.kicad_mod`, read
directly): pads at (+/-3.0, +/-1.27), size 1.2 mm (lead axis) x 0.8 mm (pitch axis),
2.54 mm pitch, 6.0 mm centre span, pads spanning 2.40-3.60 mm from part centre. Pin 1
top-left with a silk dot, counterclockwise numbering — standard SOP-4. Matches the
recorded intent exactly.

**Board placement** (via `pcbnew` on `pcb/af4-trigger-hat.kicad_pcb`): U1 at
(124.0, 137.0) rotation 0; absolute pads land at x = 121.0 / 127.0, y = 135.73 / 138.27.
Nets: pin 1 = LED_A (anode, driven through R1), pin 2 = GNDL (cathode), pins 3/4 =
TIP / +10V4 (symmetric output, no polarity). Correct for a 1-Form-A PhotoMOS. Pads carry
F.Cu + F.Paste + F.Mask, so paste apertures exist.

**Primary source:** direct download of `semi_eng_gu_sop4_1a.pdf` is blocked. The egress
proxy answers 403 to CONNECT for panasonic.com, mm.digikey.com and datasheet.octopart.com
alike, so the drawing could not be obtained as an image, which is the only method that has
previously worked on this project. Instead, two differently-prompted extractions were run
against Digi-Key's mirror of the exact Panasonic document. A full ordered number dump shows
the package outline run (4.4 +/-0.2, 4.3 +/-0.2, 2.1 +/-0.2, 2.54 +/-0.1, 0.4,
**6.8 +/-0.4**, 0.05) immediately followed by the recommended-mounting-pad callouts:
**0.4, 1.2, 0.8, 2.54 +/-0.1**. Every number in the footprint appears as a printed callout
on Panasonic's own drawing, and a "0.8, 0.4, 2.4, 1.2" run corroborates the 2.4 mm
inner-edge offset. Nothing in the document supports either of the two earlier scrambled
readings (0.5 x 1.0, or 0.4 x 2.54).

**The residual:** which of 0.8 / 1.2 goes on which axis is precisely what a number list
cannot prove. That is the exact species of the third defect in this project's history, and
it is therefore not reported as seen.

**What bounds it:** the lead span is confirmed printed as 6.8 +/-0.4, so lead tips land
3.2-3.6 mm from centre. Only the orientation actually used — 1.2 mm along the lead axis,
pad ending at 3.6 — covers the tip across the whole tolerance range. The rotated assignment
would end pads at 3.4 and lose the toe at maximum tolerance, which is the precise failure
the earlier audit caught. The chosen orientation is the only one consistent with the
confirmed span.

**Recommended pre-payment action:** open the PDF on any unrestricted machine and look at
the pad drawing for sixty seconds.

**GS suffix:** Digi-Key lists AQY212GS as 4-SOP (0.173", 4.40 mm) — the SMD SOP-4, not the
GH DIP. The BOM orders exactly `AQY212GS`.

## Item 2 — DRC and geometry: VERIFIED (independently re-run)

KiCad 7.0.11 installed, zones filled with `ZONE_FILLER`, `pcbnew.WriteDRCReport` re-run
from scratch: **61 items — 28 lib_footprint_issues, 16 silk_overlap, 8 silk_edge_clearance,
7 silk_over_copper, 2 text_height; zero clearance, courtyard, hole, edge, unconnected or
mask items.** Identical to the claimed counts.

Items were read in every class rather than assumed cosmetic. lib_footprint_issues is
"library not in table" (footprints are embedded, no fab effect); silk_over_copper is
"clipped by solder mask" (the fab clips it); silk_edge items are overhanging connector
outlines; text_height is 0.75 mm against a 0.8 mm minimum. Genuinely cosmetic.

**Drill file** (`pcb/gerbers/af4-trigger-hat.drl`, read directly): tool list exactly
0.45 / 0.70 / 0.80 / 1.00 / 1.20 / 2.13 / 3.20 mm, 47 entries. All 8 slots (G85) are plated
tools T2 = **0.70 mm** and T3 = **0.80 mm**. The 0.70 mm floor was actually enforced in the
shipped file; no 0.60 or 0.40 mm slots survived from the stock footprints.

**Clearance — this corrects a standing project belief.** DRC was swept at multiple rules on
the real filled board: **zero violations at 0.2032 mm (8 mil) and at 0.24 mm; first hits at
0.25 mm.** True minimum copper gap is 0.24-0.25 mm, minimum track 0.35 mm, vias 0.9 / 0.45.
The board is clean even at an 8/8 mil order setting. The 0.20 mm figure carried in the docs
is the **KiCad netclass default**, conservative relative to the real geometry. Ordering 6/6
remains correct, but it is not the cliff edge the notes have treated it as.

**Gerber authenticity:** copper, mask, paste and edge layers were re-exported from the
`.kicad_pcb` and diffed against the shipped files. Identical, except for drill-mark flashes
the re-plot added and one 40 micron zone-fill vertex. The shipped Gerbers are genuinely from
this board, with pours filled.

**Isolation band:** both shipped copper Gerbers were parsed for flashes, vertices and
crossing strokes strictly inside x 121.65-126.35. Zero on both layers. The band is clear.

## Item 3 — All 20 MPNs against live listings: VERIFIED (all exist)

Every line found by exact string on a live distributor listing, Digi-Key unless noted:
AQY212GS (571632); LM1117MPX-ADJ/NOPB (also LCSC C263277); SS14-E3/61T (1091538); SMAJ13A
Littelfuse (762272); SMBJ13CA Littelfuse (285976); APT2012SGC (1747530, LCSC C5353439);
**APT2012SYCK** (1747533); **1206L010/60WR** (Newark 39AH9731, Mouser, TTI, Arrow;
Digi-Key carries the `-A` reel variant 11205749); **GRM31CR61H106KA12L** (Digi-Key 3693684,
LCSC C77092); T491B106K025AT (1681740); RC0805FR-07220RL (727741); RC0805FR-0710KL (727535);
RC0805FR-07100KL (727544, Mouser); RC0805FR-07121RL (Arrow, SnapEDA); RC0805FR-07887RL
(728182); RC0805FR-071KL (727444); RC0805FR-076K8L (728066); PJ-079BH (9830149 plus
sameskydevices.com); SJ1-3523N (738689); PPTC101LFBN-RC (810149).

**No plain "APT2012SYC" listing exists anywhere**, confirming the original was fabricated
rather than merely obsolete.

**F1 parametrics confirmed at Newark:** hold 100 mA, trip 250 mA, 60 VDC. Matches the BOM.

**PJ-079BH's 2.5 mm centre pin confirmed on Same Sky's own product page**, 24 V / 5 A.

Existence was checked for all 20 lines. Stock depth was counted only for the two flagged
lines, F1 and C1; the other 18 are taken on the listing's presence.

## Item 4 — C1 sourcing: EOL pattern corroborated, WELL STOCKED, alternate nominated

Murata's own product page returned 403, so the **official EOL notice remains unverified from
Murata directly.** The distributor pattern strongly corroborates it: Digi-Key, Newark and TTI
all show zero stock while the listings stay up.

**The decisive fact: LCSC — PCBWay's natural source — holds roughly 123,710 pieces at about
$0.23 (C77092)**, with TME holding around 900 more. For a five-board run this question
closes. C1 is comfortably sourceable.

**Nominated alternate, from live listings rather than recall:
`C3216X5R1H106K160AB` (TDK)** — 10 uF, 50 V, X5R, 1206, +/-10%, active at Digi-Key
(2443476), Newark, TTI, and LCSC / JLCPCB (C2167848). Drop-in on the C_1206 pad. This
belongs in the remark box as a pre-approved substitute, so the choice is never made at the
bench.

## Item 5 — BOM = centroid = board: VERIFIED (exact)

BOM: 20 lines, 21 parts (J3 and J4 at quantity 2). The board's reference set from pcbnew,
minus H1/H2 and TP1-TP5, is exactly the BOM's 21 designators. R6 and R7 are present on the
board, in the BOM, and in the centroid.

**Centroid: all 17 SMD rows recomputed against the board, 0 mismatches** — origin at the
lower-left corner (89.15, 160.0), Y increasing upward, counterclockwise rotations, exactly
as the README declares. Through-hole parts and test points correctly absent.

**Joints confirmed from two independent primary sources.** pcbnew PTH pad counts give
J1 = 5, J2 = 3, J3 = 10, J4 = 10, total **28**. The shipped drill file independently agrees:
three 0.8 mm slots plus two 0.7 mm slots at J1, three 0.7 mm slots at J2, and twenty 1.0 mm
holes across J3 and J4. The "44" fiction appears nowhere in the shipped README — only in the
inquiry text that explicitly repudiates it. `pcb/make_package.py` now computes the count from the
board and asserts BOM-to-board reference equality.

The three package files in `pcb/` are byte-identical to the zip's contents, and the zip holds
the 15 files the inquiry text promises.

---

## Minor findings, none blocking

1. **The Part 2 letter to Ivy is stale.** It tells her team to pull up the parts review on
   T-3P4W1125728A, a quotation since deleted at the vendor, so the expectation may simply
   fail. Harmless, but reword before sending.
2. **J2 carries "exclude from BOM / exclude from pos" flags in the board file.** Metadata
   inconsistency only. The shipped BOM lists J2 correctly and the generator cross-checks by
   reference name, so there is no fab effect. Worth fixing in `pcb/gen_pcb.py` eventually.
3. **R5 arithmetic confirmed.** 9.22 V across 887 ohms is about 96 mW in a 125 mW 0805, or
   77%. Vout = 1.25 x (1 + 887/121) + Iadj x 887, about 10.47 V, as claimed. In spec, runs
   hot. A thin-film 0.25 W part is a future nicety, not a change to make now.
4. **Digi-Key stocks F1 only as `1206L010/60WR-A`** (same device, packaging suffix);
   Mouser and Newark stock the plain `/60WR`. If PCBWay proposes the `-A`, it is legitimate.

---

## Confirmed versus trusted

Everything above was checked against the board file, the shipped Gerbers and drill file, an
independent DRC re-run, or a named live distributor listing — **except** three things, stated
here so the boundary of this review is not mistaken for a clean sweep:

- **the visual axis assignment** on Panasonic's pad drawing, bounded by the printed-callout
  extraction and the lead-span argument above, with a sixty-second human check recommended;
- **Murata's official EOL notice** for C1, corroborated only by the zero-stock pattern at
  three authorized distributors;
- **stock depth on the 18 unflagged BOM lines**, where existence was checked but stock was
  not counted.

---

## Sources

Panasonic SOP-4 pad drawing, Digi-Key mirror:
https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8522/semi_eng_gu_sop4_1a%20%282%29.pdf
AQY212GS: https://www.digikey.com/en/products/detail/panasonic-electric-works/AQY212GS/571632
1206L010/60WR, Newark:
https://www.newark.com/littelfuse/1206l010-60wr/fuse-resettable-ptc-60vdc-0-1a/dp/39AH9731
1206L010/60WR-A: https://www.digikey.com/en/products/detail/littelfuse-inc/1206L010-60WR-A/11205749
GRM31CR61H106KA12L: https://www.digikey.com/en/products/detail/murata-electronics/GRM31CR61H106KA12L/3693684
GRM31CR61H106KA12L, LCSC: https://www.lcsc.com/product-detail/C77092.html
C3216X5R1H106K160AB (nominated alternate):
https://www.digikey.com/en/products/detail/tdk-corporation/C3216X5R1H106K160AB/2443476
APT2012SYCK: https://www.digikey.com/en/products/detail/kingbright/APT2012SYCK/1747533
APT2012SGC: https://www.digikey.com/en/products/detail/kingbright/APT2012SGC/1747530
LM1117MPX-ADJ/NOPB, LCSC: https://www.lcsc.com/product-detail/C263277.html
SS14-E3/61T: https://www.digikey.com/en/products/detail/vishay-general-semiconductor-diodes-division/SS14-E3-61T/1091538
SMAJ13A: https://www.digikey.com/en/products/detail/littelfuse-inc/SMAJ13A/762272
SMBJ13CA: https://www.digikey.com/en/products/detail/littelfuse-inc/SMBJ13CA/285976
T491B106K025AT: https://www.digikey.com/en/products/detail/kemet/T491B106K025AT/1681740
PJ-079BH, Same Sky:
https://www.sameskydevices.com/product/interconnect/connectors/dc-power-connectors/jacks/pj-079bh
SJ1-3523N: https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/SJ1-3523N/738689
PPTC101LFBN-RC: https://www.digikey.com/en/products/detail/sullins-connector-solutions/PPTC101LFBN-RC/810149
