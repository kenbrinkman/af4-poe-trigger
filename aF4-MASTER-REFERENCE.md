# aF4 PoE Trigger — Master Reference (rev E)

**Purpose of this document.** A single consolidated reference for the aF4 frozen-feeder
PoE trigger project, written to be *audited*. Every load-bearing claim carries a provenance
tag so a reviewer can tell what has been verified against a primary source and what is an
assertion that has not. The assertions are the interesting part — attack those first.

> 🔑 **Do not read this file whole** — it costs ~24,000 tokens. Use the section index
> below, then `grep -n "^### 2.4"` and read only that range.
>
> 🚫 **This file does not describe current state.** For phase, what may be trusted, and the
> open-items ledger, read **`STATUS.md`** — it is the only live-status document in this
> project. §8 below is the ledger of record for **item numbering**; `STATUS.md` is the
> ledger of record for **what is still open**.

Generated 2026-08-28, revised after independent audit the same day, after the 2026-09-01
bench and vendor-documentation passes, after the 2026-09-02 order went to fabrication, and
after the 2026-09-11 assembly-sample EQ found J3 and J4 built on the wrong face (§A3), after
the reworked board was verified and accepted 2026-09-12 (§A3.1), and after the order shipped
2026-09-14 (§A3.2). Canonical source for this file is the repo; the other project docs
(`docs/aF4-reference.md`, `docs/aF4-pcb-notes.md`, `docs/aF4-esp32-trigger-BOM.md`,
`docs/aF4-enclosure-notes.md`, `docs/aF4-assembly-guide.md`) remain authoritative in their own areas
and go deeper. This document does not replace them; it makes the whole thing checkable in
one pass.

## Provenance tags used throughout

| Tag | Meaning |
|---|---|
| `[MEAS]` | Kenny measured it on the physical hardware, date given |
| `[DS]` | Read off the manufacturer datasheet, verified 2026-08-28 |
| `[DIST]` | Manufacturer part number confirmed as a real, stocked part at a distributor, 2026-08-28 |
| `[CAD]` | Taken from vendor CAD source (Olimex ESP32-POE-ISO Rev N KiCad files) |
| `[SPEC]` | From inD aquatics' published 0-10 V setup guide |
| `[CALC]` | Derived. Inputs and working shown so the arithmetic can be rechecked |
| `[ASSERT]` | **Stated but not independently verified.** Treat as unproven |
| `[EQ]` | Found in a PCBWay engineering-query exchange, from photographs of the built boards |

---

<!-- SECTION-INDEX -->
## Section index

> 🔑 **Do not read this file whole.** Find the section here, then read only its
> line range. Numbers drift — confirm with `grep -n "^### 2.4" <file>`.

  - §A1 U1 is on the wrong footprint — the board cannot be built `[AUDIT]` — L126
  - §A1.1 FIXED — a project-local footprint built from Panasonic's drawing — L144
  - §A1.2 Rejected: `SO-4_4.4x4.3mm_P2.54mm`, matched on dimensions but not on pad shape — L167
  - §A1.3 Isolation, re-derived `[AUDIT]` — L196
  - §A2 `pcb/gen_pcb.py` says `SMAJ15A` for D2; everything else says `SMAJ13A` `[AUDIT]` — L218
  - §A3 J3/J4 are built on the wrong face — the fab data cannot carry a THT mounting side `[EQ]` — L229
  - §A3.1 Rework verified from photographs, and accepted with two defects open `[EQ] 2026-09-12` — L286
  - §A3.2 The EQ closed and the order shipped `[EQ] 2026-09-14` — L334
  - §A4 J1, the 12 V barrel jack, faces inboard on all five boards `[CAD] 2026-09-18` — L380
- **§1 What the system must do** — L576
  - §1.1 Requirements — L584
  - §1.2 Measured facts about the port — L595
  - §1.3 ⚠️ `[VENDOR] 2026-09-01` inD publishes THREE different hold times — L612
  - §1.4 ✅ `[VENDOR] 2026-09-01` RESOLVED — and the assumption was backwards — L652
- **§2 Circuit** — L681
  - §2.1 Regulator — the calculation that matters — L728
  - §2.2 Load on the 10.4 V rail — L761
  - §2.3 PhotoMOS drive — L812
  - §2.4 The GPIO13 problem — why the trigger is on GPIO32 — L837
  - §2.5 Protection — L879
  - §2.6 Indicator LEDs — L902
- **§3 Bill of materials — with verification status** — L936
  - §3.1 Sourcing traps recorded — L965
  - §3.2 Bought separately (not on the board) — L973
- **§4 Board** — L981
  - §4.1 Geometry from vendor CAD `[CAD]` — L999
  - §4.2 Verification status of the board — L1009
  - §4.3 Isolation — L1031
  - §4.4 The ordered board re-checked on KiCad 9.0.7 `[MEAS] 2026-09-17` — L1044
- **§5 Firmware** — L1079
  - §5.1 The safety architecture — L1085
  - §5.2 Timing check against the spec `[CALC]` — L1102
  - §5.3 ✅ `[AUDIT]` The lockout did not survive a reboot — CLOSED 2026-09-01 — L1122
  - §5.4 ✅ `[AUDIT]` The web server was a second, unauthenticated control path — CLOSED 2026-09-01 — L1146
  - §5.5 ✅ The related hygiene problem — the worse one — CLOSED 2026-09-02 — L1157
  - §5.6 `[AUDIT]` Held-high failure modes are bounded — the design's best safety property — L1175
  - §5.7 Home Assistant integration — L1186
- **§6 Enclosure** — L1267
  - §6.1 The vertical stack — the governing dimension — L1275
  - §6.2 Two details that are easy to lose — L1310
  - §6.3 The hat collided with an Olimex capacitor — raised 1.5 mm `[MEAS] 2026-09-16` — L1328
  - §6.4 Lid label turned to read portrait `2026-09-16` — L1441
- **§7 Errors already found and fixed** — L1461
  - §7.1 The inverse failure mode, named 2026-09-02 — L1496
- **§8 Open items** — L1516
  - §8.1 Commissioning gate (from `docs/aF4-assembly-guide.md` §6) — L1569
- **§9 Repository map** — L1600
  - §9.1 Toolchain constraints worth knowing — L1623
  - §9.2 The toolchain under Claude Code on the Mac `[MEAS] 2026-09-17` — L1638
- **§10 Audit status** — L1680
  - §10.1 Still unverified after the audit — L1696
  - §10.2 Bench work still unrun (`docs/aF4-meter-test-battery.md`) — L1730
- **§11 The PoE board was replaced `[MEAS] 2026-09-18`** — L1742
  - §11.1 Every board has two MACs, three apart, and the two systems use different ones — L1757
  - §11.2 Home Assistant migrates the device; it does not need a delete and re-add — L1776
  - §11.3 The OPNsense reservation is one line — L1798
  - §11.4 The OTA password rotation, and the character that broke it — L1810
  - §11.5 The standing corrections — L1835
- **§12 Commissioning passed, end to end `[MEAS] 2026-09-18`** — L1857
  - §12.1 Polarity, settled by meter — L1870
  - §12.2 The numbers — L1881
  - §12.3 The reef system is plumbed and running — L1918
  - §12.4 What a manual feed deliberately does not touch — L1937
  - §12.5 The decision taken, and the one question it opens — L1951
  - §12.6 The standing corrections — L1965
- **§13 The retired board was erased `[MEAS] 2026-09-19`** — L1981
  - §13.1 Erase, don't overwrite — and verify by read-back — L2004
  - §13.2 What survives, and what it means for reuse — L2020
  - §13.3 The standing corrections — L2041
- **§14 The case is closed, mounted, and the system is live `[MEAS] 2026-09-19`** — L2054
  - §14.1 The 23:45 "missed feed(s)" alert was correct, and cannot recur — L2084
  - §14.2 The standing corrections — L2102

<!-- /SECTION-INDEX -->

---

## A. Build blockers

### A1. U1 is on the wrong footprint — the board cannot be built `[AUDIT]`

`pcb/gen_pcb.py` places U1 on KiCad's `Package_SO:SO-4_4.4x2.3mm_P1.27mm`. That footprint's
own description points at an **OPTEK OPIA403** optocoupler: pads at x = ±3.15 mm,
y = ±0.635 mm — a **1.27 mm terminal pitch**.

The Panasonic AQY212GS is not that package. From Panasonic's own GU SOP4 datasheet
(`semi_eng_gu_sop4_1a.pdf`) `[DS]`:

| Parameter | AQY212GS (Panasonic) | Footprint in use |
|---|---|---|
| **Terminal pitch** | **2.54 mm** | **1.27 mm** ❌ |
| Body | 4.4 × 4.3 mm | 4.4 × 2.3 mm ❌ |
| Lead span, tip to tip | 6.8 ± 0.4 mm | 6.30 mm pad centres |
| Recommended pad | 0.5 × 1.0 mm on 2.54 mm pitch | 0.64 × 2.0 mm on 1.27 mm |

Every pin missed its pad by ~0.635 mm along the pin row.

### A1.1 FIXED — a project-local footprint built from Panasonic's drawing

**Final answer: `pcb/footprints/aF4.pretty/AQY212GS_SOP4_Panasonic.kicad_mod`**, authored from the
"Recommended mounting pad (TOP VIEW)" drawing in `semi_eng_gu_sop4_1a.pdf`:

| Panasonic recommended pad | Value |
|---|---|
| Pad size | **0.8 mm** across the pitch axis × **1.2 mm** along the lead axis |
| Pad centres, pitch axis | 2.54 mm |
| Pad centres, span axis | **6.0 mm** (±3.0) |
| Tolerance | ±0.1 mm |

Pads therefore span 2.40–3.60 mm from the part centre, against a lead tip at 3.2–3.6 mm
(6.8 ± 0.4 span). Toe lands on the pad across the whole tolerance range.

> **An interim fix got this wrong in an instructive way.** Before the drawing was readable,
> KiCad's `SO-4_4.4x4.3mm_P2.54mm` was used — it has the correct pad **centres** (±3.0,
> ±1.27) and an exact body match, but **its pads are rotated 90°**: 0.8 mm along the lead
> axis where Panasonic asks for 1.2 mm, and 1.2 mm across the pitch axis where Panasonic
> asks for 0.8 mm. The part would have mounted, but with no toe fillet at the far end of the
> lead-span tolerance. A footprint can match on pitch, body and pad centres and still be the
> wrong land pattern. **Read the drawing.**

### A1.2 Rejected: `SO-4_4.4x4.3mm_P2.54mm`, matched on dimensions but not on pad shape

`SOP-4_3.8x4.1mm_P2.54mm` was rejected: right pitch, but pad centres only 5.50 mm apart,
too narrow for a 6.8 mm lead span. The footprint now used matches Panasonic on every
dimension that exists in both:

| | Panasonic AQY212GS | `SO-4_4.4x4.3mm_P2.54mm` |
|---|---|---|
| Body | 4.4 × 4.3 mm | F.Fab outline 4.4 × 4.3 mm — exact |
| Terminal pitch | 2.54 mm | pads at y = ±1.27 — exact |
| Lead span | 6.8 ± 0.4 mm → tips at 3.2–3.6 | pads span 2.6–3.4 from centre |
| Pad 1 quadrant | — | unchanged, so the netmap needed no edit |

**Regenerated in full:** `pcb/gen_pcb.py` → `pcb/post.py` → Gerber/drill export → `pcb/make_package.py`.
Three routing waypoints that had been hard-coded to the old pad rows now derive from the
pad positions. The "ISOLATION BARRIER" silk text moved from y 128.00 to 125.50, because the
taller footprint pushed U1's reference designator onto it.

**Verification:** DRC returns **61 items, identical in class and count to the pre-fix
board** — 0 clearance, 0 courtyard, 0 hole, 0 copper-to-edge, 0 unconnected, 0 mask
bridges; the remainder are the same silkscreen and library-footprint cosmetics as before.
Drill tools 0.450 / 0.700 / 0.800 / 1.000 / 1.200 / 2.130 / 3.200 mm, no plated slot under
0.70 mm. BOM ≡ PARTS ≡ board refs (21). Centroid 17 SMD. The board was also **rendered and
looked at**, not merely measured.

`pcb/gen_pcb.py`'s `load()` now checks a project-local `footprints/` directory before the stock
KiCad libraries, so `aF4.pretty` holds any part whose stock footprint is wrong for the part
actually being bought.

### A1.3 Isolation, re-derived `[AUDIT]`

The **"4.3 mm pad-to-pad across U1"** figure is **withdrawn** — it was the copper gap of the
OPIA403 pattern, not of the AQY212GS. The real numbers, measured off the regenerated board:

| | Value |
|---|---|
| U1 pad-to-pad copper gap | **4.80 mm** (was 4.30 on the wrong footprint) |
| Copper-free band, by design | 4.70 mm, x 121.65–126.35 |
| **True minimum logic-to-power creepage** | **4.425 mm** (was **4.225 mm** before the fix) |

The governing constraint is **not U1** — it is **R1 pad 2**, whose logic-side copper reaches
x 121.925 and intrudes 0.275 mm into the nominal band, against the GNDP pour edge at
126.350. That was true of the old board too; the footprint fix improved the real creepage by
0.2 mm. Both mounting holes inside the band are **NPTH — no copper**. Zone fills stop
exactly on the band edges. At 4.4 mm between two SELV domains, creepage is nowhere near the
weak link in the 1500 Vrms argument.

*How it got past DRC: the same mechanism as the slot widths — DRC checks pads against
tracks, not pads against the physical part. The footprint was well-formed and wrong,
which is this project's signature failure mode (§7).*

### A2. `pcb/gen_pcb.py` says `SMAJ15A` for D2; everything else says `SMAJ13A` `[AUDIT]`

The BOM, `pcb/make_package.py` and all prose specify SMAJ13A. Turn-key sources from the BOM,
so the boards would have received the 13 V part — but the "source of truth" script
contradicted the BOM. **Fixed 2026-08-28:** the script now says SMAJ13A. If a 15 V
standoff was ever the intent it was never propagated anywhere, and adopting it
deliberately would close the open-circuit-voltage question in §2.5 by fiat
(SMAJ15A breakdown 16.7–18.5 V still clamps far under the AQY212's 60 V rating).

---

### A3. J3/J4 are built on the wrong face — the fab data cannot carry a THT mounting side `[EQ]`

**Found 2026-09-11 from PCBWay's assembly sample photographs.** Both 1 × 10 sockets are
fitted on the **top** face with their openings pointing up. They belong on the **bottom**
face: plastic body hanging below the board, solder joints on the top side.

**This is our error, not PCBWay's.** They built exactly what the data said.

Three project documents already fix the socket below the board, and they agree:

| Source | What it says |
|---|---|
| §6.1 stack | `z = 4.12` top of the male header plastic, `z = 12.62` hat underside. The gap is **8.50 mm — the socket body height exactly.** With the socket on top, the hat underside would sit at 4.12 and every line below it moves |
| `docs/aF4-pcb-notes.md` | "male header plastic 2.54 mm + socket body 8.5 mm ⇒ the hat's underside sits ~11.0 mm above the ESP32's top face" |
| `docs/aF4-assembly-guide.md` §3, §5 | Male headers "pins pointing up" on the ESP32, then "**Hat down onto the two headers**". Openings must face down |
| `hardware/enclosure/af4_hat_dummy_ocp.py` | The printed fitment dummy is the fourth witness and the most literal one. The plate is `box(..., HAT_Z, ..., HAT_TOP)` = 12.618→14.218. J1, J2, U1 and the LED bumps are all fused **above** `HAT_TOP`. The two socket bars are `box(bx0, BAR_Y0, HAT_Z - SOCKET_H, bx1, BAR_Y1, HAT_Z)` = **4.118→12.618, entirely below the plate**, and peg into holes cut in its underside. Its own comment: "The bar underside is the top of the male header plastic the sockets will sit on (z = 4.118)" |

As built the Olimex pins reach ~8.5 mm above the ESP32's top face while the hat underside
sits at 12.62 mm. **They never touch** — and a socket cannot be entered from below in any case.

**Why nothing caught it.** The mounting side of a through-hole part is invisible in every
machine-readable file in the package:

1. `pcb/gen_pcb.py` places J3/J4 with the same `place(...)` call as everything else, so the
   footprints sit on `F.Cu` with silkscreen on `F.SilkS`. Nothing says "fit from the reverse".
2. `pcb/af4-trigger-hat-centroid.csv` carries **SMD rows only** — no J1, J2, J3 or J4, and no
   side column. The side was never in machine-readable data at all.
3. `pcb/PCBWay-README.txt` ASSEMBLY reads "**Sides populated: top only**". Critical note 5
   already said J3/J4 "must be seated flush and square — they mate with a header on another
   board" and stopped one sentence short of naming the face.

Gerbers encode copper, mask and silk. **They do not encode which side a leaded part is
inserted from.** For an SMD part the side is implied by the layer; for a THT part it is not
implied by anything, because the holes are identical either way.

**The rework is cheap and must be described that way to PCBWay:** same holes, same parts,
plated through with pads on both faces, so **no PCB change and no BOM change**. Pin 1 stays
in the hole it is in now — a 1 × 10 in-line connector does not mirror when flipped. The top
silkscreen legend ends up on the opposite face from the part, which is cosmetic.

> **Generalised lesson, and it is the §7 pattern in a new costume:** a fact that lives only
> in prose is a fact the factory cannot act on. **Any part fitted from the non-standard face
> must be named by designator in the fab note *and* have its footprint on that face in the
> CAD.** Do not rely on an assembly drawing, and put the THT parts in the centroid with a
> side column so the machine-readable package carries it too.

Reply text and the full photo-by-photo check: `pcb/pcbway-EQ-2026-09-11-reply.md`.

**Everything else in the sample photos was verified correct** against the BOM and the
pad-level geometry in `pcb/af4-trigger-hat.kicad_pcb`: U1 pin 1 top-left, U2 tab left,
D1 band bottom and D2 band top, C2 positive stripe right, all seven resistor codes,
J1 5 soldered slots + 1 NPTH post, J2 3 soldered slots + 5 NPTH pegs, all 21 designators
populated. **D3/D5 LED polarity is not resolvable at the photo's resolution** and was
referred back to PCBWay to confirm against the centroid.

---

### A3.1 Rework verified from photographs, and accepted with two defects open `[EQ] 2026-09-12`

PCBWay reworked one board and photographed both faces. **The A3 defect is fixed.**

⚠️ **The two photographs originally saved into `pcb/BOARD REVIEW EQ/` as `Front.jpg` and
`Back.jpg` are the REJECTED sample, not the reworked board.** They were saved on the evening of
2026-09-11, after the reply had already gone out, and the front one plainly shows both sockets
standing on the top face. **Renamed 2026-09-12** to `rejected-sample-2026-09-11-*.jpg`, with the
reworked pair alongside as `rework-2026-09-12-*.jpg` and a `README.md` in that folder saying
which is which. *Do not read the folder name as "the current board".*

**What the rework photographs show — verified 2026-09-12:**

| Check | Result |
|---|---|
| J3/J4 mounting face | ✅ Bodies on the **bottom** face, openings down, pin tails and solder on the **top** face — as §6.1 requires |
| Pin 1 | ✅ Still in the square pad on both. Not mirrored, not renumbered |
| Seating | ✅ Both flush against the board, square, parallel to each other and to the edges. **The J3 body appearing to overhang the board edge in the bottom-face photo is perspective** — the 8.50 mm body seen at an oblique angle — not lateral offset |
| Collateral damage | ✅ R1 and R2 sit within a few mm of J4 and are intact |
| Isolation band | ✅ Clean. No solder balls, and the bottom-face flux residue stops short of the upper silk line |
| J4's ten joints | ✅ Silver annulus with the gold pin end visible in each. Properly wetted |
| J3's ten joints | ⚠️ **Not gradeable.** That row is shot at too oblique an angle; the barrels read as open with the pin off-centre, which is as likely to be the camera angle as a defect |

**The two defects accepted, both carried over unfixed from the 2026-09-11 reply:**

1. **Pin 10 of each row** — the far end from the PIN 1 marker — is a dull grey irregular blob
   with burnt flux spatter and soldermask staining spreading from it. Rework heat made it
   worse. This is the same joint the earlier reply asked to be reflowed.
2. **Flux residue on the bottom face** at that same end of both sockets: heavy clear smears
   with white crystallised streaks, uncleaned.

**The decision, Kenny 2026-09-12: accept and ship, do not ask for a second rework.** The
reasoning is worth keeping because it generalises. **Five boards are being built and one
working board is needed.** Both defects are local to two joints, both are repairable at the
bench with an iron and IPA, neither propagates, and neither can worsen in transit. A second
rework round would restart the build clock — see §7's standing note on EQ cost — for cosmetic
gain on parts that will be inspected and touched up locally anyway. **Vendor goodwill spent on
a defect you can fix yourself in five minutes is goodwill you do not have for a defect you
cannot.**

Consequence for the build: **inspect all five on arrival and select the best board**, rather
than assuming board 1 is the one to fit. Reflow the two pin-10 joints and clean the flux
before the item-12 header work. Tracked as item 26.

Reply text and the accept/reject reasoning: `pcb/pcbway-EQ-2026-09-12-rework-accepted.md`.

---

### A3.2 The EQ closed and the order shipped `[EQ] 2026-09-14`

PCBWay order `YB1800644` reads **"This order was Shipped (Awaiting delivery)"** as of
2026-09-14, with the Logistics Information table giving **DHL (DTP)**, shipping time
**2026-09-14**, and the tracking-number column **blank**. That ends the A3 thread: the
acceptance reply released the rework, the remaining four boards were built, and all five left
the factory. Nothing is owed to PCBWay and nothing on this project waits on them.

**Shipped 12 days after the order was placed**, against a quoted 26–28 day lead time — and that
is *with* two engineer questions, each of which restarts the build clock (§7). The J3/J4 rework
round cost nothing against the quote. **Treat PCBWay's quoted lead time as a ceiling, not an
estimate**, and do not plan the next run's schedule around it.

⚠️ **The "Estimated Finish Time" reminder on the order page is not maintained.** It still read
`2026-09-29` on the day the boards shipped — it is the pre-EQ fabrication estimate and was never
recalculated, not by the 09-02 EQ, not by the 09-11 one, and not by the shipment. **The status
line and the Logistics Information table are the live fields; the reminder line is decoration.**
This is what item 21 was written to chase, and the answer is that there is nothing there to read.
**No delivery date is published anywhere on the order page.** DHL Express out of China typically
runs 3–6 business days to the US east coast, which puts arrival loosely in the 09-18 to 09-23
window — a working band, not a commitment, and not to be quoted as one.

**The blank tracking number is normal** within a day or two either side of a status flip.
Kenny's call on 2026-09-14 was **not to chase the waybill** and to let it appear. If it has not
by roughly 09-18, the order page is still the place to look before mailing anyone: PCBWay's
email is not a reliable signal for order events, which is why the page is the source of truth.

**DHL (DTP)** is understood to be PCBWay's duties-and-taxes-prepaid service, i.e. the $56.99 of
shipping, tax and handling taken at checkout should cover import charges and nothing should be
collected at the door. ⚠️ **Not verified against PCBWay's own published terms.** If DHL presents
a duty invoice on delivery, check it against the order before paying it rather than assuming it
is owed.

**What this changes for the build:**

- **Item 21 closes**, overtaken by events rather than answered (see above).
- **Item 26 stops being a note and becomes the next action.** The arrival inspection is now the
  top of the open-item list, ahead of items 12 and 16, all three in one bench session.
- ⚠️ **Only board 1 has ever been seen.** The other four were built after the 09-12 acceptance
  and were never photographed. They are *expected* to carry J3/J4 on the bottom face because the
  reworked sample was accepted as the pattern, but that is an inference, not an observation.
  **Check the mounting face on every board before selecting one** — the same defect that A3
  caught is exactly the one that a second build run can reproduce silently.

---

### A4. J1, the 12 V barrel jack, faces inboard on all five boards `[CAD] 2026-09-18`

The boards arrived 2026-09-18. Kenny saw it immediately: nothing can be plugged into the
12 V input. **J1 is rotated 180° from usable, on every board, and the error is in our fab
data — not in PCBWay's build.** Same family as A3: ours, not theirs. No complaint, no credit
request, no email.

**The proof, from two independent sources.** `pcb/gen_pcb.py` places J1 at rotation **270**
(`"J1", "PJ-079BH", 144.00, 121.00, 270`), which `pcb/af4-trigger-hat.kicad_pcb` carries as
`(at 144 121 -90)`. CUI's own STEP model for `BarrelJack_CUI_PJ-079BH_Horizontal` puts the
Ø5.5 receptacle bore at footprint-local **y +10.32** and the 2.5 mm centre pin on the same
axis. At rot 270 that bore maps to board **x = 133.68** — pointing at the middle of the hat.
The jack's blank back face lands at x 145.28, 0.87 mm inside the board's right edge at 146.15.

**J2 is correct, and for the same reason J1 is not.** The SJ1-3523N's bore is also at
footprint-local +y, but J2 is placed at rot **90**, which maps its nose to x 148.45 — 2.30 mm
proud of the board edge, as intended. **The two connectors needed the same handedness and were
given opposite rotations.** One number, 180° apart.

**The part cannot be re-seated.** J1's three pins sit at footprint-local x = 0, −3.2, −8.5:
gaps of 3.2 and 5.3 mm. No in-plane rotation and no bottom-side fit maps that set onto itself —
the gaps come back in the wrong order. The two shield tabs and the Ø2.13 locating boss settle
it. A PJ-079BH can go into those holes exactly one way, and that way is backwards.

**Everything else about the board is unaffected.** The pads are correctly netted — pad 1
`+12V_RAW` at (144.00, 121.00), pad 2 `GNDP` at (144.00, 112.50), pad 3 the jack's internal
switch contact, unconnected. Nothing is damaged, no other net is touched, and no other
component is placed inside J1's 11.5 × 10.1 mm body shadow.

#### The second error, in the enclosure, on the same part

`hardware/enclosure/af4_enclosure_ocp.py` carried `J1_Y = -116.56` under the comment *"jack
axes, from the vendor 3D models"*. **−116.56 is the jack's BODY centre** (footprint-local
x −4.45). The bore axis is at local x −3.19, i.e. **y −117.81**. The wall hole was therefore
**1.25 mm off axis**, against 0.95 mm of radial slack in a Ø7.4 hole for a Ø5.5 plug. **The
plug would have fouled the wall even if the jack had faced outward.** A second datum taken by
hand instead of from the part — §6.3's lesson, repeated on the very next component.

#### Why nothing caught it

Three checks looked as though they covered this. **All three were hollow**, and each one was
hollow in a different way:

| Check | Where | Why it could not fail |
|---|---|---|
| `J1 plug engagement` | `af4_enclosure_ocp.py` | Arithmetic on `J1_FACE_X = 145.28` — a hand-typed constant for the *wrong face*. It measured the assumption against itself |
| `J1 bore reaches past the wall inner face` | `af4_hat_dummy_ocp.py` | Evaluated `J1_X1 - (J1_X1 - J1_BORE_L) >= J1_BORE_L`, i.e. `9.5 >= 9.5`. Algebraically true for every input |
| `5.5 mm plug path clears the case wall bore` | `af4_hat_dummy_ocp.py` | Intersected the plug with the **case** only, never with the jack body. It tested the hole, not the jack |

The fitment dummy was built to prove the enclosure before the boards came back, and it did its
job on everything it actually tested. But it took J1's bore face from the same hand assumption
the enclosure did, so it agreed — and agreement between two models fed the same wrong number is
not verification. **§9 already says a script can only ever agree with itself; this is what that
costs when the number it agrees about is wrong.** `verify_enclosure.py`, which exists precisely
to break that circle, reads the STL and the parameters — and the parameters were the error.

→ New lesson, and it is the sharper form of §6.3's: **a check whose result is fixed by its own
inputs is not a check.** Before trusting one, ask what value of the world would make it fail.
If there is none, it is a comment.

#### The decision: use all five boards as built

Taken by Kenny, 2026-09-18, and it is better than the alternative of desoldering J1.

- **J1 stays fitted and dead** on every board. Its bore opens inboard at x 133.68, where D1 and
  C1 block it, so nothing can ever be plugged into it by mistake. Its contacts stay on
  `+12V_RAW` / `GNDP` — inert inside a closed case.
- **The 12 V feed is taken from J1's own pad tails on the hat's UNDERSIDE**, which is open air:
  board x 144 is 26 mm outboard of the ESP32's right edge (118.15), a fact `af4_enclosure_ocp.py`
  already asserts. Clear height from the floor at z −9.50 to the hat underside at 14.118, minus
  J1's 3.4 mm pin drop.
- **From there to a panel-mount jack in the +X wall**, at enclosure **y −172.50, z +6.00** —
  mid-window between the hat's near edge (−160.0) and the −Y/+X lid boss (edge −184.5), and low
  enough that the cable passes under the hat.
- **The old J1 wall penetration is gone**, Ø7.4 hole and Ø13 × 1.8 counterbore both. The wall is
  solid there, and `verify_enclosure.py` check 4 now proves it on the printed mesh.
- **A polarised 2-pin inline connector goes in the run**, near the jack. Without one the hat is
  tethered to the case and cannot be lifted off its headers for service.
- **A cable tie post** stands on the floor at (143.00, −162.50), between the jack and the hat.
  The wires land on J1's pad tails, which is the weakest joint in the repair; nothing should be
  able to pull on them.

**Identifying the two pads from the underside.** The three tails are in a row at board x 144,
and the asymmetric spacing is the key: **the wider gap is on the ground side.**

| Order, running toward J2 | Net | Board y | Gap to the next |
|---|---|---|---|
| nearest the board's own edge | `GNDP` — pad 2 | 112.50 | 5.3 mm |
| middle | the jack's switch contact — **unconnected, leave it** | 117.80 | 3.2 mm |
| nearest J2 | `+12V_RAW` — pad 1 | 121.00 | — |

Confirm with a meter before soldering: **the GND tail to TP4 is a dead short.** That pins it
unambiguously. ⚠️ **Do not try to confirm +12 V against TP1 the same way** — F1 and D1 sit
between them, so it reads a diode drop, not continuity, and a correct board looks like a fault.

#### The part: DALQUIS DC-099, already in stock `[MEAS] 2026-09-18`

Not ordered — **found in the parts drawer.** Kenny already had six, bought 2026-07-18, and
**rev C used this same part** before the hat existed (`docs/aF4-pcb-notes.md`; the rev C
enclosure had a "DC-099 hole in the input wall" that rev D deleted). 5.5 × 2.5 mm, 10 A,
threaded panel mount, **150 mm of 18 AWG pre-soldered leads — red is +12 V, black is −**,
recorded on both rev C protoboard diagrams in `archive/`. No soldering at the panel at all,
which makes it strictly better than the Same Sky PJ-005B that was the fallback.

| | | Provenance |
|---|---|---|
| Barrel, full Ø | 11.50 mm | `[MEAS]` |
| **Barrel flat**, face to opposite arc | 10.50 mm | `[MEAS]` |
| Flange thickness | 1.50 mm | `[MEAS]` |
| Nut: thickness / across flats / across corners | 3.00 / 14.00 / 15.80 mm | `[MEAS]` |
| Thread length | 9.00 mm | `[VENDOR DRAWING]` |
| Overall length | 20.00 mm | `[VENDOR DRAWING]` |
| Flange Ø, body Ø | 16.00, 13.00 mm | ⚠️ `[ASSUMED UPPER BOUND]` |

**The vendor drawing was ambiguous and the caliper resolved it.** It gives "2 mm", "9 mm",
"9 mm" and an overall "20 mm" with no indication of which are axial and which are diameters.
Two readings were coherent: 2 + 9 + 9 = 20 as consecutive axial segments, or a 2 mm flange
with 9 mm thread and body *diameters*. **A measured 11.5 mm barrel rules out the second**, so
the thread is 9 mm long — which clears the 3.0 mm wall and its 3.0 mm nut with 3.0 mm to spare.
Flange and body diameters remain uncalipered and are carried as upper bounds; both only feed
the clearance envelope, which the nut's 15.80 mm across-corners dominates anyway, and **anything
up to Ø20 still passes every check.**

#### Retention: the barrel has a flat

⚠️ **This replaced a worse design.** The script carried an opt-in pad-plus-captive-hex-pocket
scheme, written when the part was unknown, to stop the jack turning when a plug is pushed in.
**The DC-099's barrel carries a flat, so the part keys itself** — better than anything that
could have been printed around it, and it costs nothing.

The wall hole is therefore a **D, flat UP**: Ø11.90 bored, then the wall put back above a plane
4.95 mm over the axis, leaving a 1.00 mm key. Flat up also makes the hole's roof a flat bridge
instead of a curved overhang, so **unlike J2 this hole needs no teardrop crown**, and its whole
envelope stays inside Ø11.90 where any plausible flange covers it. The stack is simply flange
outside, 3.0 mm wall, nut inside.

The pad and hex-pocket code is gone, along with the now-unused `hex_x` helper. It was the right
design for an unknown part and the wrong one for this part; a hex pocket would have eaten the
wall the flange clamps.

**Fit the jack before the boards go in.** The nut is 14 mm across flats and wants a spanner or
fingers inside an otherwise empty box.

#### The wiring, as executed `2026-09-18`

Kenny soldered the DC-099's leads to J1's pad tails on the hat's underside the same day:
**red to pin 1 (`+12V_RAW`), black to pin 2 (`GNDP`), pin 3 left bare.** Re-soldered once so
the leads exit **inboard** rather than across the board's right-hand edge — see the routing
constraint below.

**The pad identification is corroborated by Same Sky's own PCB layout drawing**, which is worth
recording because it is an independent source from the footprint: the drawing gives **5.30 and
3.20** down the pin column and **6.20 and 3.60** down the shield-tab column, and our footprint
has exactly those gaps. Two consequences:

- **Pin 1 sits in the tight pair with pin 3; pin 2 is the far one.** The wide gap is the ground
  side, in both columns, on the low-y side of the board.
- The tab column gives a **second, independent read** of which way round the part is, using
  features that carry no wires. If the pin row is ever ambiguous under solder, read the tabs.

⚠️ **Polarity is not confirmed until the meter says so.** The photograph agrees and the drawing
agrees, but the deciding test is **black tail → TP4 reads a dead short**. Do not attempt the
mirror test on red against TP1: F1 and D1 sit between them, so a *correct* board reads a diode
drop and looks like a fault. A reversal is not destructive — D1 is a series Schottky and blocks
it — so the failure mode is D3 staying dark at commissioning 6.1, not damage.

#### Routing: the 0.50 mm you cannot see

🚫 **The 12 V leads must never cross the hat's right-hand edge.** `HAT_X1` is 146.15 and `IX1`
is 146.65: **0.50 mm**, and the enclosure script asserts exactly that gap. A wire laid over that
edge is crushed when the lid goes on, and the damage is invisible from outside.

Take the leads straight **down** off the pad tails into the void beneath the hat, then along the
floor to the tie post and the jack. There is room: the pads sit at board x 144, **26 mm outboard
of the ESP32's right edge**, so nothing is under them but ~20 mm of air between J1's 3.4 mm pin
drop and the case floor at z −9.50.

#### The lid does not change

✅ Verified rather than assumed, 2026-09-18: `aF4-trigger-lid.stl` is **byte-for-byte identical**
to its state at commit `29f1682`, which is what the 2026-09-17 lid was printed from — unchanged
since `5cb4b7b`, the portrait-label commit. Every change in this section is +X wall and floor
geometry. The case's external envelope is unchanged at 65.2 × 117.0 × 39.9 mm, so the existing
lid still mates. **Print the case only.**

#### Carried to rev F

- **J1 to rotation 90**, with the body re-placed so the nose overhangs the right edge. This is a
  re-layout of that corner, not a nudge: at rot 90 the pin column moves to x ≈ 135.8.
- **Both jack datums taken from the vendor STEP**, bore axis and bore face, never from a body
  outline or a typed face coordinate.
- Already carried, unchanged: J3/J4 footprints onto `B.Cu` (item 24), the hat underside kept
  clear over the Olimex cap, C1's EOL replacement, R5 to 0.25 W (item 18), J1/J2 sourcing.

---

## 1. What the system must do

Replace the inD connect WiFi dongle on an inD aquatics aF4 refrigerated frozen-food feeder
with an Olimex ESP32-POE-ISO running ESPHome, so feeds can be scheduled from Home Assistant.

The aF4 exposes a 3.5 mm "0-10 V" trigger port. It is a **threshold input, not an analog
level** — no DAC is required.

### 1.1 Requirements

| # | Requirement | Value | Source |
|---|---|---|---|
| R1 | Trigger threshold | ≥ 9 V held **≥ 15 s** | `[VENDOR] 2026-09-01` — see note |
| R2 | Re-arm | port must see ~0 V for > 60 s | `[SPEC]` — verbatim from inD's Neptune Systems page, audit-verified 2026-08-28 |
| R3 | Minimum feed spacing | ≥ 5 minutes | `[VENDOR] 2026-09-01` — Apex guide states it |
| R4 | Do not drive the port with raw 12 V | OEM dongle measured at **10.37 V** | `[MEAS] 2026-07-10` |
| R5 | Feeder must stay powered continuously | it is a refrigerator | `[SPEC]` |
| R6 | Supply | 12 V, 12.5 A external brick, barrel **5.5 × 2.5 mm centre-positive** | `[MEAS] 2026-07-10` |

### 1.2 Measured facts about the port

| Measurement | Result | Source |
|---|---|---|
| Tip↔sleeve at rest | 0 V | `[MEAS] 2026-07-10` |
| Tip↔sleeve during an OEM-triggered feed | 10.37 V | `[MEAS] 2026-07-10` |
| "Link" icon mechanism | **mechanical** — a bare plug with nothing attached lights it. Jack insertion switch, no electrical sensing | `[MEAS] 2026-07-10` |
| Consequence | no bleed resistor needed for link detect; rest voltage is genuinely 0 V | `[CALC]` |
| Tip↔sleeve resistance, unpowered | **~11 kΩ** → **~0.95 mA at 10.4 V** | `[MEAS] 2026-09-01` |
| OEM plug wiring | **TRS plug, only tip + sleeve wired. Ring floats** | `[MEAS] 2026-09-01` |
| OEM dongle output, open-circuit | 10.35 V settling to **10.37 V** — confirms R4 was an *open-circuit* figure | `[MEAS] 2026-09-01` |
| OEM dongle turn-on overshoot | **16.40 V**, brief, unloaded — boost startup overshoot | `[MEAS] 2026-09-01` |
| OEM dongle pulse behaviour | **pass-through, no fixed-width pulse** — holds until toggled off | `[MEAS] 2026-09-01` |
| 12 V brick, open-circuit | **12.13 V**, stable, centre-positive | `[MEAS] 2026-09-01` |
| 12 V rail loaded (TEC + feed) | idle **11.84–11.86 V**, minimum **11.77 V** across 3 feed cycles | `[MEAS] 2026-09-01` |
| aF4 unit under test | PN **10102101**, SN **130063** — outside every documented serial range | `[MEAS] 2026-09-01` |

### 1.3 ⚠️ `[VENDOR] 2026-09-01` inD publishes THREE different hold times

R1 previously read **`≥ 9 V held > 6 s`**. That figure is genuine: the 2026-08-28 audit
fetched inD's **Neptune Systems page** and quoted it verbatim — *"9v or higher signal for
greater than 6 seconds"*. R1–R3 were all verified against that page. **The 6 s was not
invented.**

The problem is that inD's own guides **disagree with each other**:

| inD source | Hold time |
|---|---|
| Neptune Systems 0-10 V page (fetched 2026-08-28) | **> 6 s** |
| inD Connect dongle guide (read 2026-09-01) | **≥ 10 s** |
| Coralvue Hydros guide (read 2026-09-01), `Run Time 00:00:15` | **≥ 15 s** |

The current Neptune **Apex** article no longer states a hold time at all, so the help
centre appears to have been reorganised since August.

**Design to the longest published figure.** R1 is therefore set to **≥ 15 s**. The old 10 s
firmware pulse satisfied the 6 s figure but **failed the 15 s one**, so the timing check's
"67 % margin" was margin against only the most permissive of three numbers.
✅ **Fixed in the repo 2026-09-01: 20 s pulse, tail left at 290 s** — a 310 s cycle, which
clears all three hold times *and* closes the separate zero-margin-at-300 s audit item. The
280 s tail first sketched here would have kept the cycle at exactly 300 s; keeping the
290 s was free. **Still needs flashing** — open item 11.

`[MEAS] 2026-09-01` closes the obvious escape route: the OEM dongle **passes the toggle
through** rather than emitting a fixed-width pulse, so inD's "10 seconds" describes the
**port**, not dongle logic.

**Key design insight:** R1 defines a *window*, not a setpoint. 10.37 V is merely what the
OEM dongle happens to produce. This is why a fixed resistor divider is the right answer and
a trimpot is not.

⚠️ `[AUDIT]` **The upper end of that window is an inference, not a spec.** inD's guide
states a 9 V floor and **no maximum voltage**; the "below 12 V" ceiling is this project's
own reading of the 10.37 V OEM measurement. The worst-case output of 10.88 V (§2.1) already
exceeds what the OEM dongle produces by half a volt. Almost certainly fine for a threshold
input — but that ceiling should carry an `[ASSERT]` tag, and until now it read as `[SPEC]`.

### 1.4 ✅ `[VENDOR] 2026-09-01` RESOLVED — and the assumption was backwards

This document previously asked whether the internal 24 h timer keeps running under
external triggering, and **assumed yes**. Both inD's Neptune Apex and Coralvue Hydros
guides state the built-in schedule is **completely overridden when the link port is
connected** — Hydros words it as *connection*, not signalling.

**So once J2's cable is plugged in the aF4 never feeds on its own.** An offline ESP32,
a mid-OTA reboot, or `input_boolean.reef_af4_schedule_enabled` left OFF means the fish
are **silently not fed**.

Every guardrail in this design prevents an *extra* feed. This is the opposite direction.

⚠️ **Corrected 2026-09-05.** This paragraph previously read "has **no detection at all**"
and proposed alerting when `counter.reef_af4_feeds_today` is still 0 past the scheduled
time, citing "open item 12". Both were wrong, and the wrongness is the point: **that alert
already existed** when this was written — `automation.reef_tank_feeder_health_watchdog` has
run a 23:45 counter-vs-elapsed-feed-times backstop and a board-offline branch since
2026-08-27 (§5.7). It was opened as **item 17** — not item 12, which is the headers — and
**withdrawn the same day**. See §7.1.

**What is actually detected:** an offline board (watchdog, 15 min), a missed scheduled feed
(watchdog, 23:45), and a skipped or unacknowledged press (the scheduled-feed automation).
**What is not:** whether food physically came out — §8 item 20, the one real remaining gap.
An over-temperature fault stops the feeder, never self-clears, and is invisible to every
mechanism above.

---

## 2. Circuit

```
 feeder 12 V brick
   │
   └─ barrel Y-splitter ──→ J1 (PJ-079BH, 5.5 × 2.5)
                             │
                             └─ F1 PPTC 0.10 A hold ──→ +12V_F
                                                          │
                                     D1 SS14 (reverse polarity, in series)
                                                          │
                            ┌───────────────┬─────────────┴──→ +12V
                            │               │
                     D2 SMAJ13A        C1 10 µF          U2 LM1117MPX-ADJ
                       (clamp)          ceramic          R4 121 Ω  OUT→ADJ
                            │               │            R5 887 Ω  ADJ→GND
                           GND             GND                    │
                                                                  │
   +10V4 rail ────┬──────────────┬─────────────────────────────────┘
                  │              │
            C2 10 µF        R6 1.0 k
            tantalum         D3 green      U1 AQY212GS PhotoMOS (pins 3/4)
                                                          │
   TIP ───┬───────────────┬──────────────┬────────────────┘
          │               │              │
     R3 100 k        R7 6.8 k        D4 SMBJ13CA      J2 (SJ1-3523N) tip
      bleed           D5 yellow       (bidir)
          │
         GND

 ESP32-POE-ISO ── GPIO32 ─┬─ R1 220 Ω ── U1 LED anode  (pin 1)
                          │
                          └─ R2 10 k ── GND
                             U1 LED cathode (pin 2) ── logic GND
```

The PhotoMOS is the **only** thing crossing between the logic domain and the feeder-power
domain. Separate ground pours, no copper bridging.

> `[AUDIT]` The chain is **series**: J1 → F1 → D1 → then D2, C1 and the LDO all
> *downstream* of the Schottky. An earlier draft of this diagram showed D2 clamping
> `+12V_RAW` upstream of D1, which is not what `pcb/gen_pcb.py` builds. The built topology is
> the better one — D2 never sees a reverse input, and F1 still protects a shorted D2 —
> but the diagram was wrong, and an auditor working from it would have signed off on a
> circuit that was never built. The pad-to-pad figure that used to appear here is
> withdrawn; see §A1.

### 2.1 Regulator — the calculation that matters

`[DS]` TI SNOS412Q, LM1117-ADJ:

| Parameter | Value |
|---|---|
| V_REF (OUT→ADJ) | 1.25 V typ; 1.238–1.262 V @ 25 °C; 1.225–1.27 V over 0–125 °C |
| I_ADJ | 60 µA typ, 120 µA max |
| Minimum load current | 1.7 mA @ 25 °C, **5 mA over full temperature range** |
| Output capacitor | ≥ 10 µF, **ESR 0.3 Ω to 22 Ω**, tantalum named explicitly |
| Dropout @ 800 mA | 1.2 V @ 25 °C, 1.3 V over temp |

`[CALC]` with R4 = 121 Ω (OUT→ADJ), R5 = 887 Ω (ADJ→GND):

```
V_OUT = V_REF × (1 + R5/R4) + I_ADJ × R5
      = 1.25 × (1 + 887/121)   + 60 µA × 887
      = 1.25 × 8.3306          + 0.0532
      = 10.413 + 0.053         = 10.47 V   (nominal)
```

Worst-case stack (V_REF at its 0–125 °C limits, both resistors at ±1 %, I_ADJ 60–120 µA):

```
  low   1.225 × (1 + 7.3306×0.9803) + 0.053  ≈  10.08 V
  high  1.270 × (1 + 7.3306×1.0202) + 0.107  ≈  10.88 V
```

**Both extremes satisfy R1 (≥ 9 V) with wide margin and stay well under 12 V.** The design is
robust precisely because the requirement is a window. ⚠️ Note the upper bound of 10.88 V
brushes the top of the "~9.5–11 V is correct" band stated in `docs/aF4-reference.md`; it is still
inside it, but there is less headroom above than the round number 10.4 V suggests.

### 2.2 Load on the 10.4 V rail

`[CALC]`, using V_OUT = 10.47 V and datasheet LED forward voltages:

| Branch | Expression | Current |
|---|---|---|
| R4 + R5 divider | 10.47 / 1008 Ω | **10.39 mA** |
| D3 green via R6 | (10.47 − 2.2) / 1000 Ω | **8.27 mA** |
| **Quiescent total** | | **18.7 mA** |
| R3 bleed (only while asserted) | 10.47 / 100 kΩ | 0.10 mA |
| D5 yellow via R7 (only while asserted) | (10.47 − 2.0) / 6800 Ω | 1.25 mA |
| **Total during a feed** | | **20.0 mA** |

Consequences:

- **Minimum load is satisfied by the divider alone** (10.39 mA vs the 5 mA requirement).
  D3's branch is a bonus, not load-bearing. Earlier project notes implied D3 carried this;
  it does not, and it must not be relied on. `[AUDIT]` Strictly the current *through R4* is
  V_REF/R4 = 10.33 mA (10.02 mA at worst-case tolerance) rather than V_OUT/1008 — same
  conclusion against the 5 mA floor, slightly different physics, and worth stating because
  this branch **is** the minimum-load guarantee.
- **`[AUDIT]` R5 is the hottest passive on the board.** It drops 9.22 V at 10.39 mA =
  **~96 mW against an 0805's 125 mW rating — 77 %**. Acceptable at enclosure temperatures,
  but it has no margin for a hot day and this document did not previously mention it. A
  0.25 W-rated 0805 is a drop-in if the margin is wanted. Note that **raising the divider
  impedance is not available** — the divider is the minimum-load ballast.
- **F1 margin:** 20 mA against a 0.10 A hold current — 5× margin `[DS]`.
- **U2 dissipation:** with the SS14 dropping ~0.35 V, U2 sees ~11.65 V in, so
  (11.65 − 10.47) × 18.7 mA ≈ **22 mW**. No thermal concern. ⚠️ The 0.35 V Schottky drop
  at ~20 mA is an estimate, not read off the SS14 forward-voltage curve. `[ASSERT]`
- **Headroom — `[AUDIT]` the earlier reasoning here was wrong.** This document previously
  argued "1.2 V dropout is specified at 800 mA, so at 20 mA it is far smaller." That is
  true of a PMOS LDO and **false of the LM1117**, which is a quasi-LDO with an NPN pass
  device: its dropout is a V_BE stack and the dropout-vs-current curve is nearly **flat at
  ~1 V**. Redone honestly, with the SS14 at ~0.3 V:

  | Brick | LDO input | Headroom to 10.47 V | Headroom to worst-case 10.88 V |
  |---|---|---|---|
  | 12.2 V | 11.90 V | 1.43 V ✓ | 1.02 V — at the edge |
  | 12.0 V | 11.70 V | 1.23 V ✓ | 0.82 V — **in dropout** |
  | 11.6 V | 11.30 V | 0.83 V — **in dropout** | 0.42 V — deep in dropout |

  **This is not a safety problem.** In dropout the LM1117 degrades gracefully to
  V_IN − ~1 V ≈ 10.3–10.7 V, still inside the 9–11 V window, so the feeder still triggers.
  What is lost is regulation and ripple rejection, not function. But two consequences
  follow: a board whose divider stacks toward the high end rides dropout on a nominal
  12 V brick; and **commissioning checks 6.2 and 6.3 are mutually inconsistent at their
  edges** — a brick legitimately passing 6.2 at 11.6 V cannot deliver 10.3 V at TP2 even
  with perfect parts. If 6.3 reads low after a low-but-passing 6.2, the divider is
  probably innocent.

### 2.3 PhotoMOS drive

`[DS]` Panasonic AQY212GS:

| Parameter | Value |
|---|---|
| LED forward voltage | 1.32 V typ, 1.5 V max |
| Recommended LED current | 5 mA min, 30 mA max |
| Load rating | 60 V, 1.0 A continuous |
| On-resistance | 0.34 Ω typ, 0.7 Ω max |
| Turn-on / turn-off | 1.3 ms typ (5 ms max) / 0.1 ms typ (0.5 ms max) |
| Isolation | 1500 Vrms |

`[CALC]` with R1 = 220 Ω from GPIO32:

```
  nominal    (3.3 − 1.32) / 220 = 9.0 mA
  worst case (3.0 − 1.5)  / 220 = 6.8 mA
```

Both inside the recommended 5–30 mA band, with 36 % margin at worst case. ESP32 GPIO source
current of 9 mA is well within its ~20 mA recommended / 40 mA absolute limit.

Switching time (1.3 ms typ) is irrelevant against a 20 s pulse.

### 2.4 The GPIO13 problem — why the trigger is on GPIO32

`[CAD]` The Olimex board has **R35, a factory 2.2 kΩ pull-up to +3.3 V on GPIO13** (the I²C
SDA pull-up), confirmed in the Rev N KiCad source. Not optional, not removable without rework.

During reset and early boot GPIO13 is high-impedance. `[CALC]` solving the node — 3.3 V through
2.2 kΩ, into R2 (10 kΩ to GND) in parallel with the R1 + LED branch:

```
  node settles ≈ 1.4 V
    in  via pull-up   (3.3 − 1.4)/2200  = 0.86 mA
    out via R2         1.4/10000        = 0.14 mA
    out via R1 + LED  (1.4 − ~1.25)/220 ≈ 0.68 mA   ← into the PhotoMOS LED
```

0.68 mA against an AQY212 operate current of ~1.1 mA typical is **62 % of the way to a
spurious feed**, before any firmware runs. `restore_mode: ALWAYS_OFF` cannot help — the pin
is high-Z before firmware exists. The failure mode is "10.4 V on the trigger port for more
than 6 seconds = an unscheduled feed into a reef tank."

> **`[AUDIT]` RESOLVED — and the truth is worse than the paragraph above.** Panasonic's
> published spec `[DS]`:
>
> | Parameter | Value |
> |---|---|
> | LED operate current | **1.1 mA typ, 3 mA max** |
> | LED **turn-off** current | **0.3 mA min**, 1.0 mA typ |
> | Recommended LED operating range | 5–30 mA |
>
> The ~1.1 mA figure was right. But the number that actually governs is the one this
> document never cited: **the guaranteed-off threshold is 0.3 mA**, and there is no
> minimum operate current — below 1.1 mA the datasheet simply stops promising the relay
> stays open. Re-solving the boot node with a realistic sub-milliamp LED V_F of
> 1.0–1.25 V gives **0.72–0.85 mA**, higher than the 0.68 mA above and **more than 2× the
> guaranteed-off current**.
>
> "62 % of the way to a spurious feed" understated it. On GPIO13, nothing guaranteed the
> feed *wouldn't* happen. Moving to GPIO32 was not cheap insurance — it was mandatory.

`[CAD]` **GPIO32** touches only the ESP32 module and EXT2 pin 6 — no pull-up, no strapping
function, not shared with UEXT. GPIO33 is nearly as clean (one unpopulated resistor).

### 2.5 Protection

| Ref | Part | Function | Notes |
|---|---|---|---|
| D1 | SS14 Schottky 40 V / 1 A | Reverse polarity, in series with +12 V | New in rev D; rev C had **none**. Costs ~0.35 V of headroom |
| D2 | SMAJ13A, 400 W unidirectional | Input transient clamp | 13 V standoff, 21.5 V clamping `[DIST]` |
| D4 | SMBJ13CA, 600 W bidirectional | Clamp across the trigger pair at J2 | 13 V standoff, breakdown 14.4–15.9 V `[DIST]`. No orientation |
| F1 | 1206L010/60WR PPTC | Overcurrent on the 12 V tap | 0.10 A hold / **0.25 A trip** / 60 Vdc, −40…+85 °C `[DS]` |
| R3 | 100 kΩ bleed | Guarantees the 0 V re-arm (R2 above) | 0.10 mA |

✅ **CLOSED `[MEAS] 2026-09-01`.** Both TVS parts have a 13 V standoff on a nominally
12 V rail. The brick measures **12.13 V open-circuit, stable** — comfortably below the
standoff, so D2 never conducts at idle and no part change is needed.

Loaded, the rail sits at **11.84–11.86 V** and dips to **11.77 V** during a feed, so the
standoff is even further away in service. Separately, the port itself tolerates the OEM
dongle's **16.40 V** turn-on overshoot on every feed, which makes the worst-case 10.88 V
output look tame.

**Deliberately absent:** a series resistor on the trigger tip. At 10.4 V into a short it
would sit right at the polyfuse hold current and cook rather than trip. The LDO's internal
current limit plus F1 handle a shorted tip properly. `[CALC]`

### 2.6 Indicator LEDs

`[DS]` Both are Kingbright 0805, both **water clear**:

| Ref | Part | Intensity @ 20 mA | V_F | λ | Angle |
|---|---|---|---|---|---|
| D3 green | APT2012SGC | 12 mcd typ, **5 mcd min** | 2.2 V typ, 2.5 max | 565 nm | 160° ⚠️ |
| D5 yellow | APT2012SYCK | 150 mcd typ, 80 mcd min | 2.0 V typ, 2.5 max | 590 nm | 140° ⚠️ |

⚠️ `[AUDIT]` **Unresolved conflict on viewing angle.** The figures above are read off the
Kingbright datasheet PDFs; the audit found 120° for both from two distributor-datasheet
sources. Neither resistor value depends on it — it changes only how wide the cone through
the lid sight holes is. Settle it against the current Kingbright drawing if it matters.

The two parts differ **~12× in efficiency**. `[CALC]` scaling intensity linearly with current:

| | Current | Intensity (typ) | Intensity (worst case) |
|---|---|---|---|
| D3 via R6 = 1.0 kΩ | 8.27 mA | ~5.0 mcd | ~2.1 mcd |
| D5 via R7 = 6.8 kΩ | 1.25 mA | ~9.3 mcd | ~5.0 mcd |

Reasonably matched to the eye. ⚠️ Linear intensity-vs-current scaling is an approximation
`[ASSERT]`; real LEDs are sub-linear at high current and roughly linear at low, so these
figures are fair-to-slightly-optimistic at the low end.

Both are viewed through **Ø3.5 mm sight holes in the lid**, which is why absolute brightness
matters here at all.

> **This was a defect, caught 2026-08-28.** R6 and R7 originally shared a single 10 kΩ value,
> giving 0.82 mA and putting D3 at ~0.5 mcd — effectively invisible. Root cause: 10 kΩ was
> chosen as a jellybean value without checking it against the LEDs' actual intensity specs.

---

## 3. Bill of materials — with verification status

Board BOM: **20 lines, 21 placements** (17 SMD + 4 THT / 28 joints). Every manufacturer part
number below was confirmed against a live distributor listing on 2026-08-28, and independently
re-confirmed by the audit the same day.

| # | Ref | MPN | Description | Status |
|---|---|---|---|---|
| 1 | U1 | Panasonic **AQY212GS** | PhotoMOS SSR, SOP-4, 60 V / 1 A, 1500 Vrms | `[DIST]` ✓ |
| 2 | U2 | TI **LM1117MPX-ADJ/NOPB** | LDO, SOT-223, adjustable, 800 mA | `[DIST]` ✓ |
| 3 | D1 | Vishay **SS14-E3/61T** | Schottky 40 V / 1 A, SMA | `[DIST]` ✓ |
| 4 | D2 | Littelfuse **SMAJ13A** | TVS 400 W unidirectional, SMA | `[DIST]` ✓ |
| 5 | D4 | Littelfuse **SMBJ13CA** | TVS 600 W bidirectional, SMB | `[DIST]` ✓ |
| 6 | D3 | Kingbright **APT2012SGC** | LED green 565 nm, 0805 | `[DIST]` ✓ |
| 7 | D5 | Kingbright **APT2012SYCK** | LED yellow 590 nm, 0805 | `[DIST]` ✓ **corrected** |
| 8 | F1 | Littelfuse **1206L010/60WR** | PPTC 0.10 A / 0.25 A / 60 V, 1206 | `[DIST]` ✓ **corrected** |
| 9 | C1 | Murata **GRM31CR61H106KA12L** | 10 µF 50 V **X5R** 1206 | ⚠️ `[AUDIT]` **EOL at Murata (2020)**, but DigiKey ships today and distributor float is ~1.6 M. Fine for 5 boards; expect PCBWay to flag it. Line up a current-production substitute from a **live parametric search**, never from memory |
| 10 | C2 | Kemet **T491B106K025AT** | 10 µF 25 V tantalum, EIA-3528 B, ESR ~2 Ω | `[DIST]` ✓ |
| 11 | R1 | Yageo **RC0805FR-07220RL** | 220 Ω 1 % | `[DIST]` ✓ |
| 12 | R2 | Yageo **RC0805FR-0710KL** | 10 kΩ 1 % | `[DIST]` ✓ |
| 13 | R3 | Yageo **RC0805FR-07100KL** | 100 kΩ 1 % | `[DIST]` ✓ |
| 14 | R4 | Yageo **RC0805FR-07121RL** | 121 Ω 1 % | `[DIST]` ✓ |
| 15 | R5 | Yageo **RC0805FR-07887RL** | 887 Ω 1 % | `[DIST]` ✓ |
| 16 | R6 | Yageo **RC0805FR-071KL** | 1.0 kΩ 1 % | `[DIST]` ✓ **new** |
| 17 | R7 | Yageo **RC0805FR-076K8L** | 6.8 kΩ 1 % | `[DIST]` ✓ **new** |
| 18 | J1 | Same Sky **PJ-079BH** | DC jack 5.5 × 2.5, 2.5 mm centre pin, 24 V / 5 A | `[DIST]` ✓ |
| 19 | J2 | Same Sky **SJ1-3523N** | 3.5 mm jack, 3-conductor, right angle | `[DIST]` ✓ |
| 20 | J3, J4 | Sullins **PPTC101LFBN-RC** ×2 | 1×10 socket, 2.54 mm | `[DIST]` ✓ |

### 3.1 Sourcing traps recorded

- **J1:** `PJ-002AH` / `PJ-102AH` look identical but are 2.0–2.1 mm centre pin. Only the
  **"B" suffix** parts are 2.5 mm. The same trap applies to the 12 V splitter cable.
- **C2 must stay tantalum.** The LM1117 requires output-cap ESR between 0.3 Ω and 22 Ω `[DS]`.
  A low-ESR ceramic substitution risks loop instability.
- **C1 is X5R, not X7R.** Murata makes no 10 µF 50 V X7R in 1206; that C/V needs a 1210.

### 3.2 Bought separately (not on the board)

Olimex ESP32-POE-ISO (~$28–35) · 2× 1×10 male headers for EXT1/EXT2 (ship unpopulated) ·
12 V barrel Y-splitter 5.5 × 2.5 centre-positive · 3.5 mm male–male patch cable ·
PETG for the enclosure · M2 / M3 self-tapping screws.

---

## 4. Board

| Property | Value |
|---|---|
| Size | 57.00 × 50.00 mm, rectangular |
| Layers / thickness / copper | 2 / 1.6 mm / 1 oz |
| Finish | ENIG preferred, HASL acceptable |
| Min track / space | 0.35 mm / 0.20 mm |
| Min drill | 0.45 mm (stitching vias) |
| Plated slots | **0.70 mm minimum**, deliberately widened |
| Placements | 17 SMD (top face) + 4 THT parts / **28** joints `[AUDIT]` |
| THT mounting side | J1, J2 bodies on the **top** face. **J3, J4 bodies on the BOTTOM face**, soldered on top — see §A3. The fab data does not express this; it must be stated by designator in the fab note |
| Mounting | 2 × M3 at (123.0, 118.0) and (123.5, 147.0), board frame |

`pcb/gen_pcb.py` is the source of truth — it generates the `.kicad_pcb` deterministically from
named coordinates taken from the Olimex Rev N source `[CAD]`, so socket alignment is exact by
construction. **Edit the script, not the board file.**

### 4.1 Geometry from vendor CAD `[CAD]`

| Feature | Position (Olimex board frame) |
|---|---|
| ESP32-POE-ISO outline | x 90.15–118.15, y 90.00–188.15 (28.00 × 98.15 mm) |
| EXT1 pin 1 | (91.44, 123.22), 2.54 mm pitch |
| EXT2 pin 1 | (116.84, 123.22), 2.54 mm pitch |
| GND | EXT1 pin 3 → (91.44, 128.30) |
| GPIO32 | EXT2 pin 6 → (116.84, 135.92) |

### 4.2 Verification status of the board

✅ **Independently re-run 2026-08-31** (`archive/reviews/aF4-prefab-review-2026-08-31.md`), on KiCad
7.0.11 with the zones filled from scratch — the counts below are confirmed, not reported.
DRC via `pcbnew.WriteDRCReport` (KiCad 7): clearance 0, courtyard
overlaps 0, hole clearance 0, hole-to-hole 0, copper-to-edge 0, unconnected 0, mask bridges 0.
That review also swept clearance at multiple rules on the filled board: **zero violations at
0.2032 mm (8 mil) and at 0.24 mm; first hits at 0.25 mm**, so the real minimum copper gap is
0.24–0.25 mm and the 0.20 mm carried in these docs is the KiCad netclass default, not the
geometry. The shipped Gerbers were re-exported and diffed against the board — identical.
Remaining flags are silkscreen cosmetics and "library footprint differs", both expected for
programmatically placed footprints.

**A defect DRC does not catch, found by inspecting the drill file:** KiCad's SJ1-3523N
footprint specifies 0.40 mm plated slots and PJ-079BH 0.60 mm — both below fab routing
minimum (~0.5 mm drilled / 1.0 mm milled). `pcb/gen_pcb.py` now enforces `MIN_SLOT = 0.70 mm` and
prints what it widened. Worst-case annular ring after widening is 0.25 mm.

> **Generalised lesson:** DRC checks what it was told to check. Slot widths, and any
> hand-written count in a generated document, are outside it. Inspect the drill tool list
> before any package leaves the building.

### 4.3 Isolation

Two separate ground pours with **no copper crossing**. The only connection is U1 itself,
straddling the boundary; its pad-to-pad gap is **4.80 mm**. The band is marked on both
silkscreens, and the two mounting holes sit inside it — both **NPTH, no copper**.

`[AUDIT]` The **true minimum logic-to-power creepage is 4.425 mm**, and it is not set by U1:
**R1 pad 2** reaches x 121.925, 0.275 mm inside the nominal band, against the GNDP pour edge
at 126.350. Measured off the regenerated board. The earlier "4.3 mm" figure was an artefact
of the wrong U1 footprint and is withdrawn (§A1).

⚠️ **Assembler instruction that must survive:** no copper, vias or stitching in that band.

### 4.4 The ordered board re-checked on KiCad 9.0.7 `[MEAS] 2026-09-17`

Kenny asked whether a board made with KiCad 7-era tools holds up under current ones. Everything
below ran on the Mac against **copies** in the session scratchpad; nothing in `pcb/` was
regenerated or rewritten. It is a check of what was ordered, not a change — rev E is spent.

**What was checked against what.** The uploaded package is `pcb/af4-trigger-hat-rev-E-GERBERS.zip`
(`pcb/pcbway-order-YB1800644.md`). Its eleven fab files are byte-identical to `pcb/gerbers/`.
The committed `.kicad_pcb` (file format 20221018, KiCad 7) loads in KiCad 9 without complaint.

| Check | KiCad 9.0.7 result |
|---|---|
| DRC, zones as shipped | **0 errors, 0 unconnected.** 33 warnings, all silkscreen: 16 silk overlap, 8 silk-to-edge, 7 silk over copper, 2 text height — the same 33 as the KiCad 7 `pcb/drc.rpt` |
| The KiCad 7 report's other 28 | `lib_footprint_issues` — not raised under `kicad-cli` with no footprint library table. Expected for generated footprints, not a finding |
| Zones refilled by KiCad 9's filler | GNDP 633.844 → 633.876 mm², GNDL 1467.197 → 1467.252 mm², same island counts. DRC after refill identical |
| Clearance sweep, custom rules | **0 at 0.24 mm, 1 at 0.25 mm** — minimum copper gap **0.245 mm**, GPIO32 track to J3 pad 4. Matches §4.2 exactly |
| Isolation, logic nets (GNDL, GPIO32, LED_A) to power copper | **4.425 mm clearance and 4.425 mm creepage** (KiCad 9's creepage constraint), set by R1 pad 2 to the GNDP pour edge at x 126.35, confirmed from pad geometry. GNDL pour to GNDP pour 4.70 mm. Matches §4.3 |
| Netlist read back from the board | Matches §2 net for net: F1 → D1 → +12V; D2 TVS +12V–GNDP; U2 pin 1 ADJ, pin 2 + tab 10V4, pin 3 12V; R4 121 Ω / R5 887 Ω; U1 pins 1/2 LED_A/GNDL, 3/4 TIP/+10V4; R2 GPIO32–GNDL; J3.3 = GNDL, J4.6 = GPIO32; D3/D5 pad 1 on GNDP |
| KiCad 9 Gerber export vs the shipped Gerbers | **Pixel-identical on all nine layers** (both coppers, masks, pastes, silks, edge), rasterised at 0.025 mm. Control: the same comparison against KiCad 9-*refilled* copper shows 2,000+ differing pixels, so the method sees sub-0.05 mm pour changes |
| KiCad 9 drill export vs the shipped `.drl` | **Identical**: the same 7 tools (0.45–3.20 mm), the same 47 hits and slots, narrowest slot 0.70 mm (§4.2) |

**Conclusion:** the tool generation changed nothing that reached the fab. The ordered board is the
board the §4.2 audit verified.

**A KiCad 9 report quirk, not a board fault:** the isolation rule reported its 4.425 mm pair as
"Pad 2 [PWRLED] of R6". R6 sits at x 135–137, on the power side; the pad geometry puts the real
pair at R1 pad 2. Read positions from a KiCad 9 DRC item before trusting its item label.

**What this does not cover:** the J3/J4 mounting face (item 24 — the file is wrong, the rework
fixed the parts), the "10s pulse" silkscreen (item 19), D3/D5 physical polarity (item 25), and
assembly quality on the four unphotographed boards (item 26). None is a tool question. Board-level
DRC also cannot catch the enclosure-side cap collision; that is §6.3's job.

---

## 5. Firmware

`firmware/af4-feeder.yaml` in the repo is the source of truth. The ESPHome Device Builder (Docker on
the Unraid server, port 6052) holds its own copy — changes must be pasted there manually,
then Install → Wirelessly.

### 5.1 The safety architecture

All feeder timing rules are enforced **on-device**. Home Assistant is scheduler only — it
presses one button and can do nothing else.

| Mechanism | Purpose |
|---|---|
| `switch.feed_ssr` is `internal: true` | HA cannot reach the raw GPIO line at all |
| `restore_mode: ALWAYS_OFF` | software half of the boot-safety pair |
| R2 10 kΩ pulldown on GPIO32 | hardware half — **unopposed** on GPIO32, which is the point |
| `script.do_feed` with `mode: single` | re-entrant presses are **dropped**, not queued |
| `button.af4_feed` template button | the sole exposed control |
| `binary_sensor.af4_lockout` | exposes lockout state for dashboards and automation conditions |
| `globals.feed_in_flight`, `restore_value: yes` | **flash-persisted**, so a reboot inside a cycle is detected on boot |
| `script.boot_recovery` off `on_boot` | serves a 300 s lockout when that flag comes back true |
| `web_server: auth:` | the local control page is no longer an anonymous second control path |

### 5.2 Timing check against the spec `[CALC]`

```
  20 s pulse    ≥ 15 s threshold hold      ✓  (33 % margin)   <-- live on the device
 290 s off tail ≥ 60 s re-arm              ✓  (383 % margin)
 20 + 290 = 310 s total cycle ≥ 5 min      ✓  (10 s of margin, was exactly 0)
```

✅ **RESOLVED AND FLASHED 2026-09-01.** Two separate problems were
closed in one edit. The old block read `≥ 6 s` and claimed a 67 % margin; against inD's
actual figures the 10 s pulse had none, so the pulse went to **20 s**. And the audit's
zero-margin complaint — R3 requires feeds ≥ 5 min apart and the cycle was exactly 300 s —
was closed by keeping the **290 s tail** rather than trimming it to 280 s, which buys the
310 s cycle for free.

Everything in this section describes the firmware **as actually running**: the device
reports its build as 2026-09-01 18:54:20, and the last YAML commit that evening was
18:51:33. It was installed three minutes after it was written. A second install on
2026-09-02 18:15:49 carried the rotated credentials and nothing else.

### 5.3 ✅ `[AUDIT]` The lockout did not survive a reboot — CLOSED 2026-09-01

`script.do_feed`'s state lives in RAM. Any reboot inside the 300 s cycle — OTA update,
crash, brownout, power blip — clears the lockout silently. The switch comes back
`ALWAYS_OFF`, so the pin is safe, but `binary_sensor.af4_lockout` reads `off` and the
device accepts a new press immediately.

A sequence that ends with two feeds ~2 minutes apart into the tank: scheduled feed fires →
OTA or crash at t+60 s → HA retry, second schedule slot, or a manual press → second feed.
Low probability, but it is exactly the class of unattended edge this document exists to
catch.

**Fix, implemented:** a `restore_value: yes` global, `feed_in_flight`, is set when the
pulse starts and cleared when the lockout ends. It lives in flash, so a reboot mid-cycle is
detected in `on_boot`, which runs `script.boot_recovery` — a 300 s lockout-only script. The
Feed button checks `boot_recovery.is_running()` and ignores presses while it is, and
`binary_sensor.af4_lockout` ORs both scripts so the state is visible. A clean boot leaves
the flag false and costs nothing.

⚠️ One practical wrinkle, verified 2026-09-01: the `on_boot` log line fires while ethernet
is still coming up, so **no log client ever sees it** and ESPHome does not replay it. Read
the *state* instead — Feed Lockout on at a low uptime with nobody having pressed Feed is
the recovery lockout. `docs/aF4-assembly-guide.md` §6 says so at the point of use.

### 5.4 ✅ `[AUDIT]` The web server was a second, unauthenticated control path — CLOSED 2026-09-01

`web_server: port: 80` exposes the Feed button to anything on the LAN, with no `auth:`
block. The safety story above — "HA is scheduler only, it presses one button and can do
nothing else" — is true of Home Assistant and **false of the network**. On a home LAN this
was a judgment call rather than a defect, but the document should have said so.

`web_server:` now carries an `auth:` block. Commissioning step 6.5 uses this page, so the
assembly guide records the credential at the point of use; Home Assistant is unaffected
because it talks over the API, not this page.

### 5.5 ✅ The related hygiene problem — the worse one — CLOSED 2026-09-02

The API encryption key, the OTA password **and the new web_server password** were all
committed in plaintext to a **public** GitHub repository. Adding web auth and publishing
its password in the same commit closed nothing; it moved the hole from the LAN to the
internet.

All three now resolve through `!secret` against a gitignored `firmware/secrets.yaml`, **and all
three were rotated** — which is the part that actually remediates it, because git history
keeps the old values whatever the working tree says. History was deliberately *not*
rewritten: rotation makes the exposed values worthless, and a filter-repo pass would
rewrite all 46 commit SHAs while GitHub can still serve cached objects. Decided 2026-09-02.

Two operational consequences, both recorded at the point of use in
`docs/aF4-assembly-guide.md` §4: the ESPHome Device Builder needs **its own copy** of
`firmware/secrets.yaml`, and the first install after the rotation authenticates with the **old**
OTA password while installing the new one.

### 5.6 `[AUDIT]` Held-high failure modes are bounded — the design's best safety property

Checked deliberately, since "unscheduled feed" is the nightmare. If the ESP32 crashes with
the SSR on, or the PhotoMOS fails shorted, the port sees a **continuously held** 10.4 V.
Per R2, re-arming requires ~0 V for more than 60 s — so a held-high line produces **at most
one feed and then never re-arms**.

Every stuck-at fault therefore costs one feed, not a feeding loop. This is the single best
safety property the design has, and it emerges from the feeder's own spec rather than from
anything on the board.

### 5.7 Home Assistant integration

Entities — **seven**, re-read from HA 2026-09-18: `button.af4_feeder_feed` (sole control),
`button.af4_feeder_restart`, `binary_sensor.af4_feeder_feed_lockout`,
`binary_sensor.af4_feeder_status`, `sensor.af4_feeder_ip_address`, `sensor.af4_feeder_uptime`,
`sensor.af4_feeder_esphome_version`. ⚠️ This list said six until 2026-09-18; the version
sensor was always there and was simply never written down.

Helpers: `input_boolean.reef_af4_schedule_enabled` (master kill switch),
`input_datetime.reef_af4_feed_time_1` … `_6`, `input_number.reef_af4_feeds_per_day`,
`counter.reef_af4_feeds_today`, `sensor.reef_af4_next_feed`.

Consumers of the aF4 entities — **four, plus a dashboard**, re-read 2026-09-18:
`automation.reef_tank_af4_scheduled_feed` (scheduler + per-feed confirmation),
`automation.reef_tank_feeder_health_watchdog` (backstop, shared with the Plank feeder),
`automation.reef_circulation_pause_powerheads_for_feeding` (triggers on the lockout edge —
**not previously recorded here**), `automation.reef_tank_reset_ato_counter_daily` (nightly
counter reset), and the **Reef Command** dashboard (`reef-command`).

**Every one keys on `entity_id`, not `device_id`** — verified 2026-09-18. That is what makes
a board swap survivable; see §11.

#### `automation.reef_tank_af4_scheduled_feed` — read from HA 2026-09-02

Materially more than "presses a button", which is all this document used to say. Triggers
on **six** `input_datetime` helpers so times stay dashboard-editable, each slot gated by
`input_number.reef_af4_feeds_per_day` — slot N is inert while the count is below N — then,
behind the master kill switch:

1. **Two interlocks before pressing.** `binary_sensor.af4_feeder_feed_lockout` must be
   `off`, and `binary_sensor.reef_tank_sump_return_pump_..._running` must be `on`. The
   second is the one this document never knew about: the feeder discharges into the sump,
   so with no return pump the food never reaches the display. It reads `off` while the
   system is unplumbed and self-clears when the return comes up.
2. **Press, then wait up to 15 s for the lockout to go `on`.** On-device the lockout is
   `do_feed.is_running() || boot_recovery.is_running()`, and the press only happens while
   it is `off` — so **the lockout turning on is proof the pulse started**. That is as close
   to feed confirmation as an input-only port allows.
3. **The counter increments only on a confirmed pulse.** An unacknowledged press notifies
   and is deliberately *not* counted, so a press lost in transit cannot log a phantom feed
   and blind the watchdog below. This is load-bearing and must survive any rewrite.
4. **Both failure paths notify**, naming which interlock failed.

#### `automation.reef_tank_feeder_health_watchdog` — read from HA 2026-09-02

The backstop for silent failure, in three branches:

- **23:45 daily check.** Compares each feeder's counter against how many of its feed times
  have actually elapsed today, computed from the `input_datetime` helpers rather than
  hardcoded — so moving a feed time cannot false-alarm. 23:45 is late enough that any
  plausible feed time has passed and early enough to beat the midnight counter reset.
- **aF4 board offline 15+ minutes** while the schedule is enabled. Gated on the toggle, so
  bench and case work with the schedule off stays quiet.
- **Plank plug Z-Wave node dead** 15+ minutes.

Three deliberate choices worth preserving:

1. **Feed counting lives in HA, not on-device** — it survives ESP32 reboots and reuses the
   existing nightly reset automation.
2. **The lockout condition does double duty.** `off` means the device is reachable *and*
   outside its lockout, so an offline ESP32 skips the feed rather than firing a button
   press into the void. Offline reads `unavailable`, which fails the check correctly.
3. **The counter counts confirmed pulses, not presses.** See point 3 above.

Networking: IP 192.168.1.55 reserved in OPNsense dnsmasq against Ethernet MAC
`00:70:07:7F:48:C3` (host override `af4-feeder`, MAC match only, no client identifier). The
board pulled a new DHCP lease after flashing, which broke HA's cached discovery with
`Errno 113`; the reservation is the fix.

**No feedback channel exists, and this is now the only unmonitored failure direction.**
The 0-10 V port is input-only, so everything above confirms that *the pulse was sent* and
nothing confirms *that food came out*. The gap that matters is an over-temperature fault:
per inD's own documentation it stops the feeder and **never self-clears**, and it is
invisible to us — the ESP32 would pulse happily, the lockout would assert, the counter
would increment, and the 23:45 watchdog would stay silent while the tank went unfed.

A power-monitoring smart plug on the 12 V supply is the only way to close it without
opening the unit: feed-motor current is the sole dispense evidence available. Open item 20.

---

## 6. Enclosure

**External 65.2 × 117.0 × 39.9 mm**, PETG, printed with no supports. (38.4 mm until the
1.5 mm hat lift of 2026-09-16, §6.3.)
`hardware/enclosure/af4_enclosure_ocp.py` is the parametric source and runs dimensional checks plus
solid-interference tests before exporting. Since 2026-09-16 the scalar checks pass at the lifted
height; ⚠️ the solid tests and exports have **not** been re-run (§6.3, item 27).

### 6.1 The vertical stack — the governing dimension

```
  z = -11.90   case floor, outside
  z =  -9.50   case floor, inside
  z =   0.00   top of the three ESP32 standoffs = ESP32 bottom face
  z =   1.58   ESP32 top face
  z =   4.12   top of the male header plastic on EXT1/EXT2
  z =   5.62   socket bottoms — float 1.50 mm above the plastic (HAT_LIFT)
  z =   9.96   male pin tips → ~4.3 mm into the sockets
  z =  11.20   top of UEXT1 box header   [MEAS]  → 2.92 mm clear
  z =  11.50   top of DCDC1 power module  [MEAS]  → 2.62 mm clear
  z =  13.40   top of the electrolytic cap beside DCDC1  [MEAS]  ← tallest thing under the hat
  z =  14.12   hat underside                       → 0.72 mm clear of the cap
  z =  15.72   hat top face
  z =  18.22   3.5 mm jack axis
  z =  19.32   barrel jack axis
  z =  22.92   barrel jack crown            → 2.08 mm clear of the lid
  z =  25.00   lid underside
```

**Revised 2026-09-16 — see §6.3.** The table this replaced put the UEXT box header at 5.98 and
called it the tallest thing under the hat. Calipers put it at 11.20, and put an electrolytic
cap at 13.40 — **0.78 mm into the hat as then designed.** The hat now sits 1.50 mm higher.

**The socket body height plus `HAT_LIFT` sets everything.** Substitute a different socket →
change `HAT_Z` and re-run; the script reports what now collides. The three `[MEAS]` rows are
`TALL_PARTS` in the script and are the check that matters.

⚠️ **This table is also the proof that J3/J4 mount from the BOTTOM face.** The 10.00 mm
between the header plastic (4.12) and the hat underside (14.12) is the 8.50 mm socket body
plus the 1.50 mm lift. Nothing in the stack sits between 14.12 and 15.72 except the board
itself. Build the sockets on top and the hat cannot reach the pins at all. See §A3.
(Before 2026-09-16 the same argument read 8.50 mm between 4.12 and 12.62.)

### 6.2 Two details that are easy to lose

- The barrel-jack hole needs its **Ø13 × 1.8 mm counterbore on the outside**, thinning the
  wall to 1.2 mm locally. Without it, 3 mm of wall eats most of the jack's 9.5 mm insertion
  depth. As built the plug engages 6.9 mm.
- The **four Ø3.5 mm LED sight holes** in the lid, each fitted with a 3 mm clear acrylic
  **light pipe**, sit over D3 and D5 on the hat and PWR1 and LNK1 on the Olimex board. This
  is the entire reason LED brightness is a real requirement rather than a cosmetic
  preference (§2.6). The pipes exist because the Olimex LEDs are 21.2 mm below the lid — a
  plain hole gives them a 4.7° viewing half-angle, visible only dead-on. ACT1 and CHRG1
  deliberately have no hole: ACT1 sits 0.361 mm inside the hat footprint and is blindfolded
  by opaque FR4. Full spec in `docs/aF4-enclosure-notes.md`; cutting and fitting in
  `docs/aF4-assembly-guide.md` §1.

Hat mounting holes at (123.0, −118.0) and (123.5, −147.0) are **forced by geometry** — the
only X clearing the ESP32's right edge below (118.15) and the parts column above (from
126.45). Not free choices.

### 6.3 The hat collided with an Olimex capacitor — raised 1.5 mm `[MEAS] 2026-09-16`

**Found 2026-09-16 while dry-fitting headers to a spare ESP32-POE-ISO**, before any rev E
board had arrived. Kenny could force the header plastic in beside DCDC1 but was worried about
the hat's clearance in that corner. The worry was well founded.

**What the design had assumed.** `hardware/enclosure/af4_enclosure_ocp.py` read *"UEXT box hdr
4.40 mm tall (vendor 3D model) — clears the hat easily"*, and §6.1 put the box header's top at
z 5.98 as the tallest thing under the hat. Both checks that could have caught a tall part were
built on that number: the scalar clearance used `1.578 + 4.40`, and the "case vs ESP32" solid
test capped the ESP32's envelope at the same height. **Nothing taller than 5.98 on the Olimex
board was ever tested against the hat.** The vendor mesh was never the problem: parsed on
2026-09-16, it puts UEXT1 at 11.53, DCDC1 at 11.99 and the cap at 13.15.

**Measured, calipers, from the ESP32's bottom face** (= z 0 in the stack, the plane the M2
standoffs stop at). A 5.0 mm reading across the board plus the WROVER can matched the model's
1.58 + ~3.3, which validates the reference face.

| Part | Measured top z | Vendor model | Clearance to hat underside at 12.62 (as designed) | At 14.12 (as fixed) |
|---|---|---|---|---|
| Electrolytic cap beside DCDC1 | **13.4** | 13.15 | **−0.78 — collision** | +0.72 |
| DCDC1 isolated power module | 11.5 | 11.99 | +1.12 | +2.62 |
| UEXT1 box header | 11.2 | 11.53 | +1.42 | +2.92 |

About 5 mm of the cap's diameter sits inside the hat outline (enclosure x 111.5–118.5,
y −161.5 to −155.0, hat edge at −160.0).

**Decision: raise the hat 1.50 mm** (`HAT_LIFT`). `HAT_Z` 12.618 → 14.118 and `IZ1` (lid
underside) 23.50 → 25.00; the standoffs, jack holes, lid bosses and light-pipe lengths all
follow. External height 38.4 → 39.9 mm. The sockets now float 1.5 mm above the header plastic;
the hat is carried by its two M3 standoffs, so nothing bears on that gap. Cost: pin
engagement ~5.8 → **~4.3 mm** (pin tip 9.96, socket bottom 5.62). 1.0 mm was rejected: it
leaves the cap 0.22 mm, inside the tolerance of a leaded cap sitting slightly crooked.
Rejected alternative: swap the cap for a Ø6.3 × 7.7 low-profile part — keeps the case but is
rework on the Olimex board.

⚠️ **Consequence for assembly:** the hat must never be pressed fully home on the headers with
the ESP32 out of the case. Without the standoffs it bottoms on the header plastic at the old
height and lands on the cap. `docs/aF4-assembly-guide.md` §5 says so.

**What changed in the script.** `TALL_PARTS` carries the three measured heights with their
footprints; each gets a ≥ 0.5 mm scalar clearance check, the hat's board slab gets a solid
intersection test against the parts grown 0.5 mm, a pin-engagement check (≥ 3.5 mm) was
added, and the "case vs ESP32" envelope now rises to the tallest measured part. Light pipes:
PoE pair 22.7 → **24.2 mm**, hat pair unchanged at 10.1 mm. `af4_hat_dummy_ocp.py` carries the
same lift.

**Two things this finding does not settle:**

- **The printed case in hand is the 38.4 mm version and must be reprinted.** The exports were
  regenerated on Kenny's Mac later the same day (below). **The lid does not change:** every lid
  feature is positioned relative to `IZ1`, so the origin-translated print file is the same part
  at either height. Confirmed on the regenerated file: same 5,448 triangles, same bounding box,
  every vertex within 0.0023 mm of the old export. → item 27
- **DCDC1 sits ~0.65 mm past the pin-10 end of EXT2 in the vendor model, but the real header
  plastic had to be forced in there.** The hat's J4 socket body is the same length and meets
  the same face. Shave the last half-segment of header plastic rather than force it, and
  dry-fit the hat before soldering. Not asserted by the script, because the model disagrees
  with the part in hand.

**Rejected on the way: mounting the ESP32 bottom side up** so standard Olimex headers point
at the hat. Olimex puts EXT1/EXT2 on `B.Cu`, and flipping the board mirrors the pinout. The
hat's two live pins are EXT1 pin 3 (GND — the only ground on either row) and EXT2 pin 6
(GPIO32); across every flip-and-rotate combination they land on EXT2-3 / EXT1-6,
EXT1-8 / EXT2-5, or EXT2-8 / EXT1-5. **No orientation puts hat ground on a ground pin.** Pin
assignments read from Olimex's `ESP32-PoE-ISO_Rev_N.kicad_pcb` on GitHub.

**A numpy-only verifier was added the same day: `hardware/enclosure/verify_enclosure.py`.** The
OCP script can only agree with itself and cannot run in a session; the verifier reads the STL
files that actually get printed and needs nothing but numpy, so it runs on the Mac, in the
Mac-side session VM (~4 s) and in the cloud container. It checks both bounding boxes, every
standoff top by ray cast, the hat envelope and the ESP32 envelope (up to the tallest measured
part) for case material by ray-parity point-in-mesh — behind a positive control that must find
the floor and walls solid — both jack holes open along their axes, and the hat slab against
`TALL_PARTS` and against the vendor ESP32 mesh sampled across every triangle. **Run against the
committed exports on 2026-09-16:**

- with the **pre-lift** parameters (`git show HEAD~1:…`) every mesh check passes — the exports
  are exactly the 12.618 / 23.50 design, which validates the verifier — and **the vendor-mesh
  check fails, tallest point 13.15 against a hat underside of 12.62.** That is this collision,
  found from the vendor model alone: a check against the part's own model would have caught it
  on 2026-08-27.
- with the **current** parameters it fails five checks — case height 35.40 vs 36.90, both hat
  standoffs at 12.618 vs 14.118, both jack holes blocked on their new axes. **That is the
  acceptance test for item 27: regenerate, then `python3 verify_enclosure.py` must print
  `ALL CHECKS PASSED`.**

Environment rule, per script (from Kenny's 3D-model workflow in another project, which holds
here too): **`af4_enclosure_ocp.py` and `af4_hat_dummy_ocp.py` need `cadquery-ocp` and run only
on Kenny's Mac; `verify_enclosure.py` needs numpy only and runs anywhere.** PyPI is 403-blocked
from both session shells, so "install it and retry" is never the fix in a session.

**Regenerated and verified on Kenny's Mac, 2026-09-16** (`~/.venvs/cad`, Python 3.14,
`cadquery-ocp` 8.0.1). `af4_enclosure_ocp.py`: all geometry checks pass and all six solid tests
read 0.000 mm³, including the new hat-slab-vs-tall-parts test; external 65.2 × 117.0 × 39.9 mm.
`af4_hat_dummy_ocp.py`: all checks pass. `verify_enclosure.py`: **ALL CHECKS PASSED** on the new
exports, re-run independently from the Mac-side session VM. Two things had to be fixed first:

- **OCP 8 broke both scripts.** Static methods lost their `_s` suffix (`TopoDS.Edge_s` →
  `TopoDS.Edge`), `Bnd_Box.Get()` returns an unbound `Limits` struct, and
  `NCollection_Utf8String` became `NCollection_String`. Both scripts now resolve these through a
  small compatibility block (`_static`, `_bbox6`, `_stl_binary`) and run on OCP 7 or 8. → §9.1
- **The dummy script carried its own hand-typed lid height,** `23.50 - (HAT_TOP + J1_H)`, and
  failed at 0.58 mm the moment the enclosure moved — the same class of error as the one this
  section records, one file over. It now reads `IZ1` and `HAT_LIFT` from
  `af4_enclosure_ocp.py` and fails if its own `HAT_LIFT` disagrees. It also looks for a macOS
  font; the committed dummy export has no embossed label, which is cosmetic.

> **Generalised lesson:** a clearance check is only as good as the number it is checked
> against. This one tested the hat against a hand-typed height instead of the vendor mesh
> that was already in `reference/vendor/`, so it passed for three weeks while wrong by 7 mm.
> **Check against the part, or the part's own model — never against a transcribed dimension.**

### 6.4 Lid label turned to read portrait `2026-09-16`

The first printed lid read along the long axis — upright only with the box landscape and the
cable end on the left. Kenny wants it upright with the box **portrait, RJ45 end at the top and
the two jacks on the left**, per a mockup. In the enclosure frame, looking down on the lid, that
is text reading along −X with its top toward −Y: `LID_LABEL_ROT = 180` (the old layout was the
equivalent of 90). Same size, depth and centre; the block now runs across the lid, and the script
asserts its clearance to the lid edge (9.8 mm), the boss counterbores (11.6) and the sight holes
(22.0). **The lid now needs reprinting as well as the case.** Reprinted with the case 2026-09-17. → item 27

`verify_enclosure.py` gained check 6, which exists because a rotation is the kind of change
nobody can verify by reading numbers: it rasterises the engraving out of the exported lid STL at
0.4 mm and scores it against all eight rotations and mirrors of the intended text. On the
existing lid export it reports **rot 90, IoU 0.72**, and 0.04 for the intended 180, which is
the photographed part — so it tells a correct export from a wrong one, including a mirrored one.
**Re-exported on the Mac the same day:** all checks pass, and check 6 reads the new lid as rot 180,
IoU 0.72.

---

## 7. Errors already found and fixed

Listed so an auditor does not spend effort re-discovering them, and because the pattern is
more useful than the individual items.

| Date | Error | Root cause |
|---|---|---|
| 2026-08-28 | **F1 `1206L010/60YR` did not exist** → `/60WR`. Trip current also wrong (0.30 → 0.25 A) | MPN generated from the naming convention (the 1206L suffix is a reel-quantity code) instead of looked up |
| 2026-08-28 | **C1 `GRM31CR71H106KA12L` did not exist** → `GRM31CR61H106KA12L`. X7R → X5R | Same. Murata makes no 10 µF 50 V X7R in 1206 |
| 2026-08-28 | **D5 `APT2012SYC` did not exist** → `APT2012SYCK` | Same |
| 2026-08-28 | **D3 under-driven ~10×** — R6/R7 shared 10 kΩ, putting the green at ~0.5 mcd | Resistor value chosen as a jellybean without checking it against the LEDs' intensity specs |
| 2026-08-28 | Docs claimed **"20 SMD placements"**; actual is 17 | A hard-coded count in a generated document, fixed in the script earlier but left standing in the prose |
| 2026-08-28 | Load and dissipation figures (~15 mA, 17 mW) predated the D3 branch | Derived numbers not revisited after a change to their inputs |
| 2026-08-28 | Claimed a lens mismatch between D3 and D5 | Asserted from naming convention; both are in fact water clear |
| 2026-08-28 `[AUDIT]` | **U1 on a 1.27 mm-pitch footprint; the AQY212GS is 2.54 mm** — board unbuildable | A KiCad footprint picked by name. Its description points at an OPTEK OPIA403 |
| 2026-08-28 `[AUDIT]` | `pcb/gen_pcb.py` said `SMAJ15A` for D2 while everything else said `SMAJ13A` | A value edited in one place and never propagated |
| 2026-08-28 `[AUDIT]` | **"44 joints" was fiction; the real count is 28** — and PCBWay prices hand-soldered joints | A hard-coded count in a generated document, with the correct itemisation printed directly beneath it |
| 2026-08-28 `[AUDIT]` | Circuit diagram showed D2 upstream of D1; the board wires it downstream | Diagram drawn from intent, not from the netlist |
| 2026-08-28 `[AUDIT]` | "Dropout is far smaller at 20 mA" — false for a quasi-LDO | A PMOS-LDO intuition applied to an NPN pass device |
| 2026-09-11 `[EQ]` | **J3/J4 built on the top face; they mount from the bottom** — found in PCBWay's assembly sample photos, boards in rework (§A3) | The mounting side of a THT part is not expressible in Gerbers, absent from an SMD-only centroid, and so survived only in prose — where `PCBWay-README.txt` then contradicted it with "sides populated: top only" |
| earlier | KiCad footprints specified 0.40 / 0.60 mm plated slots, below fab minimum | DRC does not check slot widths |
| earlier | Rev B: three buck modules failed in sequence | A trimpot existed only to hit a precision target the port does not require |

**The dominant failure mode in this project is a plausible value asserted rather than
checked** — a part number that parses correctly under its manufacturer's scheme, a resistor
value that looks like a jellybean, a count copied from an earlier revision, **a footprint
chosen because its name contained the right characters**. Every one was well-formed and
wrong.

`[AUDIT]` The first version of this document was written to expose exactly that pattern and
still shipped four fresh instances of it, including a build blocker. The lesson is not
"tag your claims" — it is that **naming a thing is not verifying it**, and the tags are only
worth what the checking behind them was worth. Where this document now says `[DS]`, a
datasheet was actually opened.

### 7.1 The inverse failure mode, named 2026-09-02

Once the design stopped moving, the dominant error flipped direction. **The docs now lag
execution rather than overstating it**, and a review that reads only the repo will invent
work that is already done. Three instances surfaced in a single day:

| What the repo said | What was true |
|---|---|
| "Missed-feed alert in HA" was the last unattended-safety gap (item 17) | `automation.reef_tank_feeder_health_watchdog` had been running it since 2026-08-27 |
| `automation.reef_tank_af4_scheduled_feed` "presses the button at each feed time" | It also holds a return-pump interlock, a 15 s pulse confirmation, and a confirmation-gated counter — all load-bearing |
| Firmware "has never been flashed", device "still on GPIO13" (item 11) | Flashed 2026-09-01 18:54, three minutes after the commit that wrote it |

All three were caught by reading the live system — Home Assistant's config and the device's
own reported build timestamp — rather than the documents describing it. **Check reality
before opening an item, and record work at the moment it is done, not at the moment someone
next reads the file.** The provenance tags do not help here: an `[ASSERT]` that has quietly
become true looks identical to one that has not.

---

## 8. Open items

> 🚫 **This table is not current state.** It is the **numbering registry** — item 12 means
> the headers, item 16 means the OTA password, permanently — plus the dated record of what
> closed each item and why. **For what is actually still open, read `STATUS.md`.**
> When an item closes, record *how* it closed here; change the open/closed picture in
> `STATUS.md`. Never renumber a row.

Revised after the 2026-08-28 audit, the 2026-08-31 pre-fabrication review, the 2026-09-01
bench and vendor-documentation passes, the 2026-09-02 order going to fabrication, the
2026-09-02 read of the live Home Assistant config, the 2026-09-11 assembly-sample EQ, the
2026-09-12 acceptance of the reworked board, the 2026-09-14 shipment, and the 2026-09-16
clearance measurement.

⚠️ Item 17 is a caution about this table itself: it was opened by the 2026-09-02 review and
closed the same day on discovering the work had existed in Home Assistant since 08-27 and
had simply never been written back here. **A ledger built by reading the repo will invent
open items as readily as it misses closed ones.** Check reality before adding a row.

| # | Item | Blocking? |
|---|---|---|
| 1 | ~~U1 footprint~~ — **CLOSED 2026-08-28.** Rebuilt from Panasonic's recommended mounting pad, regenerated and re-verified (§A1); independently re-checked 2026-08-31 | — |
| 2 | ~~Tell PCBWay to hold~~ — **CLOSED.** The rev D quotation was deleted at the vendor; rev E went in as a fresh inquiry 2026-08-31 with the corrected files and the 28-joint count | — |
| 3 | ~~`on_boot` lockout~~ — **CLOSED 2026-09-01.** Flash-persisted `feed_in_flight` + `script.boot_recovery`, 300 s (§5) | — |
| 4 | ~~Verify AQY212 operate current~~ — **CLOSED.** 1.1 mA typ / 3 mA max, turn-off 0.3 mA min. The GPIO32 move was mandatory, not optional | — |
| 5 | ~~Measure the 12 V supply's open-circuit voltage~~ — **CLOSED `[MEAS] 2026-09-01`: 12.13 V**, stable, comfortably under the 13 V standoff. Loaded it sits at 11.84–11.86 V and dips to 11.77 V | — |
| 6 | ~~Widen the 300 s feed cycle~~ — **CLOSED 2026-09-01.** 20 s + 290 s = 310 s; the tail was kept rather than trimmed, which buys the margin for free | — |
| 7 | ~~Widen commissioning check 6.3~~ — **CLOSED 2026-09-01.** 6.3 is now 10.0–10.9 V and 6.2 is 11.4–12.0 V; A2 made this mandatory, not optional | — |
| 8 | ~~Measure the trigger port's input current~~ — **CLOSED `[MEAS] 2026-09-01`: ~11 kΩ, about 0.95 mA at 10.4 V.** Negligible against the 18.7 mA budget; the load-budget assumption was right | — |
| 9 | ~~`web_server: auth:`~~ — **CLOSED 2026-09-01**, and it created item 16 | — |
| 10 | ~~C1 substitute~~ — **CLOSED 2026-08-31.** LCSC holds ~123 k of `GRM31CR61H106KA12L`; pre-approved alternate `C3216X5R1H106K160AB` (TDK) is in the order notes. PCBWay quoted the correct MPN 2026-09-02 and did not substitute | — |
| 11 | ~~`firmware/af4-feeder.yaml` needs pasting into the ESPHome Device Builder + OTA~~ — **CLOSED 2026-09-01**, and this row was stale for a day before anyone noticed. The device reports its firmware as built 18:54:20 that evening, three minutes after the commit that wrote it. GPIO32, the 20 s pulse, the boot lockout and web auth have been live since | — |
| 12 | ~~Solder two 1×10 male headers into EXT1/EXT2, pins up~~ — ✅ **CLOSED 2026-09-18.** Both rows fitted, plastic on the top face. The hat drops onto them and rests on its two tall standoffs with both jack noses through the +X wall — the 1.5 mm socket-to-plastic gap that keeps the hat off the Olimex capacitor is present as designed (§6.3). → §12 | — |
| 13 | ~~Confirm the internal 24 h timer under external triggering~~ — **CLOSED `[VENDOR]`: the built-in schedule is completely overridden while the link port is connected.** The old assumption was backwards; this is what item 17 exists to cover | — |
| 14 | Resolve the LED viewing-angle conflict, 120° vs 160°/140° (§2.6) | No — cosmetic |
| 15 | ~~Commissioning steps 6.1–6.8 must all pass before the schedule toggle is enabled~~ — ✅ **CLOSED `[MEAS] 2026-09-18`.** All eight passed against the real feeder in one sitting: 6.2 = 11.4 V, 6.3 = 10.37 V, 6.4 = 0 V with D5 dark, 6.5 = 10.37 V held 20 s with a clean edge, 6.6 = 310.007 s then 310.013 s, 6.7 link solid, 6.8 the unit fed. Measured values and what each one settles are in §12.2 | — |
| 16 | ~~Rotate the OTA password~~ — ✅ **CLOSED 2026-09-18.** All three credentials are now rotated and verified live. `af4_api_key` and the web password went over OTA on 2026-09-02; `af4_ota_password` rotated at the serial flash of the **replacement** board (§11.4) and was then proven end to end by a successful Device Builder OTA install — the one credential OTA cannot change, verified by the path that needs it. The first attempt failed `authentication is invalid` because the chosen password contained YAML-significant characters, so the Mac and Device Builder secrets stores resolved to different strings; a punctuation-free `openssl rand -hex 24` value pasted into both fixed it. The old values remain in git history and are worthless by design | — |
| 17 | ~~Missed-feed alert in HA~~ — **ALREADY CLOSED, and this item should never have been opened.** `automation.reef_tank_feeder_health_watchdog` has done it since 2026-08-27: a 23:45 counter-vs-elapsed-feed-times backstop, plus a board-offline branch. The scheduled-feed automation independently notifies on skip and on unacknowledged press. Read from HA 2026-09-02; the work existed and was simply never written back to this repo | — |
| 18 | **R5 runs at 77 % of an 0805's 125 mW rating.** A 0.25 W part is a drop-in; raising the divider impedance is NOT available, it is the minimum-load ballast. **Window has now closed for this run** — boards are in fabrication | No — note for a future rev |
| 19 | Silkscreen on the fabbed rev E boards reads **"10.4V 10s pulse"**. Corrected in `pcb/gen_pcb.py` for any future rev; the five boards in fabrication will carry the old string | No — cosmetic, and unfixable now |
| 20 | **No dispense confirmation.** Everything in §5 confirms the pulse was *sent*; nothing confirms food came out. An over-temperature fault would be invisible and never self-clears. A power-monitoring smart plug on the 12 V supply is the only fix short of opening the unit | No — the last unmonitored failure direction |
| 21 | ~~Read the recalculated ship date off the PCBWay order page~~ — **CLOSED 2026-09-14, overtaken rather than answered.** The page never published a recalculated date: the "Estimated Finish Time" reminder still read 2026-09-29 on the day the order shipped, because that field is not maintained. The boards shipped 2026-09-14, 12 days after the order was placed against a 26–28 day quote (§A3.2). Added to the registry 2026-09-05; it had been carried only in the handoff, which numbered it 20 — a number already spent on dispense confirmation | — |
| 22 | `pcb/gen_pcb.py` stray "exclude from BOM/pos" flags on J2. Added to the registry 2026-09-05; the handoff numbered it 9, a number already spent on the closed `web_server: auth:` item | No |
| 23 | ~~J3/J4 built on the wrong face~~ — **CLOSED 2026-09-12.** Rework requested 2026-09-11 (§A3), reply sent 08:17 the same day, one reworked board photographed and verified 2026-09-12: bodies on the bottom face, joints on top, pin 1 unchanged, both seated flush and square (§A3.1). Two workmanship defects were left open deliberately and rolled into item 26 rather than reworked again | — |
| 24 | **Move the J3/J4 footprints to `B.Cu`** (silkscreen to `B.SilkS`) in `pcb/gen_pcb.py`, rewrite the `PCBWay-README.txt` ASSEMBLY line to name the face by designator, and add the THT parts to the centroid with a side column. The fix for the *cause* of item 23, as opposed to this run's rework | No — but it is the only thing that stops item 23 recurring |
| 25 | ~~D3/D5 LED polarity unverified~~ — ✅ **CLOSED 2026-09-18 on the build board.** Resolved exactly where it was routed: **D3 lit at 6.1 and D5 lit at 6.5.** Both indicators are the right way round. Referred to PCBWay 2026-09-11 and explicitly released 2026-09-12 so it could not hold the EQ open — the right call, since commissioning answered it for nothing. ⚠️ Verified on the **built board only**; the other four are untested and the question would return with them | — |
| 26 | **Inspect all five boards on arrival and select the best one to build** — do not assume board 1, and **check the J3/J4 mounting face on every board**: only the reworked sample was ever photographed (§A3.2). Two known defects on every board, accepted rather than reworked (§A3.1): pin 10 of each socket row carries excess solder with burnt flux, and the bottom face has uncleaned flux residue at that end. Reflow the two joints, clean with IPA, and check the ten J3 joints that the photograph could not grade. Do this **before** the item-12 header work, in the same bench session | No — but it gates a clean commissioning run |
| 28 | ✅ **CLOSED same day, 2026-09-18.** Nothing was ordered: Kenny already had six **DALQUIS DC-099** panel jacks, the same part rev C used, with 150 mm of 18 AWG pre-soldered leads. Calipered, the `PJ_*` block set, `PJ_DIMS_VERIFIED` flipped, both scripts re-run and the exports regenerated. The measurement also revealed a **flat on the barrel**, which replaced the printed anti-rotation scheme with a D-hole. Flange Ø and body Ø remain uncalipered upper bounds and gate nothing. → §A4 | — |
| 29 | **Reprint the CASE** from the exports regenerated 2026-09-18 — **the lid does not change**, its STL is byte-identical, so the 09-17 lid print still stands. The 09-17 case is retired: old J1 hole, no panel-jack hole. Print size unchanged at 65.2 × 117.0 × 39.9 mm. Then fit the DC-099 **flat up** and tighten its 14 mm nut **before the boards go in**, solder the pair to J1's pad tails on the hat underside (**red +12 V, black −**; GND tail to TP4 reads a dead short — confirm that way, never against TP1), and anchor the cable at the tie post → §A4. ✅ **CLOSED 2026-09-18.** Case printed; DC-099 fitted flat up in the D-hole with its 14 mm nut tightened while the box was empty; the pair soldered to J1's pad tails and routed **inboard**, clear of the 0.50 mm edge. Polarity then confirmed by meter — black tail → TP4 a dead short, red → TP4 open (§12.1). Tie-post anchoring goes with the final close-up under item 27 | — |
| 27 | **Case and lid reprinted 2026-09-17** (Kenny) from the exports verified on the Mac 2026-09-16: the case for the 1.5 mm hat lift (§6.3), the lid for the portrait label (§6.4). **Still open:** cut the two PoE light pipes to 24.2 mm (hat pipes unchanged, 10.1), and move the hat up 1.5 mm in the Tinkercad model. The pre-lift case is retired — do not assemble into it. ✅ **CLOSED 2026-09-18** (recorded 09-19). Pipes cut and fitted — both lit through the lid — M3s in, 12 V cable anchored, lid on with all four screws, and the box wall-mounted above the sump on its printed bracket. Reported by Kenny and corroborated by the install photo; no dimension was re-measured here. The Tinkercad hat lift is cosmetic-model housekeeping and is not tracked further → §14 | — |
| 30 | **Erase the retired ESP32-POE-ISO.** `python -m esptool --port /dev/cu.usbserial-XXXX erase-flash`, then label it *"retired 2026-09-18 — was af4-feeder, base MAC `20:e7:c8:74:a6:d4`"* and bag it. Until it is erased it still carries the node name `af4-feeder`, a valid API encryption key and an OTA password, so powering it on the LAN puts a second board answering to the same name beside the real one — a genuine feed hazard, not a theoretical one. Safe to do now: the replacement is adopted and verified (§11), so no rollback is being destroyed. ✅ **CLOSED 2026-09-19.** Full-chip `erase-flash` on the bench over USB with the Ethernet lead out; identity confirmed by `read-mac` **before** the erase and the erase confirmed by reading five offsets back as `0xFF` **after** it. The board carries no credentials now. Labelling and bagging is physical and is Kenny's; it is housekeeping, not a hazard → §13 | — |
| 31 | **Confirm the aF4's internal 24 h schedule resumes once the link cable is removed.** Opened 2026-09-18. §1.4 establishes that the built-in schedule is *completely overridden while the port is connected* — but both inD guides describe only the connected state, and **neither says what happens on release.** This project already assumed the override direction backwards once, so the reverse direction is not to be assumed either. The check is free: pull the cable and read the feeder's own display for a next feed time. Consequence if it does not resume and nobody looks: the feeder is silently dark for as long as the case is on the bench | No — but it is the live-animal risk while the enclosure is away |

### 8.1 Commissioning gate (from `docs/aF4-assembly-guide.md` §6)

All voltages referenced to **TP4 (power ground)**, not the ESP32's ground.

| # | Check | Expect |
|---|---|---|
| 6.1 | Splitter tap into the **12 V panel jack** (not J1 — J1 is dead, §A4) | D3 green lit |
| 6.2 | TP1 (12 V) → TP4 | **11.4–12.0 V** (12 V less the Schottky drop) |
| 6.3 | TP2 (10.4 V) → TP4 | **10.0–10.9 V** — the check that matters |
| 6.4 | TP3 (tip) → TP4 at rest | 0 V, D5 dark |
| 6.5 | Press Feed on the ESPHome web page (login `af4`) | D5 lights, TP3 ≈ 10.4 V for **20 s**, returns to 0 V |
| 6.6 | Feed Lockout binary sensor | On with the pulse, clears **310 s** later |
| 6.7 | Plug the patch cable into J2 | aF4's **link LED goes solid** — the port sees the connection |
| 6.8 | Press Feed again | aF4's **link LED flashes green** — the pulse was accepted (newer units; SN 130063 qualifies) |

If 6.3 reads ~1.4 V, R4 and R5 are swapped. If it reads near 12 V, the divider is not
connected. Either way **stop — do not connect the feeder.**

✅ **Both bands widened 2026-09-01 on measured evidence, and this was mandatory rather than
cosmetic: as originally written, 6.2 and 6.3 would each have failed a perfectly good board.**
A2 measured the feeder's 12 V rail at 11.77 V under load, putting TP1 near 11.47 V, and a
low-tolerance divider legitimately regulates at 10.08 V against a stated floor of 10.3 V.
The two checks were also mutually inconsistent at their edges. **If 6.3 reads low, check 6.2
first** — a low-but-passing 6.2 means the LM1117 is simply in dropout and following its
input, where the output lands at ~10.5 V regardless of R4/R5, and the divider is innocent.

⚠️ If 6.5 does nothing, suspect the boot-recovery lockout before the hardware — and read the
*state*, not the log (§5).

---

## 9. Repository map

| File | Role |
|---|---|
| `aF4-MASTER-REFERENCE.md` | This document — consolidated, audit-oriented |
| `firmware/af4-feeder.yaml` | ESPHome config, **source of truth** |
| `docs/aF4-reference.md` | Feeder specs, measurements, regulator rationale |
| `docs/aF4-pcb-notes.md` | Board design decisions, part equivalence, PCBWay procedure |
| `docs/aF4-esp32-trigger-BOM.md` | Human-readable parts list with reasoning |
| `docs/aF4-assembly-guide.md` | Build sequence and commissioning |
| `docs/aF4-enclosure-notes.md` | Print and fit notes |
| `hardware/enclosure/af4_enclosure_ocp.py` | Parametric enclosure source, self-checking. Needs `cadquery-ocp` — Mac only |
| `hardware/enclosure/verify_enclosure.py` | Checks the exported case/lid STLs against the parameters, measured parts and vendor mesh. numpy only — runs anywhere (§6.3) |
| `pcb/gen_pcb.py` | **Source of truth for the board.** Edit this, not the `.kicad_pcb` |
| `pcb/post.py` | Fills copper pours, runs DRC |
| `pcb/make_package.py` | Generates BOM, centroid, fab notes, zip |
| `pcb/af4-trigger-hat-rev-E-GERBERS.zip` | **What was actually uploaded** to the PCB-fabrication line item |
| `pcb/af4-trigger-hat-rev-E-PCBWay.zip` | The all-in-one package. Byte-identical fab data, but **not** the file that was uploaded |
| `pcb/pcbway-order-YB1800644.md` | Order, quote, EQ and payment record |
| `tools/section_index.py` | Regenerates this document's section index; `--check` for staleness. Run by Claude Code hooks (§9.2) |
| `.claude/settings.json` | Claude Code project settings: no commit attribution, secrets unreadable, `git push` allowed and force pushes ask, section-index hooks (§9.2) |
| `aF4-protoboard-*.svg`, `archive/rev-c-protoboard/protoboard 20x20.stl` | **Rev C history — do not build from these** |

### 9.1 Toolchain constraints worth knowing

- ⚠️ *Superseded 2026-09-17 by §9.2 — `pcbnew` is available through KiCad 9's bundled Python.*
  **`pcbnew` is not installed on the Mac.** `pcb/make_package.py` cannot be re-run locally;
  artifact-only fixes must patch the generated file and repack the zip directly. The BOM half
  of the script needs no `pcbnew`, though — its `PARTS` list can be sliced out of the source
  and exec'd to regenerate the CSV, then cross-checked against the centroid.
- `kicad-cli` 7.x has **no `pcb drc` subcommand** (9.x does — §9.2); DRC runs through the `pcbnew` Python module.
- Zones must be filled with `ZONE_FILLER` before exporting Gerbers, or the pours come out empty.
- **The enclosure scripts need `cadquery-ocp`, which installs only on Kenny's Mac** (PyPI is
  403-blocked from both session shells). The Mac venv is Python 3.14, which pulls **OCP 8.0.1** —
  an API break from 7.x: no `_s` suffix on static methods, `Bnd_Box.Get()` unusable,
  `NCollection_Utf8String` → `NCollection_String`. Both scripts carry a compatibility block for
  it. `verify_enclosure.py` is numpy-only and runs in any shell (§6.3).

### 9.2 The toolchain under Claude Code on the Mac `[MEAS] 2026-09-17`

From 2026-09-17 sessions run in **Claude Code, natively on Kenny's Mac**, not in the Cowork
sandbox. Most of §9.1's "session shell" limits were properties of that sandbox, not of the
project. Each line below was checked on the Mac on 2026-09-17.

| Tool | Where | Checked |
|---|---|---|
| KiCad **9.0.7** | `/Applications/KiCad/KiCad.app` | `kicad-cli version` |
| `kicad-cli` | `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` — **not on `PATH`** | has `pcb drc`, `pcb export`, `pcb render` |
| `pcbnew` Python module | KiCad's bundled Python: `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3` (3.9) | `import pcbnew` → 9.0.7 |
| `cadquery-ocp` 8.0.1 + numpy 2.5.3, trimesh, matplotlib | venv `~/.venvs/cad` (Python 3.14) | `verify_enclosure.py` **ALL CHECKS PASSED**, label rot 180 IoU 0.72 |
| ESPHome **2026.8.2** | `/opt/homebrew/bin/esphome` | `esphome config firmware/af4-feeder.yaml` → *Configuration is valid* (one expected warning: GPIO12 strapping pin — the Olimex PHY power pin) |
| `gh` | `/opt/homebrew/bin/gh`, logged in as `kenbrinkman` | `gh auth status` |
| Home Assistant | MCP server attached to the Claude Code session | live state and automations readable (§5.7) |

**What this changes, and what it does not:**

- **`pcb/make_package.py` and `pcb/post.py` can probably run locally again**, under KiCad's
  bundled Python. **Not yet exercised.** (KiCad 9 *has* since read, DRC'd and re-exported the
  committed board without changing a pixel of fab output — §4.4. The generator scripts themselves
  are still unrun.) The committed board was produced by KiCad 7-era
  tooling; KiCad 9 may rewrite the file format, re-fill zones differently, or report new DRC
  classes. The first run must be **diffed against the committed `.kicad_pcb` and `drc.rpt`**
  before anything regenerated is trusted — and the rev E fab data is spent regardless (§4 of
  `.claude/CLAUDE.md`, lesson 6).
- **The enclosure scripts no longer need Kenny at the keyboard** — a session can run them in
  `~/.venvs/cad`. `verify_enclosure.py` needs numpy, which the Homebrew `python3` lacks: run
  it with `~/.venvs/cad/bin/python`.
- **`esphome config` prints the resolved configuration**, which may include secret values —
  whether this version redacts them was not checked. Send its stdout to `/dev/null` and read
  only the exit code and the status lines. Never pass `--show-secrets`.
- **Validation is not deployment.** The Device Builder copy and its own secrets store are still
  separate and still hand-synced (`.claude/CLAUDE.md` lesson 3). A local `esphome config` pass
  says nothing about what the Device Builder holds.
- **GitHub is reachable**, through git's `osxkeychain` helper and `gh`. Pushing first stayed
  with Kenny by choice; later on 2026-09-17 it moved to the session. `git push` and
  `git push origin main` are allowed, force and delete pushes ask (`docs/git-rules.md` §2).
- **PyPI reachability from the Mac was not tested**; nothing here needed it.

---

## 10. Audit status

This document was independently audited on 2026-08-28 (`archive/reviews/aF4-audit-2026-08-28.md`). The audit
re-derived all §2 arithmetic, re-verified all 20 MPNs against live listings, cloned the
Olimex Rev N source to check every `[CAD]` claim, and read the repo's own generated files.

**What held:** every arithmetic result in §2 (V_OUT 10.466 V, worst-case 10.080–10.875 V,
loads 18.6 / 19.95 mA, dissipation 22.1 mW, PhotoMOS drive 9.00 / 6.75 mA); every `[CAD]`
geometry claim; the firmware matching §5 exactly; all 20 part numbers; the drill file
carrying no slot under 0.70 mm; BOM ≡ PARTS ≡ board refs; centroid = 17 SMD; no vias in the
isolation band; every diode and regulator orientation checked pad-by-pad.

**What did not:** §A1 (U1 footprint), §A2 (SMAJ15A), the circuit diagram's topology, the
44-joint count, the dropout reasoning in §2.2, the unstated reboot gap in §5, and the
`[SPEC]`-tagged 12 V ceiling in §1 that was really an inference.

### 10.1 Still unverified after the audit

*(Items 1–3 were closed by the bench session and vendor-documentation pass of
2026-09-01. Struck through rather than deleted, so the audit's original scope stays
readable.)*

1. ~~Supply open-circuit voltage vs the 13 V standoff~~ — **CLOSED `[MEAS]`: 12.13 V.**
2. ~~Feeder trigger-port input impedance / current draw~~ — **CLOSED `[MEAS]`: ~11 kΩ,
   about 0.95 mA at 10.4 V. Negligible against the 18.7 mA quiescent budget and F1's
   0.10 A hold. The load-budget assumption was correct.**
3. ~~Feeder's internal 24 h timer behaviour under external triggering~~ — **CLOSED
   `[VENDOR]`: the schedule is completely overridden while the link port is connected.
   The previous assumption was backwards. See §1.**
4. ~~DRC and the enclosure's 13+3 checks — reported, not re-run~~ — **DRC CLOSED
   2026-08-31**: independently re-run on KiCad 7.0.11 with zones refilled, 61 items, counts
   identical, every class read rather than assumed cosmetic; the shipped Gerbers were also
   re-exported and diffed against the board. The **enclosure's own checks remain
   script-reported**, not independently re-run.
5. ~~Panasonic's recommended SOP4 land pattern~~ — **CLOSED 2026-08-31.** Two independent
   extractions of Panasonic's drawing put every footprint number on the printed
   callout list (0.4, 1.2, 0.8, 2.54 ±0.1) against a package run ending 6.8 ±0.4, and only
   the orientation actually used — 1.2 mm along the lead axis — keeps the toe on the pad
   across the whole span tolerance. **Kenny confirmed the axis assignment visually against
   the drawing on 2026-08-31.** That check is not re-derivable by tooling and must not be
   quietly re-opened.
6. LM1117 V_REF sub-bands — consistent with SNOS412 and every secondary source, but the
   exact table was not re-pulled from TI's PDF.
7. LED viewing angle, 120° vs 160°/140°.
8. **Murata's official EOL notice for C1** — corroborated only by the zero-stock pattern at
   three authorised distributors and Octopart's lifecycle data. Moot in practice: PCBWay
   quoted and sourced the correct MPN.
9. **Stock depth on 18 of the 20 BOM lines** — existence was verified for all 20, but only
   F1 and C1 had stock actually counted. Also moot now: all 20 are priced and on order.

### 10.2 Bench work still unrun (`docs/aF4-meter-test-battery.md`)

None of it blocks anything, and none of it can change the board any more.
**A4** V_loaded and **A5**'s powered current confirmation are two minutes each with the rig
already understood; **A6** (port decay time) would confirm R3 is harmless-but-redundant;
**B1** (hold-time sweep) is confirmatory only, since 20 s clears all three of inD's
published figures; **B2** is confounded by the 5-minute spacing rule; **B3** (held-high
yields exactly one feed) is the one with real information value, because the design's best
safety property currently rests on vendor documentation rather than on this unit.

---

## 11. The PoE board was replaced `[MEAS] 2026-09-18`

The Olimex ESP32-POE-ISO that had been flashed and on the network since July was swapped for
a duplicate board. Nothing was wrong with the old one; the new one is the board that goes into
the rev E enclosure. The swap cost one failed OTA, recorded below because the failure is the
useful part.

**Only three things ever knew which physical ESP32 this was.** The node name `af4-feeder`, the
API encryption key, the OTA password and all seven entity IDs live in the YAML and follow the
firmware, not the silicon. The three that do not:

1. Home Assistant's ESPHome config entry, whose unique_id is the board's MAC.
2. The OPNsense dnsmasq reservation, MAC → `192.168.1.55`.
3. The old board's own flash — same node name, same API key, same OTA password.

### 11.1 Every board has two MACs, three apart, and the two systems use different ones

This looked like a contradiction in the record and is not one.

| | Old board | New board |
|---|---|---|
| **Base MAC** — what ESPHome reports and HA stores | `20:e7:c8:74:a6:d4` | `00:70:07:7f:48:c0` |
| **Ethernet MAC** — what DHCP sees and OPNsense reserves against | `20:E7:C8:74:A6:D7` | `00:70:07:7F:48:C3` |

The ESP32 derives its interface MACs from one eFuse base address: WiFi STA = base, AP = base+1,
BT = base+2, **Ethernet = base+3**. ESPHome's `mac_address` is the base; the LAN8720 uses base+3.
So HA's device record and the DHCP reservation legitimately hold **different values for the same
board**, and every document in this project that names "the MAC" means the Ethernet one.

**Confirmed three ways, not assumed:** the +3 relationship was inferred from the old board's pair,
then *measured* from the new board's DHCP lease before the reservation was edited, then displayed
outright by the ESPHome Device Builder device panel, which lists `MAC Address` and `Ethernet MAC`
as separate fields. ⚠️ **Never compute the reservation MAC — read it from the lease.**

### 11.2 Home Assistant migrates the device; it does not need a delete and re-add

The planned procedure was: delete the ESPHome integration entry (to free the seven entity IDs),
re-add, re-paste the API key, re-set the area, then check nothing came back as `_2`. **That was
unnecessary.** HA raised a repair —

> **Device conflict for af4-feeder** — the device has reported a MAC address change from
> `20:e7:c8:74:a6:d4` to `00:70:07:7f:48:c0` … *Migrate configuration to new device* /
> *Remove or rename device*

**Take "Migrate configuration to new device."** It re-points the existing config entry's unique_id
at the new MAC and keeps everything hanging off it. Verified afterwards: same `device_id`
(`2508be2c…`), same config entry (`01KXV8NE…`), all **seven** entity IDs unchanged with no `_2`
suffix, recorder history intact, area still **Reef Tank Sump**, and the API key never re-entered.

"Remove or rename device" is the branch for two boards meant to coexist. It is not this case.

**Why the entity IDs mattered enough to plan around:** all four consumers key on `entity_id`, not
`device_id` (§5.7). A delete-then-re-add in the wrong order leaves the old registry rows holding
the names, the new entities land as `button.af4_feeder_feed_2`, and the scheduled feed, the
watchdog and the powerhead pause all break **silently**. The migrate path cannot produce that.

### 11.3 The OPNsense reservation is one line

Host entry uuid `259adfd7-8c24-4661-8ec0-65cff87d45a8` in `/conf/config.xml`, reachable as
`ssh vault` (192.168.1.1). Change `hwaddr` only — **edit the entry, never add a second**; two
entries claiming `.55` is the classic failure. Apply with `configctl dnsmasq restart`, which
regenerates `/usr/local/etc/dnsmasq.conf` (`dhcp-host=00:70:07:7f:48:c3,192.168.1.55,af4-feeder`)
and restarts the service. Back up `/conf/config.xml` first and diff afterwards — the change
should be exactly one line.

⚠️ **The lease is 86400 s.** A reservation change does not move a board that already holds a
pool address; it bites at the next renewal, twelve hours away. **Reboot the board.**

### 11.4 The OTA password rotation, and the character that broke it

Item 16 — rotating `af4_ota_password`, open since the 2026-09-02 credential incident — was closed
here, because **a serial flash is the only flash that can rotate it** (§4.3) and the board was on
the bench bare.

The first Device Builder install after the rotation failed: **`authentication is invalid`**. The
cause was not the procedure but the password itself — **it contained characters that YAML parses**,
so the Mac's `firmware/secrets.yaml` and the Device Builder's own `secrets.yaml` resolved to two
different strings while *looking* identical in both editors. The worst of these is `#`: unquoted,
` #` opens a comment and silently truncates the value.

**ESPHome imposes no password requirements at all** — `ota.password` validates as
`cv.sensitive()` → `cv.string`, any non-empty string, no length or character rules; an *empty*
value silently disables OTA authentication; and OTA v2 authenticates by SHA-256 challenge-response
over a nonce and cnonce, so the password is never transmitted. **Every real constraint is YAML
and copy-paste.** Use `openssl rand -hex 24` — punctuation-free hex cannot misparse — quote it
anyway, paste rather than retype it into the second store, and compare the two by hash before
spending a flash.

**Nothing is written to the board on a failed OTA auth**, which is why this is a cheap failure and
why it was worth provoking deliberately while the case was still open. Resolved by a clean hex
password in both stores, a serial re-flash, then a successful Device Builder install — config
hash `0xa8529b6a` → `0xd4f82693`, build `2026-09-18 18:07:52`.

### 11.5 The standing corrections

- 🚫 **Never compute the Ethernet MAC for a reservation.** Read it from the DHCP lease. → §11.1
- 🚫 **On a board swap, take HA's "Migrate configuration to new device."** Do not delete and
  re-add the ESPHome entry; the entity IDs are load-bearing and migration preserves them. → §11.2
- 🚫 **An OTA password must be punctuation-free.** Two YAML files that *look* the same can
  resolve differently. Compare by hash, not by eye. → §11.4
- ⚠️ **Prove an OTA path before the case closes.** The enclosure has no USB cutout, so after
  assembly OTA is the only way in and recovery is USB with the case open. The Device Builder
  install that closed item 16 doubles as that proof.
- **The Device Builder YAML was byte-identical to `firmware/af4-feeder.yaml`** at the time of the
  swap — 196 lines, zero diff. A "Modified" badge in the Device Builder means *the config it
  would build now differs from what it last built*, which a secrets edit alone is enough to cause.
  It is not evidence of YAML drift; check before assuming it is. → §4.3
- **The Mac can flash and build independently.** `esphome run firmware/af4-feeder.yaml --device
  /dev/cu.usbserial-XXXX` compiles from the source of truth with the repo's secrets; the esp-idf
  and xtensa toolchains are already cached in `~/.platformio`, so no long first build. The Olimex
  enumerates as a CH340 (`0x1a86:0x7523`). If it will not enter the bootloader: hold **BUT1**,
  tap **RST**, release **BUT1**. → §9.2

---

## 12. Commissioning passed, end to end `[MEAS] 2026-09-18`

The rev E hat was assembled into the reprinted case and every check in the commissioning gate
was run against the real feeder the same evening. **6.1 through 6.8 all pass.** This is the
first time the trigger circuit has been measured rather than argued, and the first time it has
driven an actual aF4.

**Assembly, as it stands.** Case printed from the 09-18 exports; DC-099 fitted flat up with its
14 mm nut tightened in the empty box; the 12 V pair soldered to J1's pad tails and routed
inboard; ESP32 on its three M2 standoffs; hat down onto both 1×10 headers and resting on its two
tall standoffs, with both jack noses through the +X wall. Items **12** and **29** are closed.
The lid is off, the light pipes are uncut (item 27), and the board is at 192.168.1.55 on PoE.

### 12.1 Polarity, settled by meter

The last unverified thing on the build. Power off, splitter tap unplugged, continuity mode:

- **black tail → TP4: dead short.** ✅
- **red tail → TP4: open.** ✅

**Red is +12 V, black is −, confirmed.** The photograph and Same Sky's PCB layout drawing had
both said so; this is the meter agreeing. The mirror test on red against TP1 was correctly not
attempted — F1 and D1 make a good board read a diode drop. → §A4

### 12.2 The numbers

| # | Check | Expected | Measured | |
|---|---|---|---|---|
| 6.1 | D3 with the panel jack fed | lit | **lit** | ✅ |
| 6.2 | TP1 → TP4 | 11.4–12.0 V | **11.4 V** | ✅ |
| 6.3 | TP2 → TP4 | 10.0–10.9 V | **10.37 V** | ✅ |
| 6.4 | TP3 → TP4 at rest | 0 V, D5 dark | **0 V, dark** | ✅ |
| 6.5 | Feed pressed (HA) | D5 lit, ~10.4 V, 20 s | **10.37 V solid, 20 s** | ✅ |
| 6.6 | Lockout on, clears 310 s | 310 s | **310.007 s / 310.013 s** | ✅ |
| 6.7 | Patch cable into J2 | link LED solid | **solid** | ✅ |
| 6.8 | Feed pressed again | link flashes, unit cycles | **fed** | ✅ |

**6.2 landed on its predicted value, not merely inside its band.** A2 measured the feeder's rail
at 11.77 V under load and §8.1 forecast TP1 "near 11.47 V"; 11.77 less the D1 Schottky drop is
11.4 V. ⚠️ **Under the original 11.6–12.2 V band this good board would have failed 6.2.** The
2026-09-01 widening was not cosmetic and this is the evidence — see §8.1.

**6.3 at 10.37 V is the OEM dongle's own measured open-circuit output to the hundredth** (§1.2).
Note what it also disproves: with 11.4 V in and 10.4 V wanted out the LM1117 has ~1.0 V of
headroom and was *expected* to be in dropout, which would have put the output near 10.5 V
regardless of R4/R5 and made 6.3 uninformative about the divider. It is not in dropout. It is
regulating, and **the R4/R5 divider is therefore confirmed by measurement**, not merely passed.

**6.4 is the first measurement of the GPIO32 decision.** 0 V at rest with D5 dark means no idle
or boot leakage through U1 at all. The pin move was justified on datasheet arithmetic — AQY212
guaranteed-off 0.3 mA against 0.72–0.85 mA of GPIO13 boot leakage — and had never been checked
on hardware. → §2.4

**6.5 adds two facts nothing had established.** TP3 under the pulse reads **10.37 V, identical
to TP2 at rest**: the AQY212GS drops essentially nothing into the feeder's high-impedance input,
so the ≥ 9 V window has ~1.4 V of margin in hand. And the falling edge is **clean, with no decay
tail** — which answers bench item **A6** incidentally: R3's bleed path is not needed to get a
sharp release, and remains harmless-but-redundant as suspected. → §10.2

**6.6 ran twice and the on-device timing does not drift:** 310.007 s and 310.013 s, 6 ms apart.

### 12.3 The reef system is plumbed and running

⚠️ **This invalidates the premise of a standing project fact.** `CLAUDE.md` lesson 9 reads "the
reef system is not plumbed; every reef power and flow sensor reads zero, and zero is correct."
As of tonight that is history. `sensor.utility_room_return_pump_electric_consumption_w` reads
**142.245 W** against the binary sensor's 10 W threshold, and Kenny confirmed directly: the
system is completely up and running.

**The lesson survives; only its example expired.** "Before calling a zero a fault, verify the
system is supposed to be non-zero" cost this project a 31-day write-up of a go-live blocker that
was a correct reading. Tonight is the same trap inverted — a *non*-zero where the record said
zero — and it was worth checking rather than assuming a sensor fault.

**Consequence for go-live:** `automation.reef_tank_af4_scheduled_feed` carries a hard interlock
requiring the return pump to be running, on the reasoning that the feeder dumps into the sump and
without return flow the food never reaches the display. **That interlock is now satisfied.**
Go-live is no longer gated on the plumbing — only on closing the case. The long-pole open item
is closed.

### 12.4 What a manual feed deliberately does not touch

`counter.reef_af4_feeds_today` stayed at **0** across both of tonight's feeds, and that is
correct. The counter is incremented only inside `automation.reef_tank_af4_scheduled_feed`, and
only *after* the board confirms the pulse by raising its lockout — an unconfirmed press must
never log a phantom feed and blind the health watchdog (§5.7). **A manual bench session
therefore leaves no trace in the counter.** Do not read that as a missing count later.

The same gating makes case work quiet: **both branches of
`automation.reef_tank_feeder_health_watchdog`** — the 15-minute board-offline alert and the
23:45 missed-feed backstop — **are conditioned on `input_boolean.reef_af4_schedule_enabled`
being `on`.** With the schedule off, the board can be off the network indefinitely without
notifying anyone.

### 12.5 The decision taken, and the one question it opens

The enclosure goes back to the bench to be finished — light pipes, M3s, tie-post anchoring, lid.
**The link cable is pulled meanwhile, to hand the feeder back its own internal schedule**, and
Kenny turns `input_boolean.reef_af4_schedule_enabled` on by hand once the case is closed. The
schedule stands at **2 feeds/day, 13:30 and 20:30**.

⚠️ **New open item 31: nothing establishes that the internal schedule resumes when the link
cable is removed.** Both inD guides state the built-in schedule is overridden *while the port is
connected* — Hydros words it as connection rather than signalling — but **neither describes the
release.** §1.4 already records that this project assumed the override direction backwards once.
Do not assume the reverse direction either: **confirm the feeder shows a next feed time on its
own display after the cable comes out.**

### 12.6 The standing corrections

- ✅ **The commissioning bands are validated by a passing board, not just by argument.** 6.2
  measured 11.4 V — the floor of its band. Anyone tempted to tighten either band should read
  §8.1 and this section first. → §8.1
- **A passing 6.3 only clears the divider if 6.2 is healthy.** Here it was in dropout territory
  by headroom yet regulating, which is what made 10.37 V informative. Check 6.2 before drawing
  any conclusion from 6.3.
- **A manual feed is invisible to `counter.reef_af4_feeds_today` by design.** → §12.4
- ⚠️ **Do not assume the aF4's internal schedule returns when the link cable is pulled.**
  Verify on the unit. → item 31
- **The reef system is plumbed as of 2026-09-18.** Reef sensors reading zero are now suspect
  rather than expected — the opposite of the rule that held until tonight. → §12.3

---

## 13. The retired board was erased `[MEAS] 2026-09-19`

Item 30, open since the swap (§11), is closed. The retired Olimex ESP32-POE-ISO — base MAC
`20:e7:c8:74:a6:d4`, Ethernet MAC `20:E7:C8:74:A6:D7` — was full-chip erased on the bench and is
now a stock board with no aF4 identity and no credentials on it.

**The hazard it removes** was never theoretical: until the erase, that board's flash held the node
name `af4-feeder`, a valid API encryption key and a valid OTA password. Powering it on the LAN
would have put a second device answering to the same name and the same credentials beside the one
that drives the feeder.

```
ESPTOOL=/opt/homebrew/Cellar/esphome/2026.8.2/libexec/bin/esptool
$ESPTOOL --port /dev/cu.usbserial-2110 read-mac      → 20:e7:c8:74:a6:d4   (the guard)
$ESPTOOL --port /dev/cu.usbserial-2110 erase-flash    → erased in 1.3 s
$ESPTOOL --port /dev/cu.usbserial-2110 read-flash <off> 0x100 …
   0x1000 bootloader · 0x8000 partition table · 0x9000 NVS · 0x10000 app · 0x1a0000 ota_1
   → all five all 0xFF                                (the proof)
```

**`esptool` needs no separate install** — it ships inside the Homebrew ESPHome venv at the path
above (v5.3.1 under ESPHome 2026.8.2). v5 spells its subcommands with hyphens. → §9.2

### 13.1 Erase, don't overwrite — and verify by read-back

Two things make this a chip erase rather than a re-flash:

- **`erase-flash` takes NVS; flashing new firmware does not.** ESPHome keeps its preferences in
  NVS, which on this board meant the API key material, the OTA password and the flash-persisted
  boot lockout (§5.2). A new app written over the top leaves all of that sitting in the partition
  behind it. Erase the chip, then flash.
- **"Erased successfully" is the tool reporting its own intent** (§A4: a check whose result is
  fixed by its own inputs is not a check). The state of the world that would make the verification
  fail is a region that still reads data — so read the regions back. Five offsets, all `0xFF`.

**Read the MAC before erasing, not after.** It is the only thing that distinguishes the two boards
once they are off the network, and it cannot be recovered from a board you have already wiped.
⚠️ `read-mac` drives DTR/RTS and **resets the board** — never point it at the commissioned one.

### 13.2 What survives, and what it means for reuse

The eFuse base MAC survives and cannot be changed. ESPHome burns no eFuses, so nothing else on the
chip is marked and the board is fully generic. If it is ever put back on PoE:

- **Give it a new identity**: a `name:` that is not `af4-feeder`, a fresh API encryption key, and a
  fresh OTA password from `openssl rand -hex 24` — punctuation-free, quoted anyway (§11.4).
- **Its Ethernet MAC is still `20:E7:C8:74:A6:D7`** (base+3, §11.1) and it needs its **own** DHCP
  reservation. 🚫 Do not touch OPNsense host entry `259adfd7-8c24-4661-8ec0-65cff87d45a8` — that
  one is `.55` and belongs to the live board. Read the new MAC off the lease rather than computing
  it, as always.
- **The nested `ethernet:` clock block**, never `clk_mode: GPIO17_OUT` (§4.3), and **GPIO13 still
  carries the factory 2.2 kΩ pull-up** (§2.4) — that is a property of the board, not of the old
  firmware, and it applies to whatever this one becomes next.

**No cleanup was needed anywhere else, and this was checked rather than assumed.** Home Assistant
holds exactly seven `af4_feeder` entities, no `_2` suffix, with the board online at `192.168.1.55`
— the migrate path (§11.2) re-pointed the config entry instead of leaving an orphan behind. The
OPNsense reservation was edited in place, so no second entry ever existed; and an erased board
issues no DHCP request, so any stale lease for `…A6:D7` expires unused.

### 13.3 The standing corrections

- 🚫 **Wiping an ESP32 means `erase-flash`, not a re-flash.** Credentials live in NVS, which a new
  app does not touch. → §13.1
- 🚫 **Do not accept the eraser's own success message as the verification.** Read the flash back at
  the bootloader, partition-table, NVS, app and OTA offsets. → §13.1
- ⚠️ **`read-mac` resets the board it is pointed at.** Identify a bench board with it; never a
  running one.
- **The eFuse MAC is permanent.** A wiped board is anonymous in firmware and still recognisable on
  the wire — plan reservations around that, do not try to change it. → §13.2

---

## 14. The case is closed, mounted, and the system is live `[MEAS] 2026-09-19`

The enclosure was finished and wall-mounted above the sump on **2026-09-18**, and
`input_boolean.reef_af4_schedule_enabled` was switched **on at 23:26** the same night. Item 27 is
closed. **This is go-live**: every gate from §8.1 through §12 has passed and the system is now
feeding on its own schedule rather than under supervision.

Verified against the live instance 2026-09-19:

| | |
|---|---|
| Board | `binary_sensor.af4_feeder_status` **on** since 2026-09-18 23:18, `192.168.1.55`, uninterrupted |
| Lockout | `binary_sensor.af4_feeder_feed_lockout` **off** — at rest, matching D5 dark in the photo |
| Schedule toggle | **on** since 2026-09-18 23:26 |
| `automation.reef_tank_af4_scheduled_feed` | **on**, `last_triggered: null` — it has never yet fired |
| `automation.reef_tank_feeder_health_watchdog` | **on**, queued mode |
| Feeds | 2/day, 13:30 and 20:30; `counter.reef_af4_feeds_today` **0** |

**The enclosure as installed:** lid on with all four screws, both PoE light pipes lit — amber and
green — through the lid, D3 lit and D5 dark on the hat, both jack noses through the wall with
their cables dressed downward, and the whole box on its printed wall bracket above the sump.
The 24.2 mm pipe length, the two M3s into the tall standoffs and the tie-post anchor are **Kenny's
report plus the photo**, not a measurement taken here.

⚠️ **Nothing has yet run unattended.** `last_triggered: null` on the scheduled feed is the plain
statement of it: every feed so far has been a button press with someone watching. **The first
fully automated feed is 13:30 on 2026-09-19**, and it passes when `counter.reef_af4_feeds_today`
reads 1 — the counter increments only after the board confirms the pulse by raising its lockout
(§12.4), so a stuck 0 is the signal.

### 14.1 The 23:45 "missed feed(s)" alert was correct, and cannot recur

Nineteen minutes after the toggle went on, the watchdog's daily backstop fired and pushed to both
phones:

> 🐟 **aF4 missed feed(s)** — Schedule is enabled but only 0 of 2 due aF4 feeds were confirmed
> today. Check the trigger board and lockout.

It also wrote an `error` row through `script.reef_log`. **Nothing is wrong.** The backstop
evaluates the whole day's due slots against the counter, and both 13:30 and 20:30 had already
passed while the schedule was still off — so at 23:45 the day genuinely held 0 of 2 confirmed
feeds. The trace confirms it took the alert branch on a true condition, not on an error.

The exposure is narrow and now spent: it can only happen on a day where the toggle is switched on
**after** a slot time. On any day that begins with the schedule on, a missed feed at 23:45 means a
missed feed. **Do not "fix" the backstop for this case** — widening it to ignore slots that
predate the toggle would also teach it to ignore a real outage that straddled a restart.

### 14.2 The standing corrections

- ⚠️ **The aF4's internal schedule is overridden again** — the link cable is back in. Item 31 is
  still unverified and its free window has closed; the fallback nobody has tested is the one that
  matters the next time this board is out of service for a day. → §12.5 · §1.4
- **Go-live is not commissioning.** §12 proved the hardware under supervision; the first
  *unattended* feed is 13:30 on 2026-09-19 and is the only thing that proves the scheduler.
- **A missed-feed alert dated to a day the toggle was flipped mid-day is expected.** → §14.1
- **The installed-enclosure details are reported, not measured here.** If a dimension ever matters
  again — pipe length, standoff engagement — measure the part, do not cite this section (§6.3).
